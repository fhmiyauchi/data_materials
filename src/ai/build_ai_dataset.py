import os
import pandas as pd
from sqlalchemy import create_engine
from pymatgen.core import Composition

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DATA_DIR, "materials.db")
TARGET_ELEMENTS = {"Li", "Fe", "Co", "Ni", "Mn", "Al", "Cu", "Na", "P", "Ti"}

# Crustal abundance (ppm)
ELEMENT_ABUNDANCE_PPM = {
    "Fe": 56_300,  "Al": 82_300, "Na": 23_600,
    "Mn": 950,     "Ti": 5_650,  "Cu": 60,
    "Ni": 84,      "Li": 20,     "Co": 25,
    "P":  1_050,   # default for unknowns is set to 10 in the logic
}

def contains_target_element(formula: str) -> bool:
    try:
        comp = Composition(formula)
        # Check if intersection of formula elements and target elements is not empty
        elements = {el.symbol for el in comp.elements}
        return bool(elements.intersection(TARGET_ELEMENTS))
    except Exception:
        return False

def calc_relative_cost_index(formula: str) -> float:
    try:
        comp = Composition(formula)
        total_inv_abundance = sum(
            amt / ELEMENT_ABUNDANCE_PPM.get(el.symbol, 10)
            for el, amt in comp.items()
        )
        return total_inv_abundance
    except Exception:
        return 1.0 # fallback

def build_feature_text(row) -> str:
    conductivity = "metal" if row.is_metal else f"{row.band_gap:.2f} eV band gap"
    stability = "thermodynamically stable" if row.energy_above_hull < 0.05 \
                else f"near-stable (hull: {row.energy_above_hull:.3f} eV/atom)"
    return (
        f"{row.formula} is a {row.crystal_system} material with a density of "
        f"{row.density:.2f} g/cm³, {conductivity}, and is {stability}. "
        f"It has a composite score of {row.composite_score:.2f} and "
        f"an element rarity index of {row.relative_cost_index:.3f}."
    )

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print("Connecting to database...")
    engine = create_engine(f"sqlite:///{DB_PATH}")

    query = """
    SELECT
        m.material_id,
        m.standard_formula as formula,
        c.density,
        c.band_gap,
        c.energy_above_hull,
        c.is_metal,
        c.crystal_system,
        c.formation_energy_per_atom,
        e.K_VRH,
        e.G_VRH,
        e.poisson_ratio,
        d.poly_total,
        d.pot_ferroelectric
    FROM materials m
    JOIN properties_core c ON m.material_id = c.material_id
    LEFT JOIN properties_elastic e ON m.material_id = e.material_id
    LEFT JOIN properties_dielectric d ON m.material_id = d.material_id
    WHERE
        c.band_gap IS NOT NULL
        AND c.density IS NOT NULL
        AND c.energy_above_hull < 0.2
    """
    
    print("Executing query...")
    df = pd.read_sql(query, engine)
    print(f"Extracted {len(df)} initial stable materials.")

    # 1. Filter by target battery-relevant elements
    print("Filtering for battery-relevant elements...")
    df = df[df["formula"].apply(contains_target_element)].copy()
    
    # Randomly sample to limit to ~3000 to keep MVP fast, if we have more
    if len(df) > 3000:
        df = df.sample(3000, random_state=42).copy()

    print(f"Curated {len(df)} materials for the AI layer.")

    # 2. Derive cost index
    print("Computing synthetic cost index...")
    df["raw_cost_index"] = df["formula"].apply(calc_relative_cost_index)
    # Normalize cost index to 0-1 range based on the curated subset
    max_cost = df["raw_cost_index"].max()
    df["relative_cost_index"] = df["raw_cost_index"] / max_cost

    # 3. Derive component scores
    print("Computing multi-objective component scores...")
    df["conductivity_score"] = df["band_gap"].apply(lambda bg: max(0, 1.0 - abs(bg - 1.5) / 17.89))
    df["stability_score"] = df["energy_above_hull"].apply(lambda hull: max(0, 1.0 - (hull / 9.71)))
    df["density_score"] = df["density"].apply(lambda d: max(0, 1.0 - (d / 26.58)))
    df["cost_score"] = df["relative_cost_index"].apply(lambda cost: max(0, 1.0 - cost))

    # 4. Derive composite score (equal weights for the static baseline)
    df["composite_score"] = (
        0.3 * df["conductivity_score"] +
        0.3 * df["stability_score"] +
        0.2 * df["density_score"] +
        0.2 * df["cost_score"]
    )

    # 5. Generate semantic feature text
    print("Generating semantic descriptions...")
    df["feature_text"] = df.apply(build_feature_text, axis=1)

    # Clean up intermediate columns if needed, or keep them for transparency
    df.drop(columns=["raw_cost_index"], inplace=True)

    # 6. Save back to SQLite
    print("Saving material_features to SQLite...")
    df.to_sql("material_features", con=engine, if_exists="replace", index=False)
    
    print("Feature engineering complete!")
    print("\nSample feature text:")
    print("-" * 50)
    print(df.iloc[0]["feature_text"])
    print("-" * 50)

if __name__ == "__main__":
    main()

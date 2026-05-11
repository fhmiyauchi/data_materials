import os
import json
from collections import Counter
import pandas as pd
from typing import Dict, Set
from sqlalchemy import create_engine  # type: ignore
from pymatgen.core import Composition


class DataTransformer:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        # Cache for formula standardizations to speed up processing
        self._formula_cache: Dict[str, str] = {}

    def standardize_formula(self, raw_formula: str) -> str:
        if pd.isna(raw_formula) or not str(raw_formula).strip():
            return "UNKNOWN"
        raw_formula_str = str(raw_formula)
        if raw_formula_str in self._formula_cache:
            return self._formula_cache[raw_formula_str]

        try:
            reduced = Composition(raw_formula_str).reduced_formula
            self._formula_cache[raw_formula_str] = reduced
            return reduced
        except Exception:
            self._formula_cache[raw_formula_str] = raw_formula_str
            return raw_formula_str

    def extract_formula_from_structure(self, struct_str: str) -> str:
        if pd.isna(struct_str):
            return "UNKNOWN"
        try:
            struct_dict = json.loads(struct_str)
            sites = struct_dict.get("sites", [])
            counter: Counter = Counter()
            for site in sites:
                species = site.get("species", [])
                for sp in species:
                    element = sp.get("element")
                    occu = sp.get("occu", 1)
                    if element:
                        counter[element] += occu

            if not counter:
                return "UNKNOWN"

            return Composition(counter).reduced_formula
        except Exception:
            return "UNKNOWN"

    def process_and_export(self, db_name: str = "materials.db") -> None:
        db_path = os.path.join(self.data_dir, db_name)
        if os.path.exists(db_path):
            os.remove(db_path)

        # sqlite requires a specific engine, type ignore for mypy
        engine = create_engine(f"sqlite:///{db_path}")  # type: ignore
        print(f"Initializing ETL pipeline to {db_path}...")

        formulas_set: Set[str] = set()

        # 1. Process Core Materials
        core_path = os.path.join(self.data_dir, "core_materials.csv")
        if os.path.exists(core_path):
            print("Processing core_materials...")
            df_core = pd.read_csv(core_path)
            df_core["standard_formula"] = df_core["formula"].apply(
                self.standardize_formula
            )
            formulas_set.update(df_core["standard_formula"].unique())

            # Materials table
            df_materials = df_core[["material_id", "standard_formula"]].copy()
            df_materials.to_sql(
                "materials", con=engine, if_exists="replace", index=False
            )

            # Properties Core
            core_cols = [
                "material_id",
                "density",
                "band_gap",
                "is_metal",
                "formation_energy_per_atom",
                "energy_above_hull",
                "volume",
                "theoretical",
                "crystal_system",
            ]
            existing_core_cols = [c for c in core_cols if c in df_core.columns]
            df_properties_core = df_core[existing_core_cols].copy()
            df_properties_core.to_sql(
                "properties_core", con=engine, if_exists="replace", index=False
            )

        # 2. Process Dielectric Constant
        dielec_path = os.path.join(self.data_dir, "dielectric_constant.csv")
        if os.path.exists(dielec_path):
            print("Processing dielectric_constant...")
            df_dielec = pd.read_csv(dielec_path)
            df_dielec.drop(
                columns=["structure", "poscar", "cif", "meta"],
                inplace=True,
                errors="ignore",
            )
            df_dielec.to_sql(
                "properties_dielectric", con=engine, if_exists="replace", index=False
            )

        # 3. Process Elastic Tensor
        elastic_path = os.path.join(self.data_dir, "elastic_tensor_2015.csv")
        if os.path.exists(elastic_path):
            print("Processing elastic_tensor_2015...")
            df_elastic = pd.read_csv(elastic_path)
            df_elastic.drop(
                columns=["structure", "poscar", "cif"], inplace=True, errors="ignore"
            )
            df_elastic.to_sql(
                "properties_elastic", con=engine, if_exists="replace", index=False
            )

        # 4. Process Battery Materials
        batt_path = os.path.join(self.data_dir, "battery_materials.csv")
        if os.path.exists(batt_path):
            print("Processing battery_materials...")
            df_batt = pd.read_csv(batt_path)
            df_batt["standard_formula"] = df_batt["composition"].apply(
                self.standardize_formula
            )
            formulas_set.update(df_batt["standard_formula"].unique())
            df_batt.to_sql(
                "experiments_battery",
                con=engine,
                if_exists="replace",
                index=True,
                index_label="id",
            )

        # 5. Process Steel Strength
        steel_path = os.path.join(self.data_dir, "steel_strength.csv")
        if os.path.exists(steel_path):
            print("Processing steel_strength...")
            df_steel = pd.read_csv(steel_path)
            df_steel["standard_formula"] = df_steel["formula"].apply(
                self.standardize_formula
            )
            formulas_set.update(df_steel["standard_formula"].unique())
            df_steel.to_sql(
                "experiments_steel",
                con=engine,
                if_exists="replace",
                index=True,
                index_label="id",
            )

        # 6. Process Matbench Phonons
        phonon_path = os.path.join(self.data_dir, "matbench_phonons.csv")
        if os.path.exists(phonon_path):
            print("Processing matbench_phonons...")
            df_phonon = pd.read_csv(phonon_path)
            df_phonon["standard_formula"] = df_phonon["structure"].apply(
                self.extract_formula_from_structure
            )
            formulas_set.update(df_phonon["standard_formula"].unique())
            df_phonon.to_sql(
                "structures_phonons",
                con=engine,
                if_exists="replace",
                index=True,
                index_label="id",
            )

        # 7. Process Matbench MP Gap
        gap_path = os.path.join(self.data_dir, "matbench_mp_gap.csv")
        if os.path.exists(gap_path):
            print("Processing matbench_mp_gap (Chunked)...")
            first_chunk = True
            for chunk in pd.read_csv(gap_path, chunksize=5000):
                chunk["standard_formula"] = chunk["structure"].apply(
                    self.extract_formula_from_structure
                )
                formulas_set.update(chunk["standard_formula"].unique())
                chunk.to_sql(
                    "structures_mp_gap",
                    con=engine,
                    if_exists="replace" if first_chunk else "append",
                    index=True,
                    index_label="id",
                )
                first_chunk = False

        # 8. Export Formulas Master Table
        print("Exporting formulas master table...")
        df_formulas = pd.DataFrame({"standard_formula": list(formulas_set)})
        df_formulas.to_sql("formulas", con=engine, if_exists="replace", index=False)

        print(f"ETL Pipeline Complete! Exported relational schema to {db_path}")

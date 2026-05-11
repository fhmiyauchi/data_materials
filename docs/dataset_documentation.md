# Materials Intelligence Dataset Documentation

This document describes the datasets exported and compiled by the NEDGEX Data Importer. This data is structured and ready for exploratory data analysis (EDA), correlation analytics, and predictive ML modeling.

---

## 1. Core Materials Dataset
**Source:** Materials Project API (`mp-api`)  
**Filename:** `core_materials.csv`  
**Size:** ~19.44 MB  |  **Records:** 154,879  
**Description:** A comprehensive snapshot of the Materials Project database containing fundamental macroscopic, electronic, and structural properties of crystalline materials.

**Fields:**
- `material_id`: Unique identifier from Materials Project.
- `formula`: Chemical formula.
- `elements`: Comma-separated list of constituent elements.
- `density`: Calculated physical density (g/cm³).
- `band_gap`: Energy band gap in electron-volts (eV).
- `is_metal`: Boolean flag indicating if the material is metallic.
- `formation_energy_per_atom`: Thermodynamic stability metric.
- `energy_above_hull`: Decomposition energy metric.
- `volume`: Unit cell volume.
- `theoretical`: Boolean flag indicating if the structure is purely theoretical or experimentally observed.
- `crystal_system`: Structural classification (e.g., Cubic, Monoclinic).

---

## 2. Experimental Battery Band Gaps
**Source:** Matbench / Matminer (`matbench_expt_gap`)  
**Filename:** `battery_materials.csv`  
**Size:** ~0.06 MB  |  **Records:** 4,604  
**Description:** Experimental band gaps of various materials, highly relevant for screening electrolytes and battery components.

**Fields:**
- `composition`: The chemical composition.
- `gap expt`: The experimentally observed band gap.

---

## 3. Dielectric Constant Dataset
**Source:** Matminer / Figshare (`dielectric_constant`)  
**Filename:** `dielectric_constant.csv`  
**Size:** ~5.87 MB  |  **Records:** 86,075  
**Description:** Tensorial and scalar dielectric properties of materials, useful for identifying novel insulators or capacitors.

**Fields:**
- `material_id`, `formula`, `nsites`, `space_group`, `volume`, `structure`, `band_gap`
- `e_electronic`: Electronic contribution to dielectric constant.
- `e_total`: Total dielectric constant.
- `n`: Refractive index.
- `poly_electronic`, `poly_total`: Polycrystalline averages.
- `pot_ferroelectric`: Potential ferroelectric flag.
- `cif`, `meta`, `poscar`: Raw structural string representations.

---

## 4. Elasticity Dataset (2015)
**Source:** Matminer / Figshare (`elastic_tensor_2015`)  
**Filename:** `elastic_tensor_2015.csv`  
**Size:** ~5.58 MB  |  **Records:** 144,854  
**Description:** Mechanical and elastic properties calculated via DFT.

**Fields:**
- `material_id`, `formula`, `nsites`, `space_group`, `volume`, `structure`
- `elastic_anisotropy`: Measure of directional mechanical dependence.
- `G_Reuss`, `G_VRH`, `G_Voigt`: Shear moduli bounds.
- `K_Reuss`, `K_VRH`, `K_Voigt`: Bulk moduli bounds.
- `poisson_ratio`: Ratio of transverse to axial strain.
- `compliance_tensor`, `elastic_tensor`, `elastic_tensor_original`: Full tensorial data.
- `cif`, `kpoint_density`, `poscar`: Structural representations.

---

## 5. Matbench Phonons
**Source:** Matbench / Matminer (`matbench_phonons`)  
**Filename:** `matbench_phonons.csv`  
**Size:** ~0.71 MB  |  **Records:** 19,641  
**Description:** Highest frequency optical phonon mode peak (useful for thermal conductivity analytics).

**Fields:**
- `structure`: JSON/Dict representation of the crystal structure.
- `last phdos peak`: The highest frequency peak in the phonon density of states.

---

## 6. Matbench MP Gap
**Source:** Matbench / Matminer (`matbench_mp_gap`)  
**Filename:** `matbench_mp_gap.csv`  
**Size:** ~180.36 MB  |  **Records:** 4,033,888 (incl. structure string representations)  
**Description:** A massive dataset correlating structural inputs to DFT-calculated PBE band gaps.

**Fields:**
- `structure`: JSON/Dict representation of the crystal structure.
- `gap pbe`: PBE calculated band gap.

---

## 7. Steel Strength
**Source:** Matminer / Figshare (`steel_strength`)  
**Filename:** `steel_strength.csv`  
**Size:** ~0.06 MB  |  **Records:** 312  
**Description:** Experimental mechanical properties of various steel alloys based on their elemental composition.

**Fields:**
- `formula`: Alloy formula.
- Elements: `c`, `mn`, `si`, `cr`, `ni`, `mo`, `v`, `n`, `nb`, `co`, `w`, `al`, `ti` (Weight percentages of alloying elements).
- `yield strength`: Yield stress.
- `tensile strength`: Ultimate tensile strength.
- `elongation`: Ductility metric.

---

## Data Science Recommendations
- **Correlation Merging:** The datasets can be merged/joined using `formula` or `material_id` where applicable.
- **Structural Parsing:** Fields like `structure`, `cif`, and `poscar` contain raw string or JSON representations. They will need to be parsed using `pymatgen` or converted into numerical features using `matminer` featurizers before feeding them into scikit-learn or deep learning models.
- **Handling NaN/Missing:** Some thermodynamic values (like `formation_energy_per_atom` in the core dataset) may contain null values if uncalculated.

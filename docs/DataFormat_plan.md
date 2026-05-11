# Relational Data Cleansing & ETL Pipeline

Transforming raw Materials Science datasets into a clean relational database requires handling a fundamental domain problem: **A Chemical Formula (Composition) is NOT a unique material.** (e.g., Carbon can be Graphite or Diamond, which have different `material_id`s and properties).

To solve this and fulfill your request for strict relational mappings (1:1, 1:N), I propose building a new **Data Transformer Pipeline** (`data_transformer.py`).

## Proposed Relational Architecture

We will restructure the data into a Star Schema. 

### 1. `formulas` (Master Parent Table)
- **Primary Key:** `standard_formula`
- Every dataset will have its formulas parsed and standardized using `pymatgen.core.Composition(formula).reduced_formula`.

### 2. `materials` (1:N with Formulas)
- **Primary Key:** `material_id` (e.g., `mp-149`)
- **Foreign Key:** `standard_formula`
- *Reasoning:* A single formula can have multiple polymorphs (crystal structures), meaning 1 Formula = N Materials.

### 3. Structure-Specific Tables (1:1 or 1:N with Materials)
Datasets that are calculated via DFT and tied to a specific crystal structure.
- **`properties_core` (1:1):** Basic MP properties (`band_gap`, `density`). FK: `material_id`.
- **`properties_dielectric` (1:1):** Dielectric tensors. FK: `material_id`.
- **`properties_elastic` (1:1):** Elastic tensors. FK: `material_id`.
- **`structures_matbench` (1:N):** Phonon peaks and PBE gaps linked to specific structures. FK: `material_id` (We will attempt to cross-match the structures, or generate a synthetic structure ID linked to the formula).

### 4. Composition-Specific Tables (1:N with Formulas)
Experimental datasets where we only know the formula, but NOT the specific crystal structure.
- **`experiments_battery` (1:N):** Battery gap experiments. FK: `standard_formula`.
- **`experiments_steel` (1:N):** Steel mechanical properties. FK: `standard_formula`.

## Implementation Steps
1. Create `src/data_importer/data_transformer.py`.
2. Implement a `pymatgen` standardization function that cleanses `formula` and `composition` strings.
3. Use Pandas to map, join, and cleanse the raw CSVs into the relational tables described above.
4. Export the final normalized tables into the `materials.db` SQLite database using proper Primary Key and Foreign Key constraints.
5. Update `just import` to trigger this ETL pipeline instead of blindly copying CSVs.

## User Review Required
> [!IMPORTANT]
> **Data Processing Time Warning:** Running `pymatgen` formula standardization and structure parsing across ~300,000 combined records will take a few minutes to process during the `just import` phase. Is a 2-5 minute processing time acceptable for this ETL step?
> 
> Please approve this relational architecture, and I will begin writing the transformation pipeline!

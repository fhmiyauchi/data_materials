# Material Science AI & Data Intelligence Platform

> ⚠️ **Academic Exercise:** This is a data science portfolio project in the domain of materials science and AI intelligence. It is **not a real commercial project.** All data is sourced from publicly available open-source datasets for educational and portfolio demonstration purposes only.

---

## 📑 Table of Contents

1. [Project Overview & Objectives](#1--project-overview--objectives)
2. [Dashboard Reports](#2--dashboard-reports)
3. [Data Sources](#3--data-sources)
4. [Data Engineering & Pipeline Architecture](#4--data-engineering--pipeline-architecture)
5. [Scientific Domain & Materials Science](#5--scientific-domain--materials-science)
6. [Exploratory Data Analysis (EDA) Methodology](#6--exploratory-data-analysis-eda-methodology)
7. [Engineering & Code Quality Practices](#7--engineering--code-quality-practices)
8. [Skills & Technology Stack](#8--skills--technology-stack)
9. [Quick Start](#9--quick-start)
10. [Project Structure](#10--project-structure)

---

## 1. 🎯 Project Overview & Objectives

Imagine a research company that needs to find the next breakthrough battery material. They have access to data on **154,879 different materials**, each with dozens of physical and chemical properties. Manually exploring this is impossible.

This project demonstrates how a modern **Data + AI platform** can transform raw scientific data into actionable intelligence — from automated data ingestion all the way to interactive analytical dashboards and AI-ready feature engineering.

### What Was Built

```
Raw Scientific APIs (Materials Project + Matminer)
      ↓
Automated ETL Pipeline (Python + Docker)
      ↓
Normalized Relational Database (SQLite, 9 tables, 154k+ records)
      ↓
5 Interactive EDA Dashboards (Apache Superset)
      ↓
[Next] AI Recommendation Engine (Task 2 — planned)
```

### Two-Phase Roadmap

| Phase | Status | Description |
|---|---|---|
| **Task 1 — Data Intelligence Platform** | ✅ Complete | ETL pipeline + relational database + EDA dashboard suite |
| **Task 2 — AI Recommendation Workbench** | 🔜 Planned | Semantic queries using vector embeddings + LLM reasoning |

---

## 2. 📊 Dashboard Reports

Five EDA dashboards were built in Apache Superset and exported as PDF reports:

| # | Dashboard | Business Question Answered |
|---|---|---|
| 1 | [Material Landscape Overview](./reports/1%20-%20Material%20Landscape%20Overview.pdf) | "What is the overall shape of the material universe?" |
| 2 | [Battery Material Intelligence](./reports/2%20-%20Battery%20Material%20Intelligence.pdf) | "Which materials are best for EV batteries and energy storage?" |
| 3 | [Stability & Conductivity Analytics](./reports/3%20-%20Stability%20%26%20Conductivity%20Analytics.pdf) | "Which materials are ferroelectric, dielectric, or optically active?" |
| 4 | [Mechanical & Structural Intelligence](./reports/4%20-%20Mechanical%20%26%20Structural%20Intelligence.pdf) | "Which materials are mechanically strongest and most durable?" |
| 5 | [AI Recommendation Workbench](./reports/5%20-%20AI%20Recommendation%20Workbench.pdf) | "Which materials should we prioritize for R&D investment?" |

---

## 3. 🗄️ Data Sources

All data is sourced from publicly available, peer-reviewed scientific repositories:

| Dataset | API / Library | Description |
|---|---|---|
| Core material properties | [Materials Project](https://materialsproject.org/) via [`mp-api`](https://github.com/materialsproject/api) | Density, band gap, crystal system, formation energy, stability for 154k+ materials |
| Dielectric constants | [Matminer `dielectric_constant`](https://hackingmaterials.lbl.gov/matminer/dataset_summary.html) | Dielectric tensor, refractive index, ferroelectric candidates |
| Elastic tensors | [Matminer `elastic_tensor_2015`](https://hackingmaterials.lbl.gov/matminer/dataset_summary.html) | Bulk modulus, shear modulus, Poisson ratio, anisotropy |
| Experimental band gaps | [Matminer `expt_gap`](https://hackingmaterials.lbl.gov/matminer/dataset_summary.html) | Real-world measured band gaps for model validation |
| Calculated band gaps | [Matminer `mp_gap`](https://hackingmaterials.lbl.gov/matminer/dataset_summary.html) | DFT-computed band gaps for cross-referencing |
| Steel alloy properties | [Matminer `steel_strength`](https://hackingmaterials.lbl.gov/matminer/dataset_summary.html) | Tensile strength, yield strength, elongation for alloys |

**Data at a Glance:**
- 154,879 unique materials
- 9 normalized relational tables
- Properties ranging from quantum-mechanical (band gap) to macroscopic (tensile strength)

---

## 4. 🏗️ Data Engineering & Pipeline Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  External APIs                       │
│    Materials Project API    Matminer Datasets         │
└───────────────┬─────────────────────┬───────────────┘
                │                     │
         ┌──────▼──────────────────────▼──────┐
         │           DataImporter              │
         │   • Pydantic v2 schema validation   │
         │   • mp-api MPRester client          │
         │   • Matminer dataset loader         │
         │   • Raw CSV persistence             │
         └──────────────┬─────────────────────┘
                        │
         ┌──────────────▼─────────────────────┐
         │          DataTransformer            │
         │   • pymatgen formula normalization  │
         │   • Formula caching (memoization)   │
         │   • Tensor → scalar extraction      │
         │   • SQLAlchemy relational loader    │
         └──────────────┬─────────────────────┘
                        │
         ┌──────────────▼─────────────────────┐
         │          materials.db (SQLite)       │
         │   Star schema — 9 relational tables  │
         └──────────────┬─────────────────────┘
                        │  (read-only mount)
         ┌──────────────▼─────────────────────┐
         │         Docker Compose Stack         │
         │   superset_app   (port 8088)         │
         │   superset_redis (cache layer)       │
         │   superset_init  (bootstrap)         │
         └─────────────────────────────────────┘
```

### Relational Data Model

Nine heterogeneous source datasets are normalized into a star schema:

```
formulas
  └── materials (formula FK)
        ├── properties_core       (material_id FK) — density, band_gap, crystal_system, stability
        ├── properties_dielectric (material_id FK) — poly_total, n, pot_ferroelectric
        ├── properties_elastic    (material_id FK) — K_VRH, G_VRH, poisson_ratio, anisotropy
        ├── experiments_battery   (formula FK)     — experimental gap measurements
        └── structures_mp_gap     (formula FK)     — DFT-computed gap for validation
experiments_steel (standalone)  — tensile/yield strength, elongation, alloy composition
```

**Key normalization decisions:**
- Chemical formulas are canonicalized via `pymatgen.Composition.reduced_formula`, so `"Fe2O3"`, `"FeO1.5"` and `"Fe₂O₃"` all resolve to the same key.
- The 3×3 dielectric tensor (`e_total`) is stored as a JSON string; the scalar `poly_total` (VRH average) is persisted alongside it to avoid real-time tensor reduction during querying.
- **Polymorphism** is correctly modeled: `formulas` ↔ `materials` is a one-to-many relationship, because the same chemical formula (e.g., `C`) can have multiple distinct crystal structures (diamond vs. graphite → different `material_id`).

---

## 5. ⚗️ Scientific Domain & Materials Science

### Key Physical Concepts Applied

**Thermodynamic Stability**

| Metric | Meaning |
|---|---|
| `energy_above_hull` (eV/atom) | Distance from the DFT convex hull. 0 = globally stable ground state phase; > 0 = metastable, may decompose. |
| `formation_energy_per_atom` (eV/atom) | Cohesive energy relative to elemental references. More negative = more strongly bound. |

**Electronic Structure**

| Metric | Meaning |
|---|---|
| `band_gap` (eV) | Kohn-Sham DFT gap. 0 = metal; < 3 eV = semiconductor; > 4 eV = insulator. Systematically underestimated by PBE functional. |
| `is_metal` | Materials Project classification flag. |

**Dielectric & Optical Properties**

| Metric | Meaning |
|---|---|
| `e_total` | Full 3×3 dielectric tensor. Direction-dependent — not directly plottable as a scalar. |
| `poly_total` | Voigt-Reuss-Hill (VRH) polycrystalline average. Scalar proxy for the dielectric constant. |
| `n` | Refractive index. |
| `pot_ferroelectric` | Potential ferroelectric flag. Relevant for FeRAM memory and piezoelectric sensors. |

**Mechanical Properties**

| Metric | Meaning |
|---|---|
| `K_VRH` (GPa) | VRH bulk modulus — resistance to volumetric compression. |
| `G_VRH` (GPa) | VRH shear modulus — resistance to shape change under applied stress. |
| `elastic_anisotropy` | Deviation from isotropic response. Low = predictable in all directions. |
| `poisson_ratio` | Lateral contraction per unit axial extension. ν ≈ 0.3 for most metals. |

*VRH = Voigt-Reuss-Hill averaging — the standard method for computing polycrystalline elastic averages from single-crystal tensors.*

### Formula vs. Material — An Important Distinction

The database distinguishes **Formulas** (chemical recipe) from **Materials** (physical crystal structure). This is intentional: diamond and graphite share the formula `C` but are completely different materials with different properties. The dataset has ~120k unique formulas but ~155k unique materials — because many formulas are polymorphic.

---

## 6. 🔍 Exploratory Data Analysis (EDA) Methodology

### Dashboard Design — A Progressive Funnel

The five dashboards were designed following a structured, hypothesis-driven narrowing approach:

```
Dashboard 1 — Universe (154k materials, no filters)
      ↓  "What crystal families exist? What is the density/band gap distribution?"
Dashboard 2 — Domain Filter (battery candidates, is_metal = 0)
      ↓  "Which lightweight semiconductors are thermodynamically stable?"
Dashboard 3 — Property Deep Dive (dielectric, ferroelectric, optical)
      ↓  "Which materials have extreme electrical or optical behaviors?"
Dashboard 4 — Mechanical Screening (elasticity, anisotropy, steel alloys)
      ↓  "Which materials are mechanically superior for structural applications?"
Dashboard 5 — Composite Scoring (top 100 ranked candidates)
      ↓  "Which specific materials are the best multi-objective candidates?"
```

### Derived Feature Engineering

Raw columns alone are insufficient for decision-making. Several composite scores were engineered:

```sql
-- Normalized multi-objective battery candidate score (0–1 range)
-- Weights: lightweight 30%, semiconductor profile 30%, stability 40%
stability_score =
    (1.0 - density / 26.58)             * 0.3
  + (1.0 - ABS(band_gap - 1.5) / 17.89) * 0.3   -- peak at 1.5 eV (optimal semiconductor)
  + (1.0 - energy_above_hull / 9.71)    * 0.4
```

**Why not use `1/band_gap`?** An earlier formula was validated against real data and rejected: 47% of rows have `band_gap = 0` (metals), causing infinite scores and ranking only metallic materials. The min-max normalized formula is more robust and domain-correct.

### Data Quality Findings

| Column | Zero/Null Count | Handling |
|---|---|---|
| `density` | 0 | ✅ Clean |
| `band_gap` | 72,640 (47%) | `NULLIF + 1e-6` epsilon guard |
| `energy_above_hull` | 33,973 (22%) | `+ 1e-6` epsilon to keep stable materials in rankings |

### Model Validation

Dashboard 2 includes a scatter plot of `gap_pbe` (calculated) vs. `gap_expt` (experimental). Points on the diagonal ($y = x$) indicate accurate computational predictions. Outliers reveal materials where the DFT-PBE model fails — a standard validation technique in computational materials science.

### Virtual Datasets Pattern

Complex multi-table JOINs are encapsulated as named Virtual Datasets in Superset, making them reusable across charts without repeating SQL:

```sql
-- Virtual: Ferroelectric Candidates
SELECT m.standard_formula, c.energy_above_hull, c.band_gap, d.poly_total, d.n
FROM properties_dielectric d
JOIN properties_core c ON d.material_id = c.material_id
JOIN materials m ON d.material_id = m.material_id
WHERE d.pot_ferroelectric = 1
ORDER BY c.energy_above_hull ASC
```

---

## 7. 🛠️ Engineering & Code Quality Practices

### Python Code Quality

All code in `src/` is enforced by three automated quality tools:

```bash
just lint       # ruff check src --fix    — style + unused imports + complexity
just format     # ruff format src         — opinionated, deterministic formatting
just typecheck  # mypy src                — strict static type analysis
```

**Pydantic v2 validation** at the API boundary ensures malformed data is caught before it touches the database:

```python
class MaterialData(BaseModel):
    material_id: str
    density: float
    band_gap: float
    is_metal: bool
    formation_energy_per_atom: Optional[float] = None
    energy_above_hull: Optional[float] = None
    crystal_system: Optional[str] = None
```

**Memoized formula standardization** avoids redundant computation during bulk ETL:

```python
# Dict cache prevents repeated pymatgen.Composition() calls across 150k formulas
self._formula_cache: Dict[str, str] = {}
```

### Security & Configuration

- All secrets (`MP_API_KEY`, `SUPERSET_SECRET_KEY`, `ADMIN_PASSWORD`) are loaded exclusively from `.env`. No credentials are hardcoded anywhere.
- `.env` is gitignored; `.env.example` is committed as a safe template.
- `materials.db` is mounted into the Superset container as **read-only (`:ro`)** — the analytics layer cannot corrupt the source of truth.

### Docker & Infrastructure

| Pattern | Implementation |
|---|---|
| **Single compose file** | ETL pipeline + Superset stack unified in one `docker-compose.yml` |
| **Named volume** | `superset_home` persists Superset metadata across container restarts |
| **Health-checked init** | `superset_init` waits for `curl //health` before bootstrapping |
| **Read-only data mount** | `materials.db` mounted as `:ro` into Superset |
| **Environment injection** | All secrets injected via Docker Compose env vars from `.env` |

### Reproducible Dashboard Bootstrap

Dashboard creation is automated via Superset's internal ORM — no manual UI clicking required:

```python
# setup_dashboard_1.py — runs inside the container
table = SqlaTable(table_name="Virtual: Ferroelectric Candidates", database=database, sql=sql)
db.session.add(table)
table.fetch_metadata()  # syncs discovered columns to Superset's cache
db.session.commit()
```

This means the entire analytics stack is reproducible from a single `just eda-up` command on a fresh machine.

### Developer Experience

A `justfile` provides memorable one-word commands for the full lifecycle:

```bash
just download    # Fetch raw datasets from APIs
just import      # Run ETL → build materials.db
just eda-up      # Start Superset stack → open http://localhost:8088
just eda-down    # Stop the stack
just lint        # Code quality check
just format      # Auto-format source
just typecheck   # Static type analysis
```

---

## 8. 📋 Skills & Technology Stack

| Category | Technologies |
|---|---|
| Language | Python 3.11+ |
| Data Validation | Pydantic v2 |
| Data Processing | Pandas, pymatgen |
| Materials Science APIs | mp-api (Materials Project), Matminer |
| Database | SQLite + SQLAlchemy ORM |
| Analytics / Dashboards | Apache Superset (open-source) |
| Containerization | Docker + Docker Compose |
| Task Runner | just |
| Linting & Formatting | Ruff |
| Type Checking | mypy |

**Core Engineering Competencies Demonstrated:**

| Area | Evidence |
|---|---|
| ETL Pipeline Design | API → CSV → transformation → normalized relational DB |
| Data Modeling | Star schema design across 9 heterogeneous sources |
| Python Engineering | Pydantic, type hints, mypy, Ruff, memoization, OOP |
| SQL & Analytics | Multi-table JOINs, derived metrics, formula validation |
| Open Source Dashboarding | Full Superset stack with programmatic ORM bootstrapping |
| DevOps | Docker, named volumes, health checks, env injection |
| Scientific Domain Knowledge | DFT concepts, thermodynamic stability, tensor reduction |
| Data Quality | Zero-value analysis, null handling, score formula validation |

---

## 9. 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- [`just`](https://github.com/casey/just): `brew install just`
- Free API key from [next.materialsproject.org](https://next.materialsproject.org/)

### Run

```bash
# Clone and enter the project
git clone <repo-url> && cd material-science-platform

# Configure environment
cp .env.example .env
# Edit .env → set MP_API_KEY, SUPERSET_SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD

# Download raw datasets from public APIs
just download

# Run ETL pipeline → builds data/materials.db
just import

# Start the Superset analytics stack
just eda-up
# → Open http://localhost:8088 and log in with your ADMIN credentials

# Stop when done
just eda-down
```

---

## 10. 📁 Project Structure

```
material-science-platform/
├── data/                              # SQLite database (gitignored)
│   └── materials.db
├── docs/
│   └── PLAN_data_exploratory_dashboard.md   # EDA blueprint with chart SQL specs
├── reports/                           # Exported PDF dashboard snapshots
│   └── *.pdf
├── src/
│   ├── data_importer/
│   │   ├── data_importer.py           # API fetchers with Pydantic validation
│   │   └── data_transformer.py        # Formula normalization + SQLite loader
│   ├── eda/
│   │   ├── superset_config.py         # Superset application configuration
│   │   ├── superset-init.sh           # Container bootstrap (admin user + db init)
│   │   ├── setup_dashboard_1.py       # Dashboard 1 ORM bootstrap
│   │   ├── setup_dashboards_2_to_6.py # Dataset registration + dashboard shells
│   │   └── setup_charts_2_to_6.py    # Chart definitions for dashboards 2–6
│   └── main.py                        # CLI entry point (download / import)
├── .env.example                       # Environment variable template (committed)
├── .env                               # Local secrets (gitignored)
├── docker-compose.yml                 # Full stack orchestration
├── justfile                           # Developer task runner
└── requirements.txt
```

---

## 📄 License & Attribution

This project is created for **educational and portfolio purposes only.**

| Source | License |
|---|---|
| Materials Project data | [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Matminer datasets | [BSD 3-Clause](https://github.com/hackingmaterials/matminer/blob/main/LICENSE) |

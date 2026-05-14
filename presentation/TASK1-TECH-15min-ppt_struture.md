# Task 1 — Technical Walkthrough (15 min)
## Material Science Data Intelligence Platform

---

## ⏱️ Time Budget

| Slide | Topic | Time |
|---|---|---|
| 1 | Title | — |
| 2 | Context & Disclaimer | 20 sec |
| 3 | Deliverables Planned | 30 sec |
| 4 | Research Methodology & Domain | 2 min |
| 5 | Data Acquisition + ELT Architecture | 2 min |
| 6 | Engineering Practices, DevOps & Challenges | 2.5 min |
| 7 | EDA — Living Tool + Findings | 2 min |
| **8** | **Live Demo (Superset)** | **5–7 min** |
| 9 | Deliverables Delivered | 30 sec |
| **—** | **Discussion** | **15 min** |

---

## Slide 1 — Title

**Title:** Building a Material Science Data Intelligence Platform
**Subtitle:** ELT Pipeline · Relational Data Modeling · Open-Source EDA
**Date:** May 2025

---

## Slide 2 — Context & Scope *(~20 sec)*

- 🧪 **Exercise, not production** — decisions optimised for demonstrating reasoning
- 🤖 **AI-assisted** — used for domain research & implementation; material science insights are illustrative, not verified scientific facts
- 📂 **Open public data** — Materials Project & Matminer (peer-reviewed)

---

## Slide 3 — Deliverables: What Was Planned *(~30 sec)*

| # | Deliverable |
|---|---|
| 1 | Domain & data source research |
| 2 | Data acquisition pipeline (REST API + Python libs) |
| 3 | Data cleansing & normalisation |
| 4 | Relational star schema (formula ↔ material ↔ properties) |
| 5 | Chemical formula standardisation + FK creation |
| 6 | Reproducible ELT pipeline (Docker + justfile) |
| 7 | 5 EDA dashboards · 20+ charts (Apache Superset) |
| 8 | Python code quality (Pydantic v2, mypy, Ruff) |

> *(We revisit this on the last slide.)*

---

## Slide 4 — Research Methodology & Domain *(~2.5 min)*

**Headline:** *"Research first. Code second."*

```
Phase 1: Domain Research → Phase 2: Data Scoping
→ Phase 3: ELT Design → Phase 4: EDA Planning → Phase 5: Build
```

**What was studied in material science:**

| Concept | Why it drove the design |
|---|---|
| Crystal systems | Geometry → properties; needed as a dimension in every dashboard |
| Energy Above Hull | 0 = synthesisable; the primary stability filter |
| Band Gap | Conductivity proxy: 0 = metal, 1–3 eV = semiconductor, >4 eV = insulator |
| Formula ≠ Material | Carbon → diamond AND graphite → must model as separate tables |
| DFT / PBE | Computational method that underestimates band gaps — validated by experiment |
| VRH averaging | Reduces a 3×3 tensor to one scalar; needed for `poly_total` to be plottable |

**Key dataset decision:**

| Method | Tool | Data acquired |
|---|---|---|
| REST API | `mp-api` (Materials Project) | 154k materials, core properties |
| Python lib | `matminer.datasets.load_dataset()` | Dielectric, elastic, battery, steel |

All raw data is **persisted to CSV before transformation** — replay safety if the API changes.

> ⚠️ *AI was used as a domain research accelerator. Insights are illustrative — not validated scientific conclusions.*

---

## Slide 5 — Data Acquisition + ELT Architecture *(~2.5 min)*

**Headline:** *"Simple ingestion now. Production-replaceable by design."*

### Exercise → Production mapping:

| Exercise (this project) | Production equivalent |
|---|---|
| REST API + Python lib | Airflow DAG / Kafka event-driven connector |
| Local CSV persistence | AWS S3 / GCS Data Lake |
| SQLite | AWS RDS / Redshift / BigQuery |
| Docker Compose | Kubernetes / Databricks |
| Manual `just` trigger | Spark jobs / dbt pipeline |

> 🗣️ *"The pattern is designed to be replaced. The ingestion logic doesn't change — the infrastructure does."*

### ELT, not ETL:

| ETL | ELT (used here) |
|---|---|
| Transform before load | Load raw → transform at query time |
| Pipeline changes for every new query | New questions need only new SQL |
| Raw data lost after transform | Raw always preserved |

```
Extract: mp-api + Matminer → raw CSV
Load:    raw CSV → SQLite (minimal change)
Transform: SQL Virtual Datasets inside Superset
           + formula normalisation only (needed for FK)
```

---

## Slide 6 — Engineering Practices, DevOps & Challenges *(~2.5 min)*

**Headline:** *"Good engineering decisions — even in an exercise."*

### Data engineering:
- **Pydantic v2:** validates every API response at the boundary — `"N/A"` on a float field raises immediately, not silently
- **Domain-aware cleansing:** `band_gap = 0` (47% of rows) is a metal — kept, not deleted
- **Star schema:** `formulas` ↔ `materials` 1-to-many — correctly models polymorphism (diamond ≠ graphite, same formula)
- **Formula FK:** `pymatgen.Composition.reduced_formula` + memoized cache → `"Fe2O3"`, `"FeO1.5"` → same JOIN key

### Python & DevOps:
```bash
just lint / format / typecheck   # Ruff + mypy — automated quality gates
```
- `materials.db` mounted `:ro` inside Superset — analytics cannot corrupt the source
- Named volume `superset_home` — dashboards survive container restarts
- All secrets from `.env` — no hardcoded credentials

### Top challenges:

| Challenge | Resolution |
|---|---|
| New domain from scratch | AI-accelerated research + primary sources |
| `e_total` is a tensor, not a float | Found via EDA → switched to scalar `poly_total` |
| Superset ECharts JSON is undocumented | ORM bootstraps shell; complex charts finalised once in UI |
| Formula JOIN fails silently | pymatgen normalisation + memoized cache |

---

## Slide 7 — EDA: Living Tool + Key Findings *(~2 min)*

**Headline:** *"Not a report — a shared analytical workspace for three types of users."*

| User | How they use it |
|---|---|
| **Data Engineer** | Validate pipeline output — distributions, FK joins, null rates |
| **Data Scientist** | Feature exploration, scoring formula iteration |
| **Materials Expert** | Scientific hypothesis testing, candidate screening |

### 5 dashboards — one progressive EDA funnel:
```
Dashboard 1: Universe (154k, no filters)   → "What do we have?"
Dashboard 2: Battery Lens (is_metal = 0)   → "Which are battery candidates?"
Dashboard 3: Specialty Properties          → "Ferroelectrics, dielectrics, optics"
Dashboard 4: Mechanical Screening         → "Strongest, stiffest materials"
Dashboard 5: AI Feature Engineering       → "Top 100 ranked — AI-ready features"
```

**EDA as validation — findings that changed engineering decisions:**
- 47% `band_gap = 0` → scoring formula v1 rejected (∞ scores for metals)
- `e_total` is a tensor → switched to scalar `poly_total`
- DFT underestimates band gaps → quantified before using computed values for ranking

---

## Slide 8 — Live Demo: Apache Superset *(~5–7 min)*

**Headline:** *"Let the data speak."*

> 🖥️ *Open Superset at http://localhost:8088 — or use the PDF reports as fallback.*

### Suggested walkthrough path:

**Dashboard 1 — Material Landscape:**
- KPI cards: 154k materials · 120k formulas · 7 crystal systems
- Bar: Crystal system distribution → *"Monoclinic dominates"*
- Scatter: Stability Landscape → *"22% sit at hull = 0 — synthesisable"*

**Dashboard 2 — Battery Intelligence:**
- Scatter: Conductivity vs Density → *"Bottom-left = the target zone"*
- Scatter: Exp. vs Calculated Band Gaps → *"DFT underestimates — this is the model error we must account for"*

**Dashboard 5 — AI Workbench:**
- Bubble chart: Top 100 candidates → *"These are the materials ranked by our composite score"*
- Feature engineering table → *"These derived columns are what the AI model will train on"*

> 🗣️ *"The dashboards are a living tool — you can filter in real time, add charts, and share SQL.
> This is the foundation the AI layer will be built on."*

---

## Slide 9 — Deliverables: What Was Delivered *(~30 sec)*

| # | Deliverable | Status |
|---|---|---|
| 1 | Domain & data source research | ✅ |
| 2 | Data acquisition pipeline (REST API + Python libs) | ✅ |
| 3 | Data cleansing & normalisation | ✅ |
| 4 | Relational star schema (formula ↔ material ↔ properties) | ✅ |
| 5 | Chemical formula standardisation + FK creation | ✅ |
| 6 | Reproducible ELT pipeline (Docker + justfile) | ✅ |
| 7 | 5 EDA dashboards · 20+ charts (Apache Superset) | ✅ |
| 8 | Python code quality (Pydantic v2, mypy, Ruff) | ✅ |

---

---

## 📎 Appendix — Discussion Ready

> *Use these slides to go deeper during the 15-min Q&A. Each maps to a condensed point in the main presentation.*

---

### Appendix A — Research-First Methodology (detail)

The project followed a strict phase-gated approach before any code was written:

```
Phase 1: Domain Research
  → What is material science? What is computational materials informatics?
  → What are the key physical properties and their scientific meaning?
  → What questions are worth answering with this data?
         ↓
Phase 2: Data Scoping
  → Which public datasets are reliable and joinable?
  → What is a realistic scope for an exercise of this size?
  → What must be explicitly deferred?
         ↓
Phase 3: ELT Design
  → How should data be structured? What requires normalisation?
  → What can be loaded raw and transformed at query time?
         ↓
Phase 4: EDA Planning
  → What scientific hypothesis does each dashboard test?
  → What chart type is correct for each hypothesis?
         ↓
Phase 5: Implementation
  → Pipeline · data model · dashboards · code quality
```

---

### Appendix B — Domain Research Detail

| Concept | What was learned | Impact on design |
|---|---|---|
| Crystal systems | 7 geometric families determine material behavior | Dimension in all dashboards |
| Energy Above Hull | 0 = on the thermodynamic convex hull = synthesisable | Primary stability filter |
| Band Gap | 0 = metal · 1–3 eV = semiconductor · >4 eV = insulator | Drives battery candidate filter (`is_metal = 0`) |
| Formula ≠ Material | Same formula → multiple structures (polymorphism) | Forced `formulas` ↔ `materials` 1-to-many model |
| DFT / PBE | Computational method that systematically underestimates band gap | Dashboard 2: exp vs. computed cross-validation chart |
| VRH averaging | Reduces a 3×3 dielectric tensor to one scalar | `poly_total` used instead of unplottable `e_total` |

> ⚠️ *All material science domain knowledge was AI-accelerated. Insights are illustrative — not verified scientific conclusions.*

---

### Appendix C — Data Acquisition: Full Detail

**REST API — `mp-api` (Materials Project):**
- Authenticates via API key from `.env`
- Paginates automatically through 154k records
- Returns structured Python objects → validated by Pydantic before any processing

**Python library — `matminer.datasets.load_dataset()`:**
- Downloads pre-curated, peer-reviewed ML-ready DataFrames
- No crawling or scraping required — data is maintained by Lawrence Berkeley National Lab

**Raw data persistence pattern:**
- All downloads saved as CSV files before any transformation
- If the API changes or a dataset is updated, raw data is preserved for replay without re-downloading

---

### Appendix D — Data Ingestion: Pydantic Validation

```python
class MaterialData(BaseModel):
    material_id: str
    density: float
    band_gap: float
    is_metal: bool
    formation_energy_per_atom: Optional[float] = None  # optional — many materials missing
    energy_above_hull: Optional[float] = None           # optional — may not be computed
    crystal_system: Optional[str] = None               # optional — may not be classified
```

**What this catches:**
- API returns `"N/A"` for a numeric field → `ValidationError` raised at boundary, not silently propagated as `NaN` downstream
- Missing optional fields default to `None` explicitly — downstream code handles nulls, not crashes

**Additional ingestion practices:**
- All API keys from `.env` only — never hardcoded
- Ingestion runs inside Docker — no local Python environment dependency

---

### Appendix E — Data Cleansing: Full Table

| Issue | Scale | Action | Scientific reasoning |
|---|---|---|---|
| `band_gap = 0` | 72,640 rows (47%) | ✅ Kept | Zero gap = metal. Perfectly valid physically. |
| `energy_above_hull = 0` | 33,973 rows (22%) | ✅ Kept | Hull = 0 = globally stable phase. Most valuable result. |
| `e_total` is a 3×3 tensor string | All dielectric rows | ✅ Serialised as JSON; `poly_total` retained | Tensor cannot be plotted — scalar VRH average used |
| Inconsistent formula notation | Cross-dataset | ✅ Normalised via pymatgen | Enables JOIN across all 6 datasets |
| Steel dataset has no `material_id` | All rows | ✅ Standalone table | No MP material_id is available for alloy compositions |

> *"In a naive pipeline, `band_gap = 0` would be treated as missing data and removed —
> silently deleting 47% of the dataset. Domain knowledge must drive cleansing decisions."*

---

### Appendix F — Data Architecture & Modelling: Full Star Schema

**The polymorphism problem:**
```
Formula: C  →  material_id: mp-66  (diamond — hardest natural material, insulator)
               material_id: mp-48  (graphite — conductor, lubricant)
```
A flat table keyed on `formula` would silently merge these into one row.

**Solution: Explicit 1-to-many star schema**
```
formulas                     (chemical identity — 1 row per unique canonical formula)
  └── materials              (physical structure — N rows per formula, polymorphic)
        ├── properties_core          (density, band_gap, stability, crystal_system)
        ├── properties_dielectric    (poly_total, n, pot_ferroelectric, e_total tensor)
        ├── properties_elastic       (K_VRH, G_VRH, poisson_ratio, anisotropy)
        ├── experiments_battery      (experimental gap measurements)
        └── structures_mp_gap        (DFT-computed gap for cross-validation)
experiments_steel              (standalone — no material_id FK from MP available)
```

**Key decisions:**
- `formulas` = chemical identity; `materials` = physical structure
- All property tables join on `material_id` — single stable FK throughout
- `experiments_steel` is left standalone — forcing a join would introduce false data

---

### Appendix G — Formula Standardisation: Full Implementation

**The problem across 6 datasets:**
```
"Fe2O3"   ← Matminer notation
"FeO1.5"  ← Alternative ratio
"Fe₂O₃"  ← Unicode subscript
```
A JOIN on raw formula strings returns **0 matches** silently.

**Full implementation with memoization:**
```python
from pymatgen.core import Composition
from typing import Dict

class DataTransformer:
    def __init__(self, data_dir: str):
        self._formula_cache: Dict[str, str] = {}  # memoize cache

    def standardize_formula(self, raw_formula: str) -> str:
        if pd.isna(raw_formula) or not str(raw_formula).strip():
            return "UNKNOWN"
        raw_str = str(raw_formula)
        if raw_str in self._formula_cache:         # O(1) cache hit
            return self._formula_cache[raw_str]
        try:
            reduced = Composition(raw_str).reduced_formula
            self._formula_cache[raw_str] = reduced
            return reduced
        except Exception:
            self._formula_cache[raw_str] = raw_str  # fallback — keep original
            return raw_str
```

**Why memoize?** `Composition()` is an expensive pymatgen call involving chemical parsing. With 154k rows and frequent formula repetition, the cache eliminates redundant computation — a practical performance pattern for bulk ETL.

---

### Appendix H — EDA Planning: Objectives-First Design

Each dashboard was specified in `PLAN_data_exploratory_dashboard.md` before Superset was opened:

1. **Scientific/business question** the dashboard must answer
2. **Primary tables** and JOIN logic required
3. **Chart type** and why it is the right fit for that hypothesis
4. **Exact axes, dimensions, and metrics**

**Example specification — Dashboard 2, Experimental vs Calculated Band Gaps:**
```
Scientific question: Is our DFT computational model trustworthy?
Chart type: Scatter Plot (comparing two continuous variables)
Dataset: Virtual JOIN of experiments_battery + structures_mp_gap ON formula
X = gap_pbe (DFT-calculated)
Y = gap_expt (experimentally measured)
What to look for:
  → Points on the y=x diagonal = accurate model
  → Systematic upward offset = DFT underestimates (expected for PBE functional)
  → Outliers far off diagonal = model fails for that crystal type
```

---

### Appendix I — EDA: Multi-Team Usage Detail

| User type | What they do in the dashboard | Specific example |
|---|---|---|
| **Data Engineer** | Validate pipeline — check distributions, confirm FK joins, verify null handling | Stability Landscape: confirms hull values are correctly distributed; no anomalous negatives |
| **Data Scientist** | Explore features, iterate on scoring formulas, test distributions | Band Gap histogram: revealed 47% zeros — changed scoring formula entirely |
| **Materials Expert** | Test scientific hypotheses, screen candidates, compare with known materials | Battery dashboard: filter crystal system, compare experimental vs. DFT band gaps |

**Why Apache Superset:**
- SQL-native — any team member with SQL knowledge can create their own chart
- Virtual Datasets — complex JOINs are encapsulated and reusable across teams without copy-pasting SQL
- Open-source — no vendor dependency, no licensing cost, full auditability of the tool itself

---

### Appendix J — Python & DevOps: Full Detail

**Three automated quality gates:**
```bash
just lint       # ruff check src --fix    — PEP8, unused imports, complexity rules
just format     # ruff format src         — deterministic formatting (Rust-based, fastest)
just typecheck  # mypy src                — strict static type analysis
```

**Type annotations throughout:**
```python
def standardize_formula(self, raw_formula: str) -> str: ...
self._formula_cache: Dict[str, str] = {}
def fetch_materials(self) -> List[MaterialData]: ...
```

**Full Docker practices:**

| Pattern | Implementation | Why |
|---|---|---|
| Read-only data mount | `materials.db` → `:ro` inside Superset container | Analytics layer cannot corrupt the source of truth |
| Named volume | `superset_home` for Superset metadata | Dashboards persist across container restarts |
| Health-checked init | `superset_init` waits for `curl //health` | Prevents bootstrap race condition on startup |
| Single compose file | ETL + Superset stack in one `docker-compose.yml` | One command to reproduce the entire stack |
| Env-var secrets | All credentials injected from `.env` | No hardcoded secrets, ever |

**`justfile` — full developer workflow:**
```bash
just download   # Fetch raw datasets from APIs
just import     # Run ETL → build data/materials.db
just eda-up     # Start Superset stack → http://localhost:8088
just eda-down   # Stop the stack
just lint       # Code quality check
just format     # Auto-format source
just typecheck  # Static type analysis
```

---

### Appendix K — Challenges: Full Detail

| Challenge | Effort | Resolution |
|---|---|---|
| **Learning material science from scratch** | High | AI-accelerated domain research + Materials Project documentation + Matminer papers |
| **`e_total` is a 3×3 tensor, not a float** | Medium | Discovered via EDA when Superset returned 0 for all values; switched to scalar `poly_total` |
| **Superset ECharts JSON is undocumented** | High | ORM bootstrap scripts generate the boilerplate; complex charts (scatter, bubble, histogram) finalized once in UI |
| **Formula JOIN fails silently across datasets** | Medium | All 4 notation variants resolved via `pymatgen.Composition.reduced_formula` + memoized cache |
| **SQLite metadata conflict** (Superset's own DB vs. `materials.db`) | Medium | Separated via Docker named volume for Superset metadata; `materials.db` mounted `:ro` |
| **Scoring formula broke on 47% zero band gaps** | Low | Caught immediately via EDA; replaced `1/band_gap` with min-max normalised formula |

> 🗣️ *"The most interesting challenges were at domain boundaries — where material science
> meets data engineering. That's exactly where the interesting engineering happens."*

---

### Appendix L — Scoring Formula: Two Iterations

**Version 1 — Rejected:**
```sql
material_score =
    (1 / NULLIF(density, 0))           * 0.3
  + (1 / NULLIF(band_gap, 0))          * 0.3
  + (1 / NULLIF(energy_above_hull, 0)) * 0.4
```
**Why rejected:** 47% of `band_gap` values are exactly 0 (metals) → `1/0` → infinite scores → all metals ranked #1. Completely wrong for battery cathode selection.

**Version 2 — Adopted:**
```sql
material_score =
    (1.0 - (density / 26.58))               * 0.3   -- lightweight
  + (1.0 - ABS(band_gap - 1.5) / 17.89)    * 0.3   -- peaks at 1.5eV (semiconductor sweet spot)
  + (1.0 - (energy_above_hull / 9.71))      * 0.4   -- thermodynamically stable
```
- Min-max normalised using known dataset ranges → all scores in [0, 1]
- `band_gap = 1.5 eV` is the scoring peak (optimal semiconductor for battery operation)
- Metals (`band_gap = 0`) score 0.79 on conductivity term (correct: still conductive, just excluded by `is_metal = 0` filter)

---

### Appendix M — Superset Automation Limitation

**What works programmatically (via Superset ORM):**
```python
table = SqlaTable(table_name="Virtual: ...", database=database, sql=sql)
db.session.add(table)
table.fetch_metadata()  # syncs column list after SQL change
db.session.commit()
```

**What requires one-time UI finalization:**
Modern ECharts-based visualisations (scatter plot, histogram, bubble chart) store their configuration as an opaque, undocumented JSON payload generated by the React frontend. This JSON cannot be reliably constructed programmatically because:
- The schema is not publicly documented
- It contains version-specific React component state
- Small differences in the JSON structure cause the chart to silently fail

**Resolution used:**
- ORM scripts create the chart shell and register the dataset
- The first manual "Edit Chart → Update Chart" in the UI finalises the JSON
- After that, the chart is persistent and exportable

This is a known architectural limitation of Superset — not an implementation gap.

---

### Appendix N — Scientific Glossary

| Term | Plain English | Used in |
|---|---|---|
| Energy Above Hull (eV/atom) | "How far from the most stable known structure — 0 = real-world material" | Dashboards 1, 2, 3, 5 |
| Formation Energy (eV/atom) | "How strongly the material wants to hold together" | Dashboard 1 |
| Band Gap (eV) | "How conductive the material is" | All dashboards |
| poly_total | "Scalar dielectric constant — ability to store charge" | Dashboard 3 |
| K_VRH (GPa) | "Resistance to being compressed / crushed" | Dashboard 4 |
| G_VRH (GPa) | "Resistance to being twisted / sheared" | Dashboard 4 |
| Elastic Anisotropy | "How direction-dependent the mechanical response is — 0 = uniform in all directions" | Dashboard 4 |
| Poisson Ratio | "How much a material narrows when stretched — 0.3 = most metals" | Dashboard 4 |
| Ferroelectric | "Can flip its internal electrical state — used in FeRAM memory and sensors" | Dashboard 3 |
| Polymorphism | "Same formula, different crystal structure → different material with different properties" | Data model |
| DFT / PBE | "Physics simulation method — fast but underestimates band gap by ~40% vs. experiment" | Dashboard 2 |
| VRH averaging | "Voigt-Reuss-Hill — standard method to reduce a 3D tensor to a single scalar" | Dashboard 3 |


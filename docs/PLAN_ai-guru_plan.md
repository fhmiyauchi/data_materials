# Task 2 — AI-Driven Development Workflows
## Material Intelligence Platform Evolution Plan

---

## 1. Objective

The goal of Task 2 is to evolve the existing Material Intelligence platform into an AI-assisted decision-support system capable of:

- semantic material search,
- intelligent material recommendation,
- multi-objective material ranking,
- AI-assisted exploratory analysis,
- and natural-language interaction with material datasets.

The platform should augment researchers and engineers by transforming structured scientific datasets into actionable material intelligence.

---

## 2. Strategic Direction

Instead of attempting fully autonomous material discovery or large-scale scientific simulation, the proposed solution focuses on:

### "AI-Augmented Material Intelligence"

This direction is intentionally pragmatic, scalable, explainable, and aligned with modern AI engineering practices.

The proposed system combines:

- structured scientific datasets,
- semantic search,
- embeddings,
- vector retrieval,
- ranking engines,
- rule-based scoring,
- and LLM reasoning.

---

## 3. Existing Foundation from Task 1

The following capabilities were already implemented during Task 1.

### Data Engineering

- ELT pipeline (Extract → Load → Transform in SQL)
- Relational star schema (`formulas → materials → properties_core / dielectric / elastic`)
- Normalized material relationships via `pymatgen.Composition.reduced_formula`
- Scientific data standardization and cleansing (domain-aware, not generic null removal)
- Curated analytical datasets

### Scientific Datasets

| Table | Source | Rows |
|---|---|---|
| `materials` + `properties_core` | Materials Project (mp-api) | ~154k |
| `properties_dielectric` | Matminer | ~1.2k |
| `properties_elastic` | Matminer | ~1.7k |
| `structures_phonons` | Matbench | ~1.3k |
| `structures_mp_gap` | Matbench | ~100k+ |
| `experiments_battery` | Matminer | ~500 |
| `experiments_steel` | Matminer | ~300 |

### Analytical Layer (Superset Dashboards)

- Dashboard 1: Material Universe Overview
- Dashboard 2: Battery Candidate Intelligence
- Dashboard 3: Specialty Properties (dielectric, ferroelectric)
- Dashboard 4: Mechanical Property Screening
- Dashboard 5: AI Feature Engineering & Composite Scoring

### AI Readiness Already in Place

- Normalized feature space (`band_gap`, `density`, `energy_above_hull`, `crystal_system`)
- Composite scoring formula (v2) developed during Task 1 EDA
- Relationship graph between formulas and structures (polymorphism handled)
- Scalable analytical schema ready for SQL-based curation

Task 2 builds directly on top of this foundation.

---

## 4. Proposed AI Use Cases

The platform should support intelligent scientific and engineering queries.

### 4.1 Material Discovery Queries

Examples:

- "Find lightweight conductive materials for EV batteries"
- "Find thermally stable materials with low density"
- "Suggest materials similar to NMC but safer"
- "Find materials with high dielectric constant and low band gap"
- "Recommend sustainable alternatives to cobalt-based materials"

### 4.2 Comparative Intelligence Queries

Examples:

- "Compare LFP vs NMC across conductivity, density, and stability"
- "What are the trade-offs between stability and conductivity?"
- "Which materials maximize energy efficiency while minimizing density?"
- "Which crystal system produces the most stable battery candidates?"

### 4.3 Scientific Exploration Queries

Examples:

- "Which crystal systems dominate conductive materials?"
- "Which properties correlate most strongly with band gap?"
- "Which materials are outliers in density vs conductivity?"

---

## 5. Recommended System Architecture

The recommended architecture is a hybrid AI retrieval and reasoning platform.

### 5.1 High-Level Architecture

```text
User Query
    ↓
LLM Intent Parser
    ↓
AI Orchestration Layer
    ↓
Hybrid Retrieval Engine
    ├── SQL Query Engine         (deterministic filters)
    ├── Vector Similarity Search (semantic matching)
    └── Rule-Based Scoring      (multi-objective ranking)
    ↓
Material Ranking Engine
    ↓
LLM Explanation Layer
    ↓
Final Recommendation
```

### 5.2 Why Hybrid Retrieval?

Pure LLM-based reasoning is insufficient for scientific material recommendation.
The platform combines:

| Capability | Technology |
|---|---|
| Deterministic filtering | SQL on `materials.db` |
| Similarity search | Embeddings + ChromaDB |
| Scientific ranking | Rule-based scoring (reuses Task 1 formula) |
| Natural language interaction | LLM (GPT-4o / Claude / Gemini) |
| Explainability | AI reasoning layer |

---

## 6. Recommended Technical Stack

### 6.1 Backend

| Library | Purpose |
|---|---|
| Python | Core language |
| LangChain or LlamaIndex | AI orchestration |
| SQLAlchemy | SQL query engine over existing `materials.db` |
| Pandas | Feature engineering and data curation |
| Streamlit | Interactive frontend (see Phase 5) |

> **Note on FastAPI:** Not required for the MVP. Streamlit handles the UI directly in Python. FastAPI would only be added if a REST API layer is needed for external integrations.

### 6.2 Database Layer

**Existing (unchanged from Task 1):**
- SQLite `materials.db` — all relational data, mounted `:ro` in Docker

**MVP Vector Store:**
- **ChromaDB** or **FAISS** (local, in-process)
- *Why:* No Postgres migration needed. Integrates directly with Python and persists to a local `.chromadb/` directory. Keeps the "one command to run" developer experience (`just ai-up`) consistent with Task 1.

**Production Evolution (future, not MVP):**
- PostgreSQL + pgvector
- Weaviate / Qdrant

### 6.3 Embedding Models

| Model | Purpose |
|---|---|
| `OpenAI text-embedding-3-small` | Best semantic retrieval quality — recommended default |
| `BAAI/bge-small-en-v1.5` | Open-source, no API key required — fallback |
| `InstructorXL` | Scientific semantic search (heavier, best for domain queries) |

### 6.4 LLM Layer

| Model | Usage |
|---|---|
| GPT-4o | Natural language reasoning and explanation generation |
| Claude | Scientific explanation quality |
| Gemini | Google ecosystem integration |
| Local Llama models | Offline / zero-cost experimentation |

---

## IMPORTANT: Architectural Constraints

### ❌ Do NOT Embed the Entire Scientific Database

The platform contains 150k+ materials with millions of relational rows, tensor payloads, and heavy JSON structures. Embedding the full database is intentionally **not recommended**.

| Risk | Impact |
|---|---|
| Excessive embedding cost | Unnecessary API spend for a prototype |
| Poor semantic retrieval quality | Noisy embeddings from tensor/JSON payloads |
| Slow ingestion pipelines | Poor MVP iteration speed |
| Duplicate polymorph representations | Degraded recommendation quality |
| Reduced explainability | Difficult recommendation reasoning |

### ✅ Recommended AI Strategy: "Curated AI Material Feature Layer"

Operate ONLY on a filtered analytical subset of **500–3,000 materials**, optimized for:

- semantic retrieval quality,
- recommendation explainability,
- embedding efficiency,
- and fast experimentation.

This is sufficient for semantic search, recommendation demos, ranking workflows, and presentation.

### Embedding Representation Rule

**✅ Embed this:**
```text
LiFePO4 is a stable lithium iron phosphate material with low density,
moderate conductivity, strong thermal stability, and suitability for
safe EV battery applications. It has a band gap of 3.2 eV, density
of 3.6 g/cm³, and an energy above hull of 0.0 eV.
```

**❌ Never embed this:**
```json
{ "lattice": {...}, "sites": [...], "tensor": [[...]] }
```

---

## 7. Data Preparation

### 7.1 Material Curation Strategy

The curated AI layer filters materials that:

- have battery-relevant elements: `Li, Fe, Co, Ni, Mn, Al, Cu, Na, P, Ti`
- have complete `band_gap`, `density`, and `energy_above_hull` values
- have `energy_above_hull < 0.2 eV/atom` (near-stable or stable)
- optionally include elastic or dielectric properties

**Curation SQL:**
```sql
SELECT
    m.material_id,
    m.standard_formula,
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
LIMIT 3000
```

### 7.2 `material_features` Table

The output of Phase 1 is a curated, denormalized feature table:

| Column | Source | Notes |
|---|---|---|
| `material_id` | `materials` | Primary identifier |
| `formula` | `materials.standard_formula` | Pymatgen-normalized |
| `density` | `properties_core` | g/cm³ |
| `band_gap` | `properties_core` | eV — 0 = metal |
| `energy_above_hull` | `properties_core` | eV/atom — 0 = perfectly stable |
| `is_metal` | `properties_core` | Boolean |
| `crystal_system` | `properties_core` | 7 classes |
| `formation_energy_per_atom` | `properties_core` | eV/atom |
| `K_VRH` | `properties_elastic` | GPa — **NULL for ~99% of rows** (see note) |
| `G_VRH` | `properties_elastic` | GPa — **NULL for ~99% of rows** |
| `poly_total` | `properties_dielectric` | Scalar dielectric constant |
| `pot_ferroelectric` | `properties_dielectric` | Boolean flag |
| `stability_score` | Derived | Min-max normalized from Task 1 formula |
| `conductivity_score` | Derived | Min-max normalized from Task 1 formula |
| `density_score` | Derived | Min-max normalized from Task 1 formula |
| `relative_cost_index` | Synthetic | See §7.3 |
| `composite_score` | Derived | Weighted sum of above scores |
| `feature_text` | Generated | Natural-language description for embedding |

> **Note on `K_VRH` / `G_VRH`:** Only ~1,700 of 154k materials have elastic data. These columns will be `NULL` for the vast majority of curated materials. The recommendation engine uses them as optional bonus signals — not as required filters. Materials without elastic data are still ranked, just without the elasticity component.

### 7.3 Synthetic `relative_cost_index`

The Materials Project does not provide pricing data. For the MVP, a **synthetic relative cost index** is derived from element abundance in the Earth's crust — a recognized proxy for material cost in materials informatics.

**Derivation logic:**

```python
# Relative crustal abundance (ppm) — inversely proportional to cost
ELEMENT_ABUNDANCE_PPM = {
    "Fe": 56_300,  "Al": 82_300, "Na": 23_600,
    "Mn": 950,     "Ti": 5_650,  "Cu": 60,
    "Ni": 84,      "Li": 20,     "Co": 25,
    "P":  1_050,   # default for unknowns
}

def relative_cost_index(formula: str) -> float:
    """
    Lower score = cheaper (more abundant elements).
    Returns a normalized 0–1 index (1 = most expensive).
    """
    comp = Composition(formula)
    total_inv_abundance = sum(
        amt / ELEMENT_ABUNDANCE_PPM.get(el.symbol, 10)
        for el, amt in comp.items()
    )
    return total_inv_abundance  # normalized across the dataset at feature build time
```

**Interpretation:**
- `LiFePO4` → moderate cost (Li is scarce, Fe is cheap — net: affordable)
- `LiCoO2` → high cost (Co is very scarce)
- `FePO4` → low cost (Fe + P both abundant)

> ⚠️ *This is a synthetic proxy, not real market pricing. It is labeled transparently in the UI as "Element Rarity Index" and included as a qualitative signal only — not a hard filter.*

### 7.4 Semantic Material Descriptions (`feature_text`)

Each curated material gets a generated natural-language description used for embedding.

**Template:**
```python
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
```

---

## 8. Vector Search Layer

### 8.1 Goal

Enable semantic similarity search over the curated material corpus.

Examples:
- "materials similar to LFP"
- "lightweight conductive materials"
- "stable low-cost cathode materials"

### 8.2 Ingestion Workflow

```text
material_features table
    ↓
build_feature_text() → feature_text string
    ↓
Embedding Model (text-embedding-3-small or bge-small)
    ↓
Vector embeddings
    ↓
ChromaDB (persistent local store)
    → Metadata stored: formula, density, band_gap, stability_score,
      relative_cost_index, crystal_system, source_dataset
```

### 8.3 Retrieval Workflow

```text
User query string
    ↓
Same embedding model
    ↓
ChromaDB similarity search (top-k results)
    ↓
Optional: SQL post-filter on metadata (e.g., band_gap < 1.0)
    ↓
Ranked candidates for scoring
```

---

## 9. Recommendation Engine

### 9.1 Goal

Recommend candidate materials based on multiple scientific constraints, ranked by a parameterizable composite score.

### 9.2 Multi-Objective Scoring (Reusing Task 1 Logic)

Task 1 EDA derived and validated the following normalized scoring formula. Task 2 parameterizes the weights dynamically based on the user's intent:

```python
# All scores normalized to [0, 1] using dataset-wide min-max ranges
# (ranges derived from 154k-material dataset in Task 1)

def compute_score(row, weights: dict) -> float:
    conductivity_score = max(0, 1.0 - abs(row.band_gap - 1.5) / 17.89)
    # peaks at band_gap = 1.5 eV (semiconductor sweet spot)
    # metals (band_gap = 0) still score 0.79 — not penalized

    stability_score = max(0, 1.0 - (row.energy_above_hull / 9.71))
    # 0.0 eV/atom → 1.0 (perfectly stable)
    # 0.2 eV/atom → 0.98 (near-stable, still excellent)

    density_score = max(0, 1.0 - (row.density / 26.58))
    # lower density = higher score (lighter = better for many applications)

    cost_score = max(0, 1.0 - row.relative_cost_index)
    # lower element rarity = higher score (more abundant = cheaper proxy)

    return (
        weights.get("conductivity", 0.3) * conductivity_score +
        weights.get("stability",    0.3) * stability_score +
        weights.get("density",      0.2) * density_score +
        weights.get("cost",         0.2) * cost_score
    )
```

### 9.3 Example Recommendation Queries

#### Example 1 — EV Battery Candidates
```text
Find lightweight conductive materials for EV batteries
```
Weights: `conductivity=0.4, stability=0.3, density=0.3, cost=0.0`
Filter: `is_metal = 0` (non-metals only — ionic conductors for cathodes)

---

#### Example 2 — Safer Cathode Alternatives
```text
Suggest safer alternatives to cobalt-based high-nickel cathodes
```
Weights: `stability=0.4, cost=0.4, conductivity=0.2`
Filter: Exclude elements `[Co, Ni]` from formula composition

---

#### Example 3 — High-Dielectric Materials
```text
Find materials with high dielectric constant suitable for capacitors
```
Weights: `stability=0.5, conductivity=0.3` (low band gap = leakage risk)
Filter: `poly_total > 10 AND is_metal = 0 AND pot_ferroelectric = True`
*Note: This query uses the dielectric subset (~1.2k records).*

---

#### Example 4 — Crystal System Exploration
```text
Which cubic crystal materials have the best stability/conductivity balance?
```
Filter: `crystal_system = 'cubic'`
Output: Top 20 ranked by `composite_score` (equal weights)

---

## 10. Natural Language Workflow

### 10.1 Goal

Allow users to interact with material datasets using natural language queries that are automatically translated into hybrid retrieval operations.

### 10.2 Workflow

```text
User Prompt
    ↓
LLM Intent Detection
    (classify: discovery / comparison / exploration)
    ↓
Constraint Extraction
    (extract: target elements, property ranges, optimization direction)
    ↓
Generate SQL filter + weight vector
    ↓
ChromaDB semantic search (top-k candidates)
    ↓
SQL post-filter + composite scoring
    ↓
Ranked material candidates
    ↓
LLM Response Generation (explanation + rationale)
```

### 10.3 Constraint Extraction Examples

| User Query | Extracted Constraints | SQL Filter | Weight Shift |
|---|---|---|---|
| "lightweight conductive material" | low density + low band gap | `is_metal = 0` | `density ↑, conductivity ↑` |
| "safer alternatives to cobalt" | avoid Co, prefer stability | exclude Co from formula | `stability ↑, cost ↑` |
| "thermally stable dielectrics" | high `poly_total` + low hull | `energy_above_hull < 0.1` | `stability ↑` |
| "affordable Li-Fe cathodes" | Li+Fe elements, low rarity | element filter | `cost ↑, stability ↑` |

---

## 11. Application Screens (Streamlit)

The frontend is built in **Streamlit** — the industry standard for AI data applications. It runs entirely in Python alongside LangChain, requiring no separate React/FastAPI stack.

### 11.1 Material Search Interface

- Natural language search input
- Property range filters (sidebar)
- Ranked results table with composite score
- One-click material detail view

### 11.2 Material Recommendation Panel

- Ranked candidates (top 10–20)
- Score breakdown bar chart (conductivity / stability / density / cost)
- AI-generated explanation for the #1 recommendation
- Optimization rationale summary

### 11.3 Material Comparison View

- Side-by-side comparison of 2–3 materials
- Radar chart: conductivity · stability · density · cost · elasticity
- Delta table: which material "wins" on each property
- AI-generated trade-off summary

### 11.4 AI Explainability Panel

Example AI output:
```text
LiFePO4 was ranked #1 because it combines:
  ✅ High structural stability (energy above hull = 0.0 eV/atom)
  ✅ Acceptable conductivity for ionic transport (band gap = 3.2 eV)
  ✅ Low element rarity index (Fe and P are abundant)
  ⚠️  Moderate density (3.6 g/cm³) — not optimal for lightweight applications
     but acceptable for stationary energy storage.
```

---

## 12. MVP Scope

### Must Have

- Curated `material_features` table (Phase 1)
- ChromaDB vector store with semantic embeddings (Phase 2)
- Composite scoring engine reusing Task 1 formula (Phase 3)
- At least 3 working NL query examples end-to-end (Phase 4)
- Streamlit UI with search + recommendation + comparison (Phase 5)
- AI-generated explanation for recommendations (Phase 5)

### Nice to Have

- Conversational memory (multi-turn queries)
- Graph visualization of material similarity network
- Research paper ingestion (RAG on scientific literature)
- Autonomous material optimization (Bayesian search)

---

## 13. Implementation Phases

### Phase 1 — Feature Engineering

**Deliverables:**
- `build_ai_dataset.py` script — reads from `materials.db`, curates 500–3,000 records
- `material_features` table written back to SQLite (or exported as Parquet)
- `relative_cost_index` synthetic column derived from elemental abundance
- `feature_text` semantic descriptions generated for each material
- All scores normalized using Task 1 min-max ranges

### Phase 2 — Embeddings Pipeline

**Deliverables:**
- `build_vector_store.py` — reads `material_features`, generates embeddings, populates ChromaDB
- ChromaDB persistent collection: `materials_semantic`
- Metadata fields stored: `formula, density, band_gap, stability_score, relative_cost_index, crystal_system`
- Retrieval tested with 3 sample queries

### Phase 3 — Recommendation Engine

**Deliverables:**
- `recommendation_engine.py` — scoring, ranking, weight parameterization
- Intent-to-weights mapping (e.g., "lightweight" → `density_weight↑`)
- SQL post-filter layer (deterministic hard constraints)
- End-to-end test: query → ranked top-10 materials

### Phase 4 — LLM Integration

**Deliverables:**
- LangChain chain: intent detection → constraint extraction → hybrid retrieval → ranking
- Prompt templates for explanation generation
- `.env`-based API key injection (consistent with Task 1 DevOps patterns)
- 3 working end-to-end NL query examples

### Phase 5 — Streamlit Frontend

**Recommended Tech: Streamlit + LangChain**

> *Why Streamlit:* Interactive data apps, side-by-side comparison panels, and AI chat interfaces are all buildable entirely in Python. Building a React/Vue frontend + FastAPI REST API would consume too much time for this exercise. Streamlit + LangChain is the production-standard for fast AI prototyping in data science teams.

**Deliverables:**
- `app.py` — main Streamlit application
- Material Search page
- Recommendation panel with score breakdown
- Side-by-side comparison view
- AI explainability panel
- `just ai-up` justfile command to launch the app

---

## 14. Demo Flow

### Step 1 — Show the Foundation
Present the existing Material Intelligence platform (Task 1).
Key points: curated datasets, normalized schema, 5 dashboards.

### Step 2 — Introduce the AI Layer
Explain the hybrid retrieval architecture: SQL + embeddings + scoring.
Show the `material_features` table and example `feature_text`.

### Step 3 — Execute a Semantic Search
```text
Query: "Find lightweight conductive materials for EV batteries"
```
Show ChromaDB returning the top candidates before scoring.

### Step 4 — Apply the Scoring Engine
Show the composite score breakdown for the top candidates.
Explain how weights shift dynamically based on user intent.

### Step 5 — Show the AI Explanation
Display the LLM-generated explanation for the #1 material.
Compare 2 candidates side-by-side (e.g., LiFePO4 vs Na₂FePO4F).

### Step 6 — Future Evolution Roadmap
- Predictive material modeling (ML regression on DFT properties)
- Digital twin integration
- Generative material discovery (GAN / diffusion models)
- Autonomous experimentation pipelines

---

## 15. Strategic Positioning

This project should be positioned as:

### "AI-Augmented Material Intelligence Platform"

Not:
- a generic chatbot,
- a simple dashboard,
- or a fully autonomous scientific discovery engine.

The emphasis remains on:
- **explainability** — every recommendation is justified scientifically,
- **scientific augmentation** — AI accelerates, not replaces, domain expertise,
- **scalability** — the architecture is designed to be production-replaceable,
- **AI-assisted workflows** — researchers guide the system, not the reverse,
- **practical engineering** — clean code, DevOps hygiene, reproducible pipelines.

---

## 16. Final Strategic Narrative

```text
Raw Scientific Data (Materials Project + Matminer)
    ↓
ELT & Standardization (Task 1)
    ↓
Material Intelligence Platform (Superset Dashboards)
    ↓
Exploratory Analytics (5 EDA dashboards)
    ↓
AI Feature Engineering (Curated material_features table)
    ↓
Semantic AI Layer (ChromaDB + embeddings)
    ↓
Material Recommendation Engine (hybrid scoring + LLM)
    ↓
AI-Augmented Scientific Decision Support (Streamlit UI)
```

---

## 17. Closing Statement

> The proposed architecture transforms fragmented scientific material datasets into an AI-augmented Material Intelligence platform capable of supporting semantic exploration, explainable recommendation workflows, and future AI-driven material optimization systems. The design is intentionally pragmatic — built on the clean ELT foundation from Task 1, extended with a curated feature layer, vector retrieval, and LLM reasoning — while remaining fully reproducible with a single `just ai-up` command.

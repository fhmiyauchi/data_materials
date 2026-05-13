# Dashboard 1 — Material Landscape Overview

## Goal
Provide a high-level exploration dashboard for the overall material universe.

This dashboard acts as the executive and scientific entry point into the platform.

---

# Primary Tables
- `properties_core`
- `materials`
- `formulas`

---

# Key Business Questions
- What types of materials exist in the dataset?
- What is the overall distribution of material properties?
- How are crystal systems distributed?
- What percentage of materials are metallic?
- What stability patterns exist?

---

# Recommended KPIs

| KPI | Formula |
|---|---|
| Total Materials | COUNT(material_id) |
| Total Formulas | COUNT(DISTINCT standard_formula) |
| Avg Density | AVG(density) |
| Avg Band Gap | AVG(band_gap) |
| Metallic Materials % | AVG(is_metal) |
| Total Crystal Systems | COUNT(DISTINCT crystal_system) |

---

# Recommended Visualizations

## 1. Materials by Crystal System
### Chart Type
Bar Chart

### Dataset
`properties_core`

### Metrics
- COUNT(material_id)

### Dimension
- crystal_system

---

## 2. Metallic vs Non-Metallic Distribution
### Chart Type
Pie Chart

### Dataset
`properties_core`

### Dimension
- is_metal

---

## 3. Density Distribution
### Chart Type
Histogram

### Dataset
`properties_core`

### Metric
- density

---

## 4. Band Gap Distribution
### Chart Type
Histogram

### Dataset
`properties_core`

### Metric
- band_gap

---

## 5. Stability Landscape
### Chart Type
Scatter Plot

### Dataset
`properties_core`

### Axes
- X = formation_energy_per_atom
- Y = energy_above_hull

### Color
- crystal_system

---

# Dashboard 2 — Battery Material Intelligence

## Goal
Enable battery-focused material exploration and candidate analysis for EV and energy storage applications.

This should be considered the flagship dashboard.

---

# Primary Tables
- `properties_core`
- `experiments_battery`
- `structures_mp_gap`
- `materials`
- `formulas`

---

# Key Business Questions
- Which materials are lightweight and conductive?
- Which materials show promising battery characteristics?
- How do experimental and calculated band gaps compare?
- Which materials provide optimal performance/stability balance?

---

# Recommended Visualizations

## 1. Battery Material Explorer
### Chart Type
Interactive Table

### Filters
- density
- band_gap
- crystal_system
- is_metal

### Display Columns
- formula
- density
- band_gap
- formation_energy_per_atom
- energy_above_hull

---

## 2. Conductivity vs Density
### Chart Type
Scatter Plot

### Dataset
`properties_core`

### Axes
- X = density
- Y = band_gap

### Color
- is_metal

---

## 3. Experimental vs Calculated Band Gaps
### Chart Type
Scatter Plot

### Join

```sql
SELECT
    b.standard_formula,
    b.`gap expt`,
    p.`gap pbe`
FROM experiments_battery b
JOIN structures_mp_gap p
    ON b.standard_formula = p.standard_formula
```

### Axes
- X = gap_pbe
- Y = gap_expt

---

## 4. Top Candidate Materials Ranking
### Chart Type
Ranked Table

### Suggested Derived Score

```sql
-- NOTE: 47% of rows have band_gap=0 (metals) and 22% have energy_above_hull=0 (stable materials).
-- NULLIF + epsilon (1e-6) prevents division-by-zero while keeping all materials in the ranking.
material_score =
    (1.0 / NULLIF(density, 0)) * 0.3 +
    (1.0 / (NULLIF(band_gap, 0) + 1e-6)) * 0.3 +
    (1.0 / (energy_above_hull + 1e-6)) * 0.4
```

### Columns
- formula
- density
- band_gap
- energy_above_hull
- material_score

---

## 5. Material Similarity Explorer
### Chart Type
Comparison Table

### Goal
Compare candidate materials against a selected reference material such as LFP.

### Suggested Metrics
- density
- band_gap
- stability
- crystal_system

---

# Dashboard 3 — Stability & Conductivity Analytics

## Goal
Provide deeper scientific insights into conductivity, dielectric behavior, and stability relationships.

---

# Primary Tables
- `properties_core`
- `properties_dielectric`
- `properties_elastic`

---

# Key Business Questions
- What properties correlate with conductivity?
- Which materials are stable and mechanically robust?
- Which materials may be promising ferroelectrics?

---

# Recommended Visualizations

## 1. Band Gap vs Dielectric Constant
### Chart Type
Scatter Plot

### Join

```sql
SELECT
    c.material_id,
    c.band_gap,
    d.poly_total
FROM properties_core c
JOIN properties_dielectric d
    ON c.material_id = d.material_id
```

### Axes
- X = band_gap
- Y = poly_total

---

## 2. Stability vs Elasticity
### Chart Type
Scatter Plot

### Join

```sql
SELECT
    c.energy_above_hull,
    e.K_VRH
FROM properties_core c
JOIN properties_elastic e
    ON c.material_id = e.material_id
```

### Axes
- X = energy_above_hull
- Y = K_VRH

---

## 3. Ferroelectric Candidate Discovery
### Chart Type
Filtered Table

### Dataset
`Virtual: Ferroelectric Candidates`

### Virtual Dataset SQL
```sql
SELECT
    m.standard_formula,
    c.energy_above_hull,
    c.band_gap,
    d.poly_total,
    d.n
FROM properties_dielectric d
JOIN properties_core c ON d.material_id = c.material_id
JOIN materials m ON d.material_id = m.material_id
WHERE d.pot_ferroelectric = 1
ORDER BY c.energy_above_hull ASC
```

### Display Columns
- standard_formula
- energy_above_hull (Stability)
- band_gap
- poly_total (Dielectric Constant)
- n (Refractive Index)

---

## 4. Refractive Index Analysis
### Chart Type
Histogram

### Dataset
`properties_dielectric`

### Metric
- n

---

# Dashboard 4 — Mechanical & Structural Intelligence

## Goal
Explore mechanical robustness and structural elasticity properties.

---

# Primary Tables
- `properties_elastic`
- `experiments_steel`

---

# Key Business Questions
- Which materials demonstrate high structural resilience?
- How does elasticity vary across materials?
- Which alloys provide optimal strength/ductility trade-offs?

---

# Recommended Visualizations

## 1. Elastic Anisotropy Distribution
### Chart Type
Histogram

### Metric
- elastic_anisotropy

---

## 2. Bulk vs Shear Modulus
### Chart Type
Scatter Plot

### Axes
- X = K_VRH
- Y = G_VRH

---

## 3. Poisson Ratio Distribution
### Chart Type
Histogram

### Metric
- poisson_ratio

---

## 4. Steel Alloy Strength Analysis
### Chart Type
Scatter Plot

### Dataset
`experiments_steel`

### Axes
- X = tensile strength
- Y = elongation

### Bubble Size
- yield strength

---

## 5. Alloy Composition Heatmap
### Chart Type
Heatmap

### Dataset
`experiments_steel`

### Metrics
- c
- mn
- si
- cr
- ni
- mo

---

# Dashboard 5 — AI Recommendation Workbench

## Goal
Bridge the platform from exploratory analytics into AI-assisted material recommendation workflows.

This dashboard directly supports Task 2.

---

# Primary Tables
- `properties_core`
- `properties_dielectric`
- `properties_elastic`
- enrichment tables (future)

---

# Key Business Questions
- Which materials best satisfy multi-objective optimization constraints?
- How can materials be ranked for battery applications?
- How can semantic AI workflows leverage structured material intelligence?

---

# Recommended Visualizations

## 1. Material Recommendation Table
### Chart Type
Ranked Interactive Table

### Suggested Filters
- max_density
- min_band_gap
- stability_threshold
- metallic/non-metallic

### Suggested Columns
- formula
- density
- band_gap
- stability
- recommendation_score

---

## 2. Multi-Objective Optimization Plot
### Chart Type
Bubble Scatter Plot

### Dataset
`Virtual: Multi-Objective Optimization (Top Candidates)` — top 100 ranked candidates at material_id level

### Virtual Dataset SQL
```sql
-- Top 100 battery candidates ranked by a composite stability score.
-- Only non-metals are included (metals are short-circuit risks for battery cathodes).
-- Row count is capped at 100 so bubbles are readable without overlap.
SELECT
    p.material_id,
    m.standard_formula,
    p.crystal_system,
    ROUND(p.density, 4)               AS density,
    ROUND(p.band_gap, 4)              AS band_gap,
    ROUND(p.energy_above_hull, 4)     AS energy_above_hull,
    -- stability_score: high = stable + lightweight + conductive
    ROUND(
        (1.0 - (p.density / 26.58))                       * 0.3 +
        (1.0 - ABS(p.band_gap - 1.5) / 17.89)            * 0.3 +
        (1.0 - (p.energy_above_hull / 9.71))              * 0.4,
    4) AS stability_score
FROM properties_core p
JOIN materials m ON p.material_id = m.material_id
WHERE p.is_metal = 0
  AND p.density IS NOT NULL
  AND p.band_gap IS NOT NULL
  AND p.energy_above_hull IS NOT NULL
ORDER BY stability_score DESC
LIMIT 100
```

### Chart Parameters
- X = density
- Y = band_gap
- Bubble Size = stability_score _(larger = higher ranked candidate)_
- Series = crystal_system _(colors bubbles by crystal family)_
- Entity = standard_formula
- Row Limit = 100

> **Design rationale:** Top 100 pre-ranked materials keeps the chart readable while
> still showing individual `material_id` candidates. Hover over any bubble to see
> the formula. The biggest bubbles in the bottom-left (low density, low band_gap)
> are the highest-priority battery candidates.

---

## 3. AI Feature Engineering Table
### Chart Type
Interactive Table

### Suggested Derived Features
- conductivity_score
- stability_score
- sustainability_score
- weight_efficiency_ratio

---

## 4. Semantic Query Examples
### Chart Type
Markdown Panel

### Example Queries
- “Find lightweight conductive materials”
- “Find safer alternatives to cobalt”
- “Compare materials similar to LFP but lower cost”

---


# Recommended Presentation Sequence

## Recommended Dashboard Walkthrough Order
1. Material Landscape Overview
2. Battery Material Intelligence
3. Stability & Conductivity Analytics
4. Mechanical & Structural Intelligence
5. AI Recommendation Workbench
6. Data Quality & Coverage _(removed from this plan — rebuild if needed)_

---

# Strategic Narrative

## Task 1 Narrative

```text
Raw Scientific Data
    ↓
Normalization & Standardization
    ↓
Material Intelligence Platform
    ↓
Exploratory Scientific Analytics
    ↓
AI-Ready Curated Features
```



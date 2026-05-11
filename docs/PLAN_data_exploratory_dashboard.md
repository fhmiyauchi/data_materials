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
material_score =
    (1 / density) * 0.3 +
    (1 / band_gap) * 0.3 +
    (1 / energy_above_hull) * 0.4
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
    d.e_total
FROM properties_core c
JOIN properties_dielectric d
    ON c.material_id = d.material_id
```

### Axes
- X = band_gap
- Y = e_total

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

### Filter
- pot_ferroelectric = true

### Display Columns
- formula
- band_gap
- e_total
- poly_total

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

### Axes
- X = density
- Y = band_gap

### Bubble Size
- stability score

### Color
- future cost index

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

# Dashboard 6 — Data Quality & Coverage

## Goal
Demonstrate engineering maturity, ETL governance, and scientific dataset integrity.

This dashboard is strategically important.

---

# Primary Tables
All datasets

---

# Key Business Questions
- How complete are the datasets?
- What coverage exists between datasets?
- How successful was normalization?
- What relationships are available for downstream AI workflows?

---

# Recommended Visualizations

## 1. Missing Values Analysis
### Chart Type
Heatmap / Table

### Metrics
Missing values by:
- table
- field
- percentage

---

## 2. Dataset Coverage Summary
### Chart Type
KPI Cards

### Metrics
- formulas with material mappings
- materials with dielectric properties
- materials with elastic properties
- formulas with phonon data

---

## 3. Formula Normalization Success
### Chart Type
KPI + Table

### Metrics
- raw formulas processed
- standardized formulas generated
- normalization success rate

---

## 4. Dataset Relationship Coverage
### Chart Type
Relationship Matrix / Sankey

### Goal
Show relationship density across:
- formulas
- materials
- properties_core
- properties_elastic
- properties_dielectric
- experiments_battery

---

# Recommended Presentation Sequence

## Recommended Dashboard Walkthrough Order
1. Material Landscape Overview
2. Battery Material Intelligence
3. Stability & Conductivity Analytics
4. AI Recommendation Workbench
5. Data Quality & Coverage

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



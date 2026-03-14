# DataHack 2026 - Complexity Lockout Analysis

This repository contains our current competition approach: identify material-specific recycling lockout, optimize 10 micro-hub locations, and quantify impact with explicit assumptions.

## Verified Baseline (Current Repo State)

Using available required datasets (`collection_points.csv`, `public_housing.json`):

- Collection points: 8,858 total, 5,301 public
- Public housing estates: 241 (population proxy: 2,262,060)
- Textiles lockout: 77.5% (public points are 168 of 746)
- Public housing textile median distance: 440m
- Public housing estates >500m from public textile points: 106
- Population >500m for textiles: 1,031,670
- Fairness metric (textile population burden >500m): 45.6%

Current optimization output:

- 10 hubs selected across 10 districts
- Unique coverage within 800m: 47 estates, 516,240 residents
- Textiles >500m: 106 -> 83 estates
- Textile population saved from >500m zone: 301,590

## Important Methodology Note

Private-building coordinates are not currently present in this repo, so private-vs-public distance multipliers are intentionally omitted in outputs. The code supports them if private-building geodata is added.

## Reproducible Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python3 scripts/validate_data.py
python3 run_analysis.py
```

## Control Tower Demo App

```bash
source venv/bin/activate
python3 control_tower/precompute_scenarios.py
streamlit run control_tower/app.py
```

Optional map enhancement:
- add `control_tower/assets/hk_districts.geojson` for district boundary overlays.

## Output Files

Data:

- `data/processed/baseline_metrics.json`
- `data/processed/optimized_hubs.csv`
- `data/processed/estates_full_analysis.csv`
- `data/processed/impact_report.json`

Core presentation visuals (locked narrative):

- `visualizations/01_landfill_composition.png` (hero stream: textiles)
- `visualizations/02_stream_inequality.png` (single fairness metric)
- `visualizations/03_textiles_deep_dive.png` (optimization map)
- `visualizations/06_sensitivity_assumptions.png` (sensitivity + assumptions)

Optional exploration:

- `visualizations/05_interactive_map.html`

## Data Contract

Required:

- `data/raw/collection_points.csv`
- `data/raw/public_housing.json`

Optional:

- `data/raw/private_buildings.csv` or `data/raw/private_buildings.json`
- `data/geo/private_buildings/*` (gml/geojson/gpkg/shp)
- `data/raw/recycling_stations.csv` or `data/geo/recycling_stations/*`

Use:

```bash
python3 scripts/download_data.py
```

for official source URLs and expected locations.

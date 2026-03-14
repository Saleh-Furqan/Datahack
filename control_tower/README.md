# Green Loop Control Tower

Interactive demo app for policy tradeoff simulation in Hong Kong's recycling network.

## What It Does

- Compares four scenarios (`Baseline`, `Mobile-First`, `Hybrid Equity`, `Static Hubs`)
- Uses measured baseline/static outputs from `run_analysis.py`
- Uses explicit modeled assumptions for mobile/hybrid scenarios
- Displays estate-level map, beneficiary analysis, fairness metrics, and sensitivity ranges

## Architecture

```
control_tower/
├── app.py                          # Frontend (Streamlit UI)
├── precompute_scenarios.py         # Backend scenario precomputation
├── backend/
│   ├── __init__.py
│   └── scenario_engine.py          # Recommendation + map/equity helpers
├── data/
│   ├── scenarios.json              # Scenario config + modeling knobs
│   └── scenario_outputs.json       # Generated outputs consumed by app
├── requirements.txt
└── README.md
```

## Run

```bash
source venv/bin/activate
python control_tower/precompute_scenarios.py
streamlit run control_tower/app.py
```

## Optional Map Upgrade

For district boundary overlays, add:

`control_tower/assets/hk_districts.geojson`

The app will auto-detect it.

## Data Inputs

- `data/processed/baseline_metrics.json`
- `data/processed/impact_report.json`
- `data/processed/optimized_hubs.csv`
- `data/processed/estates_full_analysis.csv`

## Claims Policy

- Baseline and static-hubs scenario metrics are measured from pipeline outputs.
- Mobile-first and hybrid scenarios are modeled estimates.
- All diversion and payback outputs are shown as ranges to reflect uncertainty.

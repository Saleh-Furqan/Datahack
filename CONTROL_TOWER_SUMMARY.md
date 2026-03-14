# Green Loop Control Tower - Current Status

## Build Status

- App scaffold: complete
- Scenario engine: complete
- Estate-level HK map: complete
- Scenario precompute pipeline: complete
- Documentation refresh: complete

## Current Scenario Outputs

From `control_tower/data/scenario_outputs.json`:

- **Baseline**: 106 estates >500m, 45.61% textile burden, Gini 0.242
- **Static Hubs**: 83 estates, 32.28% burden, diversion range 3,361-5,882 t/y
- **Mobile-First**: 97 estates, 38.03% burden, diversion range 2,420-5,294 t/y
- **Hybrid Equity**: 87 estates, 32.73% burden, diversion range 3,025-5,882 t/y

## What Was Fixed

1. Scenario sliders now drive real recommendation logic in Auto mode.
2. Map view now uses real estate columns (`estate`, `population`) and no longer crashes.
3. Precompute now uses measured pipeline anchors plus explicit modeled assumptions.
4. Units are standardized to annual tonnes for displayed diversion metrics.
5. Frontend/backend split added for maintainability.

## How To Run

```bash
source venv/bin/activate
python control_tower/precompute_scenarios.py
streamlit run control_tower/app.py
```

## Optional Enhancement

Add `control_tower/assets/hk_districts.geojson` to overlay district boundaries on the map.

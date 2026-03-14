# Green Loop Control Tower - Team Runbook

This runbook is for teammates who need to run, verify, edit, and present the app quickly.

## 1) One-Command Mental Model

If analysis outputs already exist, run:

```bash
cd /home/saleh/datahack
source venv/bin/activate
python control_tower/precompute_scenarios.py
streamlit run control_tower/Home.py
```

## 2) Full Refresh Workflow (Safe Order)

1. Validate data presence:
```bash
source venv/bin/activate
python scripts/validate_data.py
```

2. Re-run analysis pipeline:
```bash
source venv/bin/activate
python run_analysis.py
```

3. Recompute scenario outputs:
```bash
source venv/bin/activate
python control_tower/precompute_scenarios.py
```

4. Launch app:
```bash
source venv/bin/activate
streamlit run control_tower/Home.py
```

## 3) Pre-Demo Checklist

- App starts with no errors.
- Map page renders and is interactive.
- Top-10 hubs in app match `data/processed/optimized_hubs.csv`.
- Impact numbers in app match deck.
- Assumptions page is included in demo path.
- Slide alignment file checked:
  - `docs/SLIDE_ALIGNMENT_CHECKLIST.md`

## 4) Who Changes What

- Scenario logic and costs:
  - `control_tower/data/scenarios.json`
- Recompute scenario outputs:
  - `control_tower/precompute_scenarios.py`
- Shared data loading:
  - `control_tower/backend/data_loader.py`
- Recommendation behavior:
  - `control_tower/backend/scenario_engine.py`
- Look and feel:
  - `control_tower/backend/theme.py`
- Map UX and layers:
  - `control_tower/pages/1_🗺️_Interactive_Map.py`

## 5) Optional Data Layers

You can unlock extra map layers by adding files:

- `data/raw/recycling_stations.csv` (needs lat/lon columns)
- `data/raw/waste_management_facilities.csv` (needs lat/lon columns)
- `control_tower/assets/hk_districts.geojson` (district boundaries)

If absent, app still works.

## 6) Common Issues

## Streamlit not found
```bash
source venv/bin/activate
pip install -r control_tower/requirements.txt
```

## Map opens but no district boundaries
- Add `control_tower/assets/hk_districts.geojson`.

## Numbers changed unexpectedly
- Re-run:
  - `python run_analysis.py`
  - `python control_tower/precompute_scenarios.py`
- Confirm no manual edits in processed outputs.

## Slides and app disagree
- Follow:
  - `docs/SLIDE_ALIGNMENT_CHECKLIST.md`

## 7) Presentation Flow (Team Hand-off)

Suggested speaker split:

1. Speaker A:
   - Problem framing + map evidence.
2. Speaker B:
   - Impact numbers + costs + scenario tradeoffs.
3. Speaker A:
   - Assumptions/validation and close.

## 8) Final Commit Suggestions

Before commit/push:

```bash
git status
python3 -m py_compile control_tower/Home.py control_tower/backend/*.py control_tower/pages/*.py
python control_tower/precompute_scenarios.py
```

Then commit docs + app updates together so teammates get one coherent state.

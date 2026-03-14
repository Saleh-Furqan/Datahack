# Green Loop Control Tower

Interactive Streamlit app for presenting the DataHack 2026 recycling analysis.

## Quick Start

```bash
cd /home/saleh/datahack
source venv/bin/activate
pip install -r control_tower/requirements.txt
python control_tower/precompute_scenarios.py
streamlit run control_tower/Home.py
```

## What This App Shows

- Estate-level textile accessibility under four scenarios.
- Proposed optimized hubs from the analysis pipeline.
- Public stream collection layers (glass, textiles, hazardous, batteries, e-waste).
- Scenario tradeoffs: burden, diversion range, cost, and district inequality.
- Assumptions and 90-day validation protocol.

## Documentation

- Full app walkthrough:
  - `control_tower/APP_WALKTHROUGH.md`
- Team runbook (setup, refresh, troubleshooting, pre-demo checks):
  - `control_tower/TEAM_RUNBOOK.md`
- Quick user guide / doc index:
  - `control_tower/USER_GUIDE.md`
- Deck-to-app consistency:
  - `docs/SLIDE_ALIGNMENT_CHECKLIST.md`

## Scope and Trust Model

- `Baseline` and `Static Hubs` metrics are measured outputs from repository pipeline artifacts.
- `Mobile-First` and `Hybrid Equity` are modeled scenarios with explicit uncertainty.
- Private-building distance comparator is not yet available in this repo; fairness metrics currently use public-housing data.

## File Layout

```text
control_tower/
├── Home.py
├── precompute_scenarios.py
├── requirements.txt
├── backend/
│   ├── data_loader.py
│   ├── scenario_engine.py
│   └── theme.py
├── data/
│   ├── scenarios.json
│   └── scenario_outputs.json
└── pages/
    ├── 1_🗺️_Interactive_Map.py
    ├── 2_📊_Scenario_Compare.py
    ├── 3_📈_Impact_Analysis.py
    └── 4_⚙️_Assumptions.py
```

## Optional Enhancements

- Add `control_tower/assets/hk_districts.geojson` for district boundary overlays.
- Add `data/raw/recycling_stations.csv` (with lat/lon) to enable a dedicated station layer.
- Add `data/raw/waste_management_facilities.csv` (with lat/lon) to enable facility layer overlays.

## Presentation Tip

Use this order in live demo:
1. `Interactive Map` (show problem geography + hubs).
2. `Impact Analysis` (numbers and beneficiaries).
3. `Assumptions` (credibility and validation).
4. `Scenario Compare` (policy tradeoff discussion if time permits).

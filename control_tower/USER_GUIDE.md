# Green Loop Control Tower - User Guide

This guide points to the right documentation depending on what you need.

## Start Here

```bash
cd <repo-root>
source venv/bin/activate
pip install -r control_tower/requirements.txt
python control_tower/precompute_scenarios.py
streamlit run control_tower/Home.py
```

## Documentation Map

- Full app explanation (all pages, controls, metrics, story link):
  - `control_tower/APP_WALKTHROUGH.md`
- Team operations and handoff runbook:
  - `control_tower/TEAM_RUNBOOK.md`
- Slide and app number consistency checklist:
  - `docs/SLIDE_ALIGNMENT_CHECKLIST.md`
- Project-level context:
  - `README.md`

## Quick Navigation for Live Demo

1. `Home.py` (headline metrics + policy selector)
2. `1_🗺️_Interactive_Map.py` (map-first narrative)
3. `3_📈_Impact_Analysis.py` (quant impact)
4. `4_⚙️_Assumptions.py` (credibility and limits)
5. `2_📊_Scenario_Compare.py` (optional deeper rigor)

## Notes

- Baseline and static-hub outputs are measured from pipeline artifacts.
- Mobile-first and hybrid-equity outputs are modeled scenario estimates.
- Private-building comparator is not active in current repo outputs.

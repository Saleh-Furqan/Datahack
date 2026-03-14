# Project Status

**Branch:** `approach2`  
**Date:** March 14, 2026  
**Status:** Analysis pipeline complete and reproducible

## Pipeline Health

- `scripts/validate_data.py` passes required datasets.
- `run_analysis.py` completes all phases and regenerates outputs.
- Visuals are regenerated from current code and data.
- Deck narrative is locked to 4 core visuals (hero, fairness, map, sensitivity).

## Current Verified Metrics

- Collection points: 8,858 total, 5,301 public.
- Public housing: 241 estates, population proxy 2,262,060.
- Textiles lockout: 77.5%.
- Textiles underserved (>500m): 106 estates, 1,031,670 residents.
- Fairness metric (textile population burden >500m): 45.6%.
- After 10 hubs: 83 estates >500m, 301,590 residents saved.
- Unique hub coverage (800m): 47 estates, 516,240 residents.
- Modeled diversion: 3,361 to 5,882 tonnes/year.
- Modeled payback: 9.32 to 40.76 years.

## Known Constraints

- Private-building coordinates are not currently loaded.
- Therefore, private-vs-public distance multipliers are omitted.
- Diversion and payback are assumption-driven model outputs, not observed measurements.
- Sensitivity assumptions are exported to `visualizations/06_sensitivity_assumptions.png`.

## Ready to Do

- Finalize deck with locked metrics from processed JSON files.
- Add explicit assumptions and limitations slide notes.
- Rehearse delivery and Q&A.

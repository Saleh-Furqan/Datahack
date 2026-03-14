# Next Steps (Methodical Execution)

## Step 1 - Freeze Truth Source (Do First)

Run and freeze outputs:

```bash
source venv/bin/activate
python3 scripts/validate_data.py
python3 run_analysis.py
```

Use only these files as the single source of truth:

- `data/processed/baseline_metrics.json`
- `data/processed/optimized_hubs.csv`
- `data/processed/impact_report.json`

Do not use old numbers from archived docs.

## Step 2 - Slide Content Lock

Create a one-page metric sheet (copied from JSON outputs) and lock:

- Textiles lockout %
- Fairness metric (textile population burden >500m)
- Textiles estates >500m before/after
- Textiles population saved
- Unique hub coverage
- Diversion and payback ranges

Every slide number must trace back to one of the three files above.

## Step 3 - Build the Deck (8 Slides)

1. Problem: lockout by stream.
2. Why textiles is the bottleneck.
3. Spatial burden by district.
4. Method (objective, thresholds, constraints).
5. Proposed 10 hubs map.
6. Before/after impact.
7. Economics with assumption box.
8. Implementation plan and pilot recommendation.

Use these locked visuals (no extras unless needed for Q&A):

- `visualizations/01_landfill_composition.png`
- `visualizations/02_stream_inequality.png`
- `visualizations/03_textiles_deep_dive.png`
- `visualizations/06_sensitivity_assumptions.png`

If you need an interactive demo layer for backup:

- `visualizations/05_interactive_map.html`

## Step 4 - Add Assumptions Slide Notes

Include concise assumptions:

- 500m underserved threshold
- 800m hub service radius
- Population proxy (`rental_flats * 2.7`)
- Diversion model capture factors (0.20 to 0.35)
- Landfill gate fee (HK$365/tonne)

## Step 5 - Presentation QA

Before final submission:

- Verify every number in slides against JSON outputs.
- Remove private-comparator claims unless private geodata is added and rerun.
- Practice 2 complete runs (target 8-10 minutes + Q&A).
- Prepare 3 expected challenges:
  - "Why these thresholds?"
  - "How robust are cost estimates?"
  - "Why does textiles dominate impact?"

## Optional Upgrade (Only If Time)

Add private-building geodata (`data/geo/private_buildings/*` or `data/raw/private_buildings.csv/json`) and rerun to enable private-vs-public comparator metrics.

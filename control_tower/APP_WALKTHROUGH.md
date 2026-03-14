# Green Loop Control Tower - Full App Walkthrough

This document explains the full app end-to-end: what each page does, why it exists, how it supports our project thesis, and how to use it in the pitch.

## 1) Core Idea and Why This App Exists

Our project thesis is:

- Hong Kong has many collection points in total.
- Accessibility is not uniform across materials and access rules.
- Textiles are the strongest “hero stream” problem in the current analysis.
- We can reduce textile burden using data-driven placement and scenario planning.

The app is built as a decision-support layer over our analysis outputs. It turns static findings into a live policy conversation:

- Where are estates currently underserved?
- Which interventions reduce burden most?
- What tradeoff appears when budget and equity priorities change?
- Which claims are measured vs modeled?

## 2) Data + Trust Model

## Inputs used by the app

- `data/processed/baseline_metrics.json`
- `data/processed/impact_report.json`
- `data/processed/estates_full_analysis.csv`
- `data/processed/optimized_hubs.csv`
- `control_tower/data/scenarios.json`
- `control_tower/data/scenario_outputs.json` (generated)

## Measured vs modeled outputs

- Measured in pipeline outputs:
  - `baseline`
  - `static_hubs`
- Modeled scenario estimates:
  - `mobile_first`
  - `hybrid_equity`

This distinction is visible in app copy and in the assumptions page.

## 3) App Structure

Main entry:

- `control_tower/Home.py`

Pages:

- `control_tower/pages/1_🗺️_Interactive_Map.py`
- `control_tower/pages/2_📊_Scenario_Compare.py`
- `control_tower/pages/3_📈_Impact_Analysis.py`
- `control_tower/pages/4_⚙️_Assumptions.py`

Shared backend:

- `control_tower/backend/data_loader.py` (single source of truth loaders)
- `control_tower/backend/scenario_engine.py` (recommendation + comparison helpers)
- `control_tower/backend/theme.py` (visual styling)

## 4) Page-by-Page Explanation

## Home Page (`Home.py`)

What it does:

- Gives immediate baseline vs static-hubs headline metrics.
- Lets users set budget + equity preference.
- Uses a scenario recommendation function to suggest a policy mode.
- Provides clean navigation into deeper pages.

Why it matters to the idea:

- Shows this is not just “add bins,” but a policy tradeoff problem.
- Frames equity and budget as first-class decisions.

Main controls:

- Budget slider (`HK$M`, capex)
- Equity priority slider (`0-100`)

## Interactive Map (`1_🗺️_Interactive_Map.py`)

What it does:

- Displays estates as clickable points on a real HK map.
- Colors estates by scenario distance status.
- Overlays proposed hubs and optional 800m rings.
- Adds toggles for public stream layers:
  - glass
  - textiles
  - hazardous
  - batteries
  - e-waste
- Supports optional overlays from extra files:
  - `data/raw/recycling_stations.csv`
  - `data/raw/waste_management_facilities.csv`
- Supports district boundary overlay from:
  - `control_tower/assets/hk_districts.geojson`

Why it matters to the idea:

- It is the clearest visual proof of “where the burden is” and “where interventions land.”
- It connects our thesis to concrete places and populations.

Main controls:

- Scenario selector
- District multi-select
- Max distance filter
- Estates / hubs / rings toggles
- Stream layer toggles and point density cap

## Scenario Compare (`2_📊_Scenario_Compare.py`)

What it does:

- Split-map side-by-side scenario comparison.
- Tradeoff frontier (Pareto-style dominance check across the four scenarios).
- Greedy placement simulator to demonstrate optimization mechanics.
- Metrics dashboard for compact comparison.

Why it matters to the idea:

- Shows we are making explicit policy tradeoffs, not one generic recommendation.
- Supports innovation and rigor criteria by showing method transparency.

Main controls:

- Left/right scenario selectors
- Optimization simulation sliders (hubs, radius)
- Run optimization button

## Impact Analysis (`3_📈_Impact_Analysis.py`)

What it does:

- Reports scenario impacts relative to baseline.
- Shows coverage distributions and population shifts.
- Shows district-level improvement and top beneficiary estates.
- Shows cost split, savings range, payback range, and uncertainty.

Why it matters to the idea:

- Converts map intuition into defendable quantitative impact.
- Supports feasibility and impact criteria directly.

## Assumptions (`4_⚙️_Assumptions.py`)

What it does:

- Lists data sources and metric definitions.
- States measured vs modeled scenario status.
- Discloses assumptions and limitations.
- Provides 90-day validation protocol.

Why it matters to the idea:

- This is the trust layer.
- Helps defend during Q&A and avoids overclaiming.

## 5) How Pages Connect to Judging Criteria

- Innovation & Originality:
  - Interactive scenario controls + tradeoff framing.
- Impact & Feasibility:
  - Beneficiary counts, costs, payback ranges, pilot protocol.
- Analytical Rigor:
  - Explicit measured vs modeled separation and reproducible outputs.
- Presentation & Visualization:
  - Clean map-first storytelling and drill-down pages.

## 6) Recommended Demo Flow (8-10 min)

1. Home:
   - Frame the burden and policy sliders.
2. Interactive Map:
   - Show underserved estates, then static-hub improvements.
3. Impact Analysis:
   - Quantify burden reduction + diversion range + beneficiaries.
4. Assumptions:
   - Show transparency and pilot validation.
5. Scenario Compare:
   - Use as optional deeper rigor segment if time permits.

## 7) Current Known Limits (Important)

- Private-building comparator is not yet active in current repo outputs.
- Mobile/hybrid scenario outcomes are modeled, not measured field results.
- Distance is geodesic proxy, not full pedestrian network routing.

These are acceptable if stated clearly during presentation.

## 8) Where to Edit What

- Change scenario definitions/cost assumptions:
  - `control_tower/data/scenarios.json`
- Recompute app outputs:
  - `python control_tower/precompute_scenarios.py`
- Update visual style:
  - `control_tower/backend/theme.py`
- Update map behavior/layers:
  - `control_tower/pages/1_🗺️_Interactive_Map.py`

## 9) Slide Alignment

Before final deck export, verify with:

- `docs/SLIDE_ALIGNMENT_CHECKLIST.md`

This prevents mismatch between deck numbers and app numbers.

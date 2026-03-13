# Quick Start Guide - DataHack 2026

## Environment Setup (DONE ✓)

```bash
# Virtual environment created
source venv/bin/activate

# All packages installed
# See requirements.txt for full list
```

## Your Next Steps

### Step 1: Download Datasets (START HERE)

Run this to see all URLs:
```bash
source venv/bin/activate
python3 scripts/download_data.py
```

**CRITICAL datasets to download NOW:**
1. Recycling Stations - https://data.gov.hk/en-data/dataset/hk-epd-wrrteam-recycling-station
2. Collection Points - https://data.gov.hk/en-data/dataset/hk-epd-recycteam-waste-less-recyclable-collection-points-data
3. Public Housing - https://data.gov.hk/en-data/dataset/hk-housing-eslocator-eslocator

Save files to: `data/raw/`

### Step 2: Validate Data

```bash
python3 scripts/validate_data.py
```

This checks if files are ready for analysis.

### Step 3: Read the Technical Plan

**Main document:** [docs/TECHNICAL_PLAN.md](docs/TECHNICAL_PLAN.md)

**Key sections:**
- Phase 1: Data acquisition (you're here)
- Phase 2: Spatial analysis (distance calculations)
- Phase 3: Solution design (greedy hub placement algorithm)
- Phase 4: Impact metrics (COMPUTED, not hardcoded)
- Phase 5: Visualizations (before/after maps)
- Phase 6: Presentation structure

### Step 4: Start Analysis

Work through notebooks in order:
1. `notebooks/01_data_cleaning.ipynb` - Clean and merge datasets
2. `notebooks/02_spatial_analysis.ipynb` - Calculate distances, identify gaps
3. `notebooks/03_solution_design.ipynb` - Place optimal hubs
4. `notebooks/04_visualization.ipynb` - Create maps and charts

---

## The Winning Strategy (TL;DR)

**Core idea:** "The 500-Meter Problem"

**What we prove:**
- X% of Hong Kong residents live >500m from recycling facilities
- This creates a significant barrier to recycling participation

**What we deliver:**
- 15-25 specific locations for new micro-hubs
- Before/after maps showing coverage improvement
- Computed impact metrics (population served, distance reduction)
- Two budget scenarios with diminishing returns curve

**Why we win:**
1. **Innovation:** Greedy max-coverage algorithm + equity analysis
2. **Impact:** Practical, low-cost, scalable solution with ESG alignment
3. **Rigor:** Multiple datasets integrated, defendable methodology
4. **Presentation:** Beautiful visualizations + compelling story

---

## Key Technical Decisions

### Distance Calculation
- **Method:** Haversine (straight-line distance)
- **Why:** Fast, defendable, conservative estimate
- **Alternative:** Road network (only if ahead of schedule)

### Hub Placement Algorithm
- **Method:** Greedy max-coverage
- **Rules:**
  - Each hub serves 300m radius
  - No hub within 150m of existing point
  - Maximize population served per hub
- **Why:** Mathematically sound, fast, explainable

### Metrics to Report
**Primary (must-have):**
- % population within 300m (before vs after)
- Count of people newly served
- Median/mean distance reduction

**Secondary (if time):**
- Equity by district
- Waste diversion estimate (with sourced assumptions)

**DO NOT hardcode impact numbers - compute everything from data**

---

## Critical Checkpoints

### Hour 6: Data Freeze
**GO:** All 3 critical datasets clean and merged → proceed with full analysis
**NO-GO:** Data issues → PIVOT to public housing only mode

### Hour 12: Analysis Complete
- Gap analysis done (know the problem)
- Hub locations identified (know the solution)
- Impact metrics calculated (know the results)

### Hour 18: Visualizations Done
- Main before/after map created
- Charts and tables ready
- Exported high-res images

### Hour 22: Presentation Ready
- Deck complete (10 slides)
- Rehearsed at least once
- Q&A prep done

---

## Common Issues & Fixes

**Problem:** Dataset missing coordinates
**Fix:** Use district-level aggregates or skip that dataset

**Problem:** Algorithm too slow
**Fix:** Limit to top 100 underserved locations as candidates

**Problem:** Running behind schedule
**Cut:** Private buildings → Waste tonnage → Equity analysis → Second scenario

**Problem:** Uncertain about impact estimates
**Strategy:** Use ranges, cite sources, be conservative

---

## Team Roles (Assign Now)

**Person 1: Data & Analysis**
- Download and clean datasets
- Distance calculations
- Hub placement algorithm
- Generate metrics

**Person 2: Visualization & Presentation**
- Create maps (Folium)
- Design charts (Plotly)
- Build presentation deck
- Practice delivery

**Both:** Solution design, impact analysis, Q&A prep

---

## Files You Need to Read

1. **[TECHNICAL_PLAN.md](docs/TECHNICAL_PLAN.md)** - Complete technical execution plan
2. **[2DAY_PLAN.md](docs/2DAY_PLAN.md)** - Hour-by-hour timeline
3. **[CREATIVE_EDGE.md](docs/CREATIVE_EDGE.md)** - What makes you stand out
4. **[EVALUATION_CHECKLIST.md](docs/EVALUATION_CHECKLIST.md)** - Judging criteria

---

## The 30-Second Pitch

Practice this:

> "[X]% of Hong Kong residents live more than 500 meters from a recycling point, creating a significant barrier to participation. We analyzed government data to identify where these gaps exist and used a max-coverage algorithm to place 25 new micro-hubs that maximize newly served residents. Our solution improves <300m coverage by [Y] percentage points at an estimated cost range of [C]-[D]. Here's the map."

[Show before/after split-screen map]

---

## Success Criteria

You win if you have:

1. ✓ One clear, data-backed finding (the gap exists, here's proof)
2. ✓ Specific recommendations (15-25 locations with justification)
3. ✓ Computed impact metrics (no hardcoded numbers)
4. ✓ Beautiful main visualization (before/after map)
5. ✓ Confident presentation (practiced, 8-10 min)

Everything else is bonus.

---

## Emergency Contacts & Resources

**Data sources:** All URLs in `scripts/download_data.py`

**Technical docs:**
- GeoPandas: https://geopandas.org/
- Folium: https://python-visualization.github.io/folium/
- Plotly: https://plotly.com/python/

**Competition info:**
- https://libguides.lib.cuhk.edu.hk/datahack/2026-data
- https://libguides.lib.cuhk.edu.hk/datahack

---

**You've got this. Stay focused, work the plan, and you'll win.**

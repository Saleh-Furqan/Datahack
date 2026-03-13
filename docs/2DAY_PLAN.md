# DataHack 2026: 48-Hour Execution Plan

## Reality Check: What We Can Actually Do in 2 Days

Forget the elaborate 4-week plan. Here's what will actually win in a 48-hour hackathon.

---

## The Focused Strategy

**Core Idea:** One killer insight + beautiful visualization beats comprehensive mediocrity

**Our Angle:** "The 500-Meter Problem" - Quantifying how many Hong Kong residents are blocked from recycling by distance, and showing exactly where to add 20-30 micro-hubs for maximum impact.

---

## Hour-by-Hour Plan

### DAY 1: Data & Analysis (12 hours)

#### Hour 0-2: Setup & Data Download
**Tasks:**
- [ ] Set up Python environment (pandas, geopandas, folium, plotly)
- [ ] Download critical datasets:
  - Recycling stations
  - Collection points
  - Public housing estates
  - Private buildings
  - Census data (district level is enough)
- [ ] Quick validation - do files open? Coordinates make sense?

**Division of labor:**
- Person 1: Environment setup
- Person 2: Data download and organization

#### Hour 2-5: Data Cleaning & Integration
**Tasks:**
- [ ] Extract coordinates from all datasets
- [ ] Standardize to same coordinate system
- [ ] Create one master CSV with:
  - All recycling points (lat, lon, type)
  - All housing (lat, lon, population estimate)
- [ ] Calculate basic stats (how many stations total? coverage area?)

**Critical output:** Clean `master_data.csv` ready for analysis

#### Hour 5-8: Core Analysis
**Focus on ONE KEY METRIC: Walking distance**

**Tasks:**
- [ ] For each housing location, find nearest recycling station
- [ ] Calculate straight-line distance (approximation is fine)
- [ ] Classify buildings:
  - Green: <300m to station
  - Yellow: 300-500m
  - Red: >500m (these are our targets)
- [ ] Count population in each category
- [ ] Identify top 20 "worst served" clusters

**Critical output:**
- List of underserved areas ranked by population
- Statistics: "X% of Hong Kong residents walk >500m to recycle"

#### Hour 8-12: Solution Design
**Tasks:**
- [ ] Identify 20-30 optimal new micro-hub locations
  - Start with centers of "red zones"
  - Refine to maximize population coverage
  - Simple algorithm: pick spots that cover most underserved people
- [ ] Recalculate coverage WITH new hubs
- [ ] Generate before/after comparison stats

**Critical output:**
- CSV of proposed hub locations
- Before/After metrics showing improvement

---

### DAY 2: Visualization & Presentation (12 hours)

#### Hour 12-16: Create Killer Visualizations
**Priority visuals (make 4-5 MAX):**

1. **Main Map: Before/After Split Screen**
   - Left: Current stations + red zones showing gaps
   - Right: Current + proposed hubs + green zones showing coverage
   - Use Folium for interactive map

2. **Impact Dashboard**
   - Big numbers:
     - "[X] residents currently underserved (>500m)"
     - "[Y] residents newly served with 25 hubs ([Z]% improvement)"
     - "Median distance reduced: [A]m -> [B]m"
     - "Optional (only if sourced): estimated annual waste diversion range"
   - Simple bar charts

3. **Top 10 Priority Locations**
   - Table/map showing exact addresses for new hubs
   - Population served by each
   - Cost estimate (rough)

4. **One "Human Story" Illustration**
   - Pick one actual neighborhood (e.g., specific housing estate)
   - Show current: "800m walk to recycle"
   - Show proposed: "New hub 150m away"
   - Before/after photos if possible

**Tools:**
- Folium for interactive maps
- Plotly for clean charts
- PowerPoint/Canva for polishing

#### Hour 16-20: Build Presentation
**Structure (10-12 slides max):**

1. **Title Slide**
   - "The 500-Meter Problem: Optimizing Hong Kong's Recycling Access"
   - Team names

2. **The Problem (1 slide)**
   - One shocking statistic: "X million Hong Kong residents walk >500m to recycle"
   - "Result: Low participation, high landfill waste"

3. **Our Approach (1 slide)**
   - "Used 5 government datasets to map every recycling point and housing location"
   - "Identified gaps and optimized new hub placement"

4. **Key Finding: The Gap (2 slides)**
   - Map showing current coverage with red zones
   - Stats on underserved populations

5. **Our Solution (2 slides)**
   - Map showing proposed 25 micro-hubs
   - Table of top 10 priority locations with addresses

6. **Impact (2 slides)**
   - Before/After comparison
   - Big numbers: population served, tons diverted, coverage %
   - Cost estimate and ROI

7. **Implementation (1 slide)**
   - "Quick Wins": 3-5 specific actionable recommendations
   - Partnership opportunities (districts, NGOs)

8. **Scalability (1 slide)**
   - "This method works for any dense city"
   - Mention: Singapore, Tokyo, etc.

9. **Conclusion (1 slide)**
   - Summary of impact
   - Call to action

#### Hour 20-22: Practice & Polish
**Tasks:**
- [ ] Rehearse presentation (divide speaking parts)
- [ ] Time it (aim for 8-10 minutes, leave time for Q&A)
- [ ] Prepare for likely questions:
   - "How did you calculate walking distance?" (straight-line approximation)
   - "What's the cost?" (rough estimate: $5-10K per micro-hub)
   - "How do you know people will use them?" (cite research on proximity)
- [ ] Final check: all data sources cited, team contributions clear

#### Hour 22-24: Buffer & Sleep
- Final tweaks
- Export everything
- Get some rest before presentation

---

## Division of Labor (2-Person Team)

### Person 1: Data & Analysis Lead
**Responsibilities:**
- Data download and cleaning
- Distance calculations and analysis
- Optimization of hub locations
- Generate statistics and metrics

**Skills needed:** Python, pandas, basic GIS

### Person 2: Visualization & Presentation Lead
**Responsibilities:**
- Map creation (Folium)
- Chart design (Plotly/Matplotlib)
- Presentation deck design
- Story and narrative flow

**Skills needed:** Data visualization, design, communication

**Note:** Both should collaborate on solution design and practice presentation together

---

## What to Cut (Stay Focused!)

**DO NOT ATTEMPT:**
- Complex optimization algorithms (heuristics are fine)
- Advanced network analysis (walking routes)
- Behavioral economics modeling
- Mobile collection routes
- Demographic deep dives
- More than two policy scenarios or full what-if tooling
- Interactive dashboards
- 3D visualizations

**These are nice-to-haves for a longer timeline. In 48 hours: FOCUS.**

---

## Critical Success Factors

### Must-Haves:
1. One clear, defensible finding (the 500m problem)
2. Specific, actionable recommendations (20-30 hub locations with addresses)
3. Quantified impact (population served, tons diverted)
4. Beautiful main map (before/after)
5. Clean, practiced presentation delivery

### Nice-to-Haves (only if time):
6. Cost-benefit analysis
7. Multiple visualization types
8. Demographic insights
9. Scalability discussion

---

## Technical Setup (Do This First)

### Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install essentials
pip install pandas geopandas numpy matplotlib seaborn
pip install folium plotly scikit-learn
pip install jupyter notebook

# Save for team
pip freeze > requirements.txt
```

### Folder Structure
```
datahack/
├── data/
│   ├── raw/           # Downloaded datasets
│   └── processed/     # Cleaned CSVs
├── notebooks/
│   ├── 01_data_prep.ipynb
│   ├── 02_analysis.ipynb
│   └── 03_visualization.ipynb
├── visualizations/    # Output maps and charts
└── presentation/      # Final deck
```

---

## Backup Plan (If Data Issues)

**If datasets are messy or incomplete:**
- Focus on PUBLIC HOUSING only (cleaner data, high impact)
- Use district-level aggregates instead of building-level
- Simplify to 3 pilot districts instead of all Hong Kong

**If time runs short:**
- Skip the optimization, manually pick 10-15 obvious gap locations
- Focus on 1-2 killer visualizations instead of many
- Simplify presentation to 8 slides

---

## The Winning Pitch (30-Second Version)

> "2.3 million Hong Kong residents live more than 500 meters from a recycling station. Using government data, we identified exactly where they are and where to place 25 new micro-hubs to serve 1.6 million of them. This would divert an estimated 8,500 tons per year from landfills at a cost of just $200K. Here's the map."
> "[X]% of Hong Kong residents live more than 500 meters from a recycling point. Using government data, we identified where those gaps are and where to place 25 new micro-hubs to maximize newly served residents. This improves <300m coverage by [Y] percentage points at an estimated cost range of [C]-[D]. Here's the map."

**Then show the before/after map. That's your mic drop moment.**

---

## Checklist Before Submission

- [ ] All data sources cited in presentation
- [ ] Team member contributions documented
- [ ] Code uploaded to GitHub with README
- [ ] Presentation deck (PDF + PPTX)
- [ ] Key visualizations exported as PNGs
- [ ] One-page executive summary (optional but good)
- [ ] Practiced delivery at least 2 times

---

## Time Management Rules

1. **Set hard deadlines for each phase** - Don't perfect, move on
2. **Code doesn't need to be pretty** - It needs to work
3. **Visualizations > Analysis depth** - Judges see what you show, not what you coded
4. **Practice the presentation** - Delivery matters as much as content
5. **Sleep at least 4 hours** - You'll present better rested

---

## Final Pep Talk

**You have 48 hours. Other teams will:**
- Overcomplicate things
- Get stuck on data cleaning
- Try to do too much
- Underwhelm on visualization
- Wing the presentation

**You will:**
- Focus on ONE clear insight
- Have specific, mapped recommendations
- Show beautiful before/after visuals
- Deliver a practiced, confident pitch

**That's how you win.**

Let's go.

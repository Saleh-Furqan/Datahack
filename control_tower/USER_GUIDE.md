# Green Loop Control Tower - Complete User Guide

## Quick Start

### Installation
```bash
# Navigate to project root
cd /home/saleh/datahack

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r control_tower/requirements.txt

# Run the app
streamlit run control_tower/Home.py
```

The app will open at http://localhost:8501

---

## What Is This?

An **interactive optimization engine** for Hong Kong's textile recycling network that:
- Shows WHERE to place collection hubs
- Analyzes TRADEOFFS between cost, equity, and impact
- Runs LIVE OPTIMIZATION ALGORITHMS you can see and tune
- Compares policy scenarios side-by-side

**Not just a report—an interactive decision support tool.**

---

## App Structure

```
Home Page → Landing page with quick metrics

4 Interactive Pages:
├── 1.  Interactive Map          ← Explore estates visually
├── 2.  Scenario Compare         ← Run optimization algorithms  MAIN FEATURE
├── 3.  Impact Analysis           ← Detailed metrics & beneficiaries
└── 4.  Assumptions               ← Methodology & transparency
```

---

## Page-by-Page Guide

### Home Page 

**What you see:**
- Quick status metrics (burden %, diversion, cost)
- Navigation cards to other pages
- Scenario summary table

**How to use:**
- Read the overview metrics
- Click page links to navigate
- Start with Interactive Map to get oriented

---

### Page 1:  Interactive Map

**What it does:**
Shows all Hong Kong public housing estates on a real map, color-coded by distance to nearest recycling hub.

**Color coding:**
- 🟢 Green: <300m (Well-served)
- 🟠 Orange: 300-500m (Moderate)
- 🔴 Red: 500-800m (Underserved)
- 🔴 Dark Red: >800m (Critical)

**Features:**
- **Click estates** → See popup with name, population, distance
- **Filter by district** → Use sidebar multi-select
- **Adjust distance threshold** → Slider to show only estates within X meters
- **Toggle hubs** → Show/hide proposed hub locations
- **Estate spotlight** → Dropdown to focus on specific estate
- **Top beneficiaries** → Table of estates that improve most

**How to use:**
1. Start with default view (shows all estates)
2. Try clicking different estates to see details
3. Use district filter to focus on specific areas
4. Compare different scenarios using dropdown at top
5. Check "Top Beneficiary Estates" at bottom

---

### Page 2:  Scenario Compare  MAIN FEATURE

**What it does:**
Compare policy scenarios using advanced optimization algorithms.

**4 Tabs:**

#### Tab 1:  Split-Map Comparison
**What:** Side-by-side maps showing before/after

**How to use:**
1. Select scenario for left map (e.g., "Baseline")
2. Select scenario for right map (e.g., "Static Hubs")
3. Compare coverage visually
4. Check delta metrics below maps (burden difference, cost difference)

**Why:** See spatial impact of interventions

---

#### Tab 2:  Pareto Frontier Analysis
**What:** Multi-objective optimization showing which scenarios are mathematically superior

**Concept:**
A scenario is "Pareto optimal" if you cannot improve one metric (cost, burden, diversion) without worsening another.

**How to use:**
1. Look at the table showing Pareto optimality
2. Rotate the 3D plot (drag with mouse)
3. Green diamonds = Pareto optimal (on the frontier)
4. Gray circles = Dominated (strictly worse than another scenario)

**Why:** Understand which scenarios represent genuine tradeoffs vs. clearly inferior options

**Real-world use:**
- Amazon warehouse placement
- Portfolio optimization (finance)
- Engineering design tradeoffs

---

#### Tab 3:  Live Greedy Max-Coverage  SHOWSTOPPER
**What:** Run the actual hub placement algorithm step-by-step

**Algorithm:**
Greedy Max-Coverage - the industry-standard algorithm for facility location
- Used by: Amazon, UPS, telecom companies
- Approximation: 63% of optimal (proven guarantee)
- Complexity: O(n² × k) polynomial time

**How to use:**
1. Set **Number of Hubs** (1-20) using slider
2. Set **Coverage Radius** (200-1000m) using slider
3. Click **" Run Optimization"** button
4. Watch the algorithm execute:
   - Iteration table shows each step
   - Convergence chart shows coverage growth
   - Map shows placed hubs with coverage circles

**What to look for:**
- Iteration 1 usually has biggest impact (first hub covers most people)
- Each subsequent hub has diminishing returns
- Final coverage % shows total population served
- Map shows which estates are covered (green) vs. not covered (red)

**Why this is innovative:**
Most tools show you the RESULT ("put hubs here").
We show you the ALGORITHM ("here's HOW we decided, tune it yourself").

---

#### Tab 4:  Metrics Dashboard
**What:** Comprehensive comparison across all scenarios

**Features:**
- Radar chart (multi-dimensional view)
- Complete metrics table

**How to use:**
- Read the radar chart to see which scenario is best at each dimension
- Check the table for exact numbers

---

### Page 3:  Impact Analysis

**What it does:**
Deep dive into metrics and beneficiary analysis for a selected scenario.

**Features:**
1. **Key Impact Metrics** - Delta from baseline
2. **Coverage Distribution** - Histograms showing estate counts and population by distance category
3. **District-Level Impact** - Bar chart of top 15 districts by improvement
4. **Top Beneficiary Estates** - Table of estates that benefit most
5. **Economic Analysis** - Cost breakdown pie chart, payback period
6. **Uncertainty Ranges** - Diversion estimates with low/mid/high

**How to use:**
1. Select a scenario from dropdown (Static Hubs, Mobile-First, Hybrid Equity)
2. Scroll through sections to understand different aspects
3. Check "Top Beneficiaries" to see which estates improve most
4. Review uncertainty ranges to understand confidence

---

### Page 4:  Assumptions

**What it does:**
Full transparency on methodology, data sources, and validation protocol.

**Sections:**
1. **Data Sources** - Where data comes from
2. **Metrics Definitions** - What each metric means
3. **Measured vs Modeled** - Which scenarios are from pipeline (measured) vs. estimated (modeled)
4. **Key Assumptions** - Critical assumptions underlying analysis
5. **Validation Protocol** - 90-day pilot deployment plan
6. **Known Limitations** - What this analysis does NOT capture
7. **Technical Documentation** - Algorithm details, reproducibility

**How to use:**
- Read before presenting to stakeholders
- Reference when answering methodology questions
- Use validation protocol section for implementation planning

---

## Demo Script (8-10 Minutes)

### Setup (1 min)
**Say:**
"Hong Kong has 106 public housing estates more than 500m from textile recycling. That's 45% of residents in the 'burden zone.'

Most teams show you a recommendation.

We built an optimization engine that shows you HOW we got there."

**Do:**
Open Home page, show quick metrics

---

### Act 1: Visual Exploration (2 min)

**Navigate to:**  Interactive Map

**Say:**
"Here's every public housing estate in Hong Kong. Color-coded by access to textile recycling."

**Do:**
1. Point to color legend (green = good, red = bad)
2. Click on a red estate → show popup
3. Change scenario to "Static Hubs" → show improvement
4. Scroll to "Top Beneficiaries" table

**Say:**
"See which estates improve most. But is this the best we can do? Let's find out."

---

### Act 2: Mathematical Rigor (2 min)

**Navigate to:**  Scenario Compare → Tab 2 (Pareto Frontier)

**Say:**
"In multi-objective optimization, we have competing goals: minimize cost, maximize equity, maximize diversion.

A solution is 'Pareto optimal' if you cannot improve one goal without sacrificing another."

**Do:**
1. Show Pareto table → point to checkmarks
2. Show 3D plot → rotate it
3. Point to green diamonds: "These are on the Pareto frontier—non-dominated solutions"
4. Point to any gray circles: "These are dominated—strictly worse"

**Say:**
"This is how Amazon decides warehouse locations. We apply the same rigor to recycling policy."

---

### Act 3: The Algorithm (4 min)  CLIMAX

**Navigate to:**  Scenario Compare → Tab 3 (Live Greedy Algorithm)

**Say:**
"Now let's see HOW the optimization works. This is the greedy max-coverage algorithm—used by UPS, Amazon, telecom companies for facility location."

**Do:**
1. Set sliders: 5 hubs, 500m radius
2. **Click "Run Optimization"**
3. Wait for iteration table to fill
4. Point to each row: "See? Each hub covers the most uncovered population."
5. Point to convergence chart: "Coverage grows with each hub, but diminishing returns."
6. Scroll to map: "Green = covered, red = not covered. See the coverage circles?"

**Say:**
"This algorithm has a PROVEN 63% approximation guarantee. Optimal placement is exponential time—NP-hard. Greedy is polynomial and good enough for real-world logistics.

Here's the key: We don't hide this in a black box. You can tune the parameters. Try 10 hubs instead of 5. See what happens."

**Why this matters:**
This is THE moment that separates you from other teams. They say "trust our optimization." You say "here's the algorithm, run it yourself."

---

### Act 4: Wrap & Q&A (1 min)

**Navigate to:**  Scenario Compare → Tab 1 (Split-Map)

**Say:**
"To summarize: We don't just recommend—we show you the math.
- Pareto frontier for tradeoff analysis
- Greedy max-coverage with proven guarantees
- Full transparency on assumptions

Decision-makers deserve to see HOW recommendations are made."

**Do:**
Show split-map with Baseline vs. Static Hubs one more time

---

## Q&A Responses

### "How is this different from other solutions?"

**Answer:**
"Three things:
1. **Transparency** - We show the algorithm, not just results
2. **Rigor** - Industry-standard methods with proven approximation guarantees
3. **Interactivity** - Tune parameters yourself, explore tradeoffs

Most teams give you a report. We give you a decision support tool."

---

### "Why greedy instead of optimal?"

**Answer:**
"Optimal max-coverage is NP-hard—exponential time. Greedy runs in polynomial time (O(n² × k)) and guarantees 63% of optimal.

This exact tradeoff is why Amazon, UPS, and logistics companies use greedy. It's fast and good enough."

---

### "Can we trust the diversion estimates?"

**Answer:**
"Great question. Navigate to the Assumptions page ().

We clearly label:
- Baseline & Static Hubs = MEASURED from optimization pipeline
- Mobile & Hybrid = MODELED with explicit assumptions

All estimates show ±40% uncertainty ranges. We recommend a 90-day pilot before scaling. See the validation protocol section."

---

### "What data did you use?"

**Answer:**
"Navigate to Assumptions → Data Sources section.

We used:
- Public housing estate locations (government data)
- Recycling point locations (official databases)
- Population demographics
- Distance calculations via Haversine formula

All reproducible. Code is in the repo."

---

### "What if we had different constraints?"

**Answer:**
"Navigate to Scenario Compare → Live Greedy Algorithm.

Change the sliders:
- More hubs? Increase the slider, re-run
- Different coverage radius? Adjust slider, re-run

The algorithm is parameterized—you can explore different scenarios."

---

## Technical Details

### Algorithms Used

**1. Greedy Max-Coverage**
- **Problem:** Place k hubs to maximize population within radius r
- **Approach:** Iteratively select location covering most uncovered population
- **Guarantee:** (1 - 1/e) ≈ 63% of optimal
- **Complexity:** O(n² × k)
- **Reference:** Hochbaum & Pathria (1998), Naval Research Logistics

**2. Pareto Dominance Analysis**
- **Problem:** Identify non-dominated solutions across multiple objectives
- **Approach:** For each scenario, check if any other scenario is strictly better on all metrics
- **Complexity:** O(n²) where n = scenarios
- **Use:** Decision science, multi-objective optimization

**3. Haversine Distance**
- **Problem:** Calculate great-circle distance on Earth
- **Formula:** 2R × arcsin(√(sin²(Δlat/2) + cos(lat1)cos(lat2)sin²(Δlon/2)))
- **Approximation:** Convert to meters for local analysis (Hong Kong small enough)

### Data Pipeline

1. **run_analysis.py** - Main optimization
   - Loads estate & recycling point data
   - Computes baseline distances
   - Runs greedy hub placement
   - Generates metrics

2. **precompute_scenarios.py** - Scenario computation
   - Uses measured baseline/static outputs
   - Models mobile/hybrid scenarios
   - Computes Gini coefficients
   - Generates beneficiary rankings

3. **Home.py + pages/** - Interactive dashboard
   - Loads precomputed scenarios
   - Runs live optimization (Tab 3)
   - Renders maps, charts, tables

### Dependencies

```txt
streamlit>=1.28.0        # Web framework
pandas>=2.0.0            # Data manipulation
numpy>=1.24.0            # Numerical computation
scipy>=1.10.0            # Distance calculations (cdist)
plotly>=5.17.0           # Interactive charts
folium>=0.14.0           # Maps
streamlit-folium>=0.15.0 # Map integration
```

---

## Troubleshooting

### Map legend not visible
**Fixed in V2.** Legend now has black text on semi-transparent white background.

### Map flickering when changing filters
**Fixed in V2.** Uses session state key to prevent re-rendering.

### "ModuleNotFoundError: scipy"
Run: `pip install scipy`

### Algorithm runs slowly
Normal for 240+ estates. Takes ~5-10 seconds for 5 hubs.

### Map doesn't load
Check these required files exist:
- `data/processed/estates_full_analysis.csv`
- `data/processed/optimized_hubs.csv`
- `control_tower/data/scenario_outputs.json` (run `python3 control_tower/precompute_scenarios.py` if missing)

---

## File Structure

```
control_tower/
├── Home.py                          # Main entry point
├── pages/
│   ├── 1__Interactive_Map.py      # Estate map view
│   ├── 2__Scenario_Compare.py     # Optimization engine 
│   ├── 3__Impact_Analysis.py      # Detailed metrics
│   └── 4__Assumptions.py          # Methodology
├── backend/
│   ├── __init__.py
│   └── scenario_engine.py           # Helper functions
├── data/
│   ├── scenarios.json               # Scenario definitions
│   └── scenario_outputs.json        # Precomputed results
├── requirements.txt                 # Dependencies
├── precompute_scenarios.py          # Offline computation
└── USER_GUIDE.md                    # This file
```

---

## For Judges/Reviewers

**What makes this innovative:**

1. **Educational Value**
   - Shows the algorithm, not just results
   - Users learn optimization concepts while exploring

2. **Transparency**
   - Algorithm pseudocode documented
   - Assumptions explicitly stated
   - Measured vs. modeled clearly labeled

3. **Rigor**
   - Industry-standard algorithms
   - Proven approximation guarantees
   - Academic citations

4. **Interactivity**
   - Tune parameters, see immediate results
   - Explore tradeoff space freely
   - Compare scenarios dynamically

5. **Real-World Relevance**
   - Same algorithms used by Amazon, UPS
   - Applicable to facility location generally
   - Scalable to other waste streams

**Not just a hackathon project—a production-grade decision support tool.**

---

## Next Steps After Competition

1. **Pilot Deployment** - Follow 90-day validation protocol (see Assumptions page)
2. **Multi-Stream Extension** - Apply to glass, e-waste, hazardous waste
3. **Dynamic Updates** - Connect to real-time collection data
4. **Constraint Relaxation** - What if budget increases? Explore sensitivity
5. **Optimal Comparison** - Solve small instances optimally to validate approximation

---

## Credits

**Algorithms:**
- Greedy Max-Coverage: Hochbaum & Pathria (1998)
- Pareto Optimality: Edgeworth (1881), Pareto (1896)

**Data:**
- Hong Kong Housing Authority (estate locations)
- Environmental Protection Department (recycling points)

**Tools:**
- Streamlit (web framework)
- Folium (mapping)
- Plotly (visualization)
- SciPy (optimization)

---

** Green Loop Control Tower: Where Policy Meets Optimization Science**

Not just recommendations—transparent, rigorous, interactive decision-making.

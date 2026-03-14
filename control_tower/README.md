# Green Loop Control Tower

**Interactive optimization engine for Hong Kong's textile recycling network**

## Quick Start

```bash
# From project root
source venv/bin/activate
pip install -r control_tower/requirements.txt
streamlit run control_tower/Home.py
```

Open http://localhost:8501

## What Is This?

An interactive web app that:
- **Shows** where to place recycling hubs using optimization algorithms
- **Compares** policy scenarios with side-by-side maps
- **Runs** live greedy max-coverage algorithm (industry standard)
- **Analyzes** tradeoffs using Pareto frontier analysis

**Not a static report—an interactive decision support tool.**

## Key Features

### Interactive Map
- Click estates to see details
- Filter by district & distance
- Compare scenarios visually
- View proposed hub locations
- Optional district boundary overlay via `assets/hk_districts.geojson`

### Optimization Engine - MAIN FEATURE
- **Split-map comparison** (before/after side-by-side)
- **Pareto frontier analysis** (multi-objective optimization)
- **Live greedy algorithm** (run hub placement yourself)
- **Radar charts** (multi-dimensional view)

### Impact Analysis
- Coverage distributions
- District-level metrics
- Top beneficiary estates
- Cost-benefit analysis

### Transparency
- Full methodology documentation
- Measured vs. modeled scenarios
- 90-day validation protocol
- Known limitations

## App Structure

```
Home.py → Landing page

4 Pages:
├── 1. Interactive Map      - Visual exploration
├── 2. Scenario Compare     - Optimization algorithms ⭐
├── 3. Impact Analysis      - Detailed metrics
└── 4. Assumptions          - Methodology
```

## Demo Flow (8 min)

1. **Home** (1 min) - Show metrics
2. **Interactive Map** (2 min) - Click estates, filter districts
3. **Pareto Frontier** (2 min) - Explain multi-objective optimization
4. **Live Algorithm** (4 min) - Run greedy max-coverage, show convergence

**Showstopper:** Tab 3 in Scenario Compare - run the algorithm live!

## Algorithms Used

**Greedy Max-Coverage** (facility location)
- Used by: Amazon warehouses, UPS hubs, cell towers
- Guarantee: 63% of optimal (proven)
- Complexity: O(n² × k)

**Pareto Frontier Analysis** (multi-objective optimization)
- Used by: Portfolio optimization, engineering design
- Shows: Which scenarios represent true tradeoffs

## Documentation

**→ See [USER_GUIDE.md](USER_GUIDE.md) for complete documentation**

Includes:
- Page-by-page walkthrough
- Demo script (word-for-word)
- Q&A responses
- Technical details
- Troubleshooting

## What Makes This Innovative

- **Transparency** - Show the algorithm, not just results
- **Educational** - Users learn optimization while exploring
- **Interactive** - Tune parameters, see immediate results
- **Rigorous** - Industry-standard algorithms with proven guarantees
- **Real-world** - Same methods used by Amazon, UPS, telecom

**Not just a hackathon demo—a production-grade tool.**

## Files

```
control_tower/
├── Home.py                       # Entry point
├── pages/
│   ├── 1_Interactive_Map.py      # Estate map
│   ├── 2_Scenario_Compare.py     # Optimization (MAIN FEATURE)
│   ├── 3_Impact_Analysis.py      # Metrics
│   └── 4_Assumptions.py          # Methodology
├── backend/
│   ├── scenario_engine.py        # Scenario helpers
│   └── theme.py                  # Shared UI theme
├── data/
│   ├── scenarios.json            # Configs
│   └── scenario_outputs.json     # Results
├── precompute_scenarios.py       # Offline computation
├── requirements.txt              # Dependencies
├── README.md                     # This file
└── USER_GUIDE.md                 # Full documentation
```

## Dependencies

- `streamlit` - Web framework
- `pandas`, `numpy` - Data processing
- `scipy` - Distance calculations
- `plotly` - Interactive charts
- `folium`, `streamlit-folium` - Maps

## Troubleshooting

**Map legend not visible?**
Fixed in latest version (black text on semi-transparent background)

**Map flickering?**
Fixed with session state key

**Missing scipy?**
Run: `pip install scipy`

## For Judges

This tool demonstrates:
- Technical rigor (proven algorithms)
- Transparency (show the math)
- Innovation (interactive optimization)
- Real-world applicability (used by logistics companies)
- Educational value (teach users optimization concepts)

**Key differentiator:** We don't just recommend—we show HOW we optimize.

---

**Green Loop: Where Policy Meets Optimization Science**

Built for DataHack 2026 - The Green Loop Challenge

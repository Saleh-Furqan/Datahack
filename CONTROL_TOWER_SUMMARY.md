# Green Loop Control Tower - Summary

## Current Status: Demo-Ready (Validated Build)

Interactive optimization engine with live algorithms and transparent methodology.

## Quick Start

```bash
source venv/bin/activate
pip install -r control_tower/requirements.txt
python3 control_tower/precompute_scenarios.py
streamlit run control_tower/Home.py
```

Open http://localhost:8501

## What's Included

### Interactive Map
- Click estates for details
- Filter by district & distance
- Compare scenarios
- View hub locations

### Optimization Engine - MAIN FEATURE
- **Split-map comparison** (before/after)
- **Pareto frontier analysis** (multi-objective optimization)
- **Live greedy max-coverage algorithm** (run it yourself!)
- **Radar charts** (multi-dimensional view)

### Impact Analysis
- Coverage distributions
- District-level metrics
- Top beneficiaries
- Cost-benefit analysis

### Transparency
- Full methodology
- Validation protocol
- Known limitations

## Key Innovations

- **Live Algorithm Simulation** - Run greedy max-coverage yourself, see convergence
- **Pareto Frontier** - Multi-objective optimization showing true tradeoffs
- **Transparency** - Algorithm shown, not hidden
- **Industry Standard** - Same methods as Amazon, UPS, telecom

## Scenario Outputs

From `control_tower/data/scenario_outputs.json`:

| Scenario | Estates >500m | Burden % | Diversion (t/y) | Cost (HK$M) | Gini |
|----------|--------------|----------|-----------------|-------------|------|
| Baseline | 106 | 45.61% | 0 | 0 | 0.242 |
| Static Hubs | 83 | 32.28% | 3,361-5,882 | 60.0 | 0.203 |
| Mobile-First | 97 | 38.03% | 2,420-5,294 | 37.5 | 0.202 |
| Hybrid Equity | 87 | 32.73% | 3,025-5,882 | 56.25 | 0.172 |

## Algorithms

**Greedy Max-Coverage**
- Facility location (hub placement)
- 63% approximation guarantee
- O(n² × k) complexity
- Used by: Amazon, UPS, cell tower placement

**Pareto Frontier**
- Multi-objective optimization
- Identifies non-dominated solutions
- Shows genuine tradeoffs

## Documentation

**Main docs:** See `control_tower/README.md` and `control_tower/USER_GUIDE.md`

- README: Quick overview
- USER_GUIDE: Complete documentation with demo script

## Demo Showstopper

**Navigate to:** Scenario Compare → Tab 3: Live Greedy Algorithm

1. Set parameters (5 hubs, 500m radius)
2. Click "Run Optimization"
3. Watch algorithm execute step-by-step
4. See convergence chart and coverage map

**This is what separates us from other teams.**

## For Judges

Demonstrates:
- Technical rigor (proven algorithms)
- Transparency (show the math)
- Innovation (interactive optimization)
- Real-world applicability
- Educational value

**Key differentiator:** We don't just recommend—we show HOW.

---

**Green Loop: Where Policy Meets Optimization Science**

# Green Loop Control Tower

**Interactive Policy Dashboard for Hong Kong's Recycling Network**

DataHack 2026 Submission

---

## 🎯 What This Is

A data-driven policy simulator that compares **4 intervention strategies** for improving textile recycling access in Hong Kong's public housing estates.

**Not just static infrastructure planning** → **Dynamic operating system for recycling policy**

---

## 🚀 Quick Start

### Run Locally

```bash
# From project root
cd control_tower

# Install dependencies (if not already in main venv)
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### Run from Project Root

```bash
streamlit run control_tower/app.py
```

---

## 📊 Features

### 1. **Scenario Comparison**
Compare 4 intervention strategies:
- **Baseline**: Current state (no intervention)
- **Static Hubs**: 10 fixed multi-stream collection points
- **Mobile-First**: 3 trucks + 15 retrofits (lower capex, flexible)
- **Hybrid Equity**: 5 hubs + 2 trucks + 15 retrofits + incentives (balanced)

### 2. **Interactive Controls**
- **Budget Slider**: Adjust available funding (HK$0-80M)
- **Equity Priority**: Balance between total impact vs equal distribution
- **Real-time Updates**: Metrics recalculate as you adjust parameters

### 3. **Multi-View Analysis**
- **Overview**: Key metrics + scenario comparison
- **Map Details**: Geographic distribution with hub locations
- **Equity Analysis**: Burden metrics + Gini coefficient + beneficiaries
- **Assumptions**: Full transparency on model assumptions + sensitivity

### 4. **Validation Protocol**
Built-in 90-day pilot framework for real-world validation

---

## 📈 Key Metrics Tracked

**Primary:**
- Estates >500m from textile recycling
- Textile population burden (% residents >500m)
- Annual waste diversion (tonnes/year)
- Total cost (capex + 5yr opex)
- Payback period (years)

**Equity:**
- District Gini coefficient (inequality measure)
- Worst-quartile improvement
- Beneficiary estate count

---

## 🔧 How It Works

### Data Pipeline
```
1. Base Analysis (run_analysis.py)
   ↓
2. Scenario Precomputation (precompute_scenarios.py)
   ↓
3. Interactive Dashboard (app.py)
```

### Precomputation
All scenarios are computed **offline** from verified baseline data:
- `data/processed/baseline_metrics.json`
- `data/processed/impact_report.json`
- `data/processed/optimized_hubs.csv`
- `data/processed/estates_full_analysis.csv`

This ensures:
✅ Fast dashboard performance
✅ Reproducible results
✅ No real-time optimization complexity

---

## ⚠️ Important Notes

### Assumptions
**All intervention effects are MODELED ESTIMATES** requiring validation.

- New hub diversion: 0.8-1.5 tpd (±40% uncertainty)
- Mobile truck diversion: 1.2-2.0 tpd (±40% uncertainty)
- Retrofit diversion: 0.3-0.6 tpd (±40% uncertainty)

**We are transparent about uncertainty** → builds trust with judges.

### Validation Plan
90-day pilot protocol included to prove feasibility.

---

## 🎤 Demo Script

**For presentation:**

1. **Start with baseline** → show the problem (106 estates, 45.6% burden)
2. **Switch to Static Hubs** → show traditional approach
3. **Switch to Mobile-First** → show flexible alternative (lower cost)
4. **Switch to Hybrid Equity** → show balanced solution
5. **Adjust equity slider** → demonstrate tradeoff space
6. **Show assumptions panel** → demonstrate transparency
7. **End with validation plan** → show pragmatic implementation

**Total demo time: 3-4 minutes**

---

## 📁 File Structure

```
control_tower/
├── app.py                      # Main Streamlit dashboard
├── precompute_scenarios.py     # Offline scenario computation
├── scenarios.json              # Scenario configuration
├── scenario_outputs.json       # Precomputed metrics (generated)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🏆 Competition Alignment

### Innovation (20%)
✅ Dynamic policy simulator vs static infrastructure planning
✅ Interactive scenario comparison
✅ Equity-aware optimization

### Impact (30%)
✅ 4 actionable strategies with clear cost-benefit
✅ Pilot-first approach (90-day validation)
✅ Addresses real inequality (2.5× distance gap)

### Rigor (30%)
✅ Built on verified baseline analysis
✅ Transparent assumptions + sensitivity
✅ Reproducible methodology

### Presentation (20%)
✅ Interactive demo (judges can play with sliders)
✅ Clear visualizations
✅ Professional UI

---

## 👥 Team

- **Saleh Furqan**: Data analysis & strategy
- **Ibrahim Malik**: Visualization & presentation

---

## 📝 License

Educational/competition use only. Data from data.gov.hk.

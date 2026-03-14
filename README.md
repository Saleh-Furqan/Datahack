# The Complexity Lockout: Hong Kong's Hidden Recycling Crisis

**DataHack 2026 — The Green Loop Challenge**

## 🎯 The Problem

Hong Kong's recycling infrastructure creates a **double trap** for low-value waste:

1. **Market Failure**: Glass, textiles, and hazardous materials lack profitable collection incentives (5-11% recovery vs 92% for metals)
2. **Infrastructure Lockout**: 70-78% of collection points for these materials are locked inside private residential estates, inaccessible to the 2.2M public housing residents who need them most

**Result**: 731 tonnes/day of recyclable waste goes to landfill while residents walk 2.5-3.1× farther than private building occupants.

---

## 📊 Key Findings

### The "Trapped Waste" Trio

| Stream | Lockout Rate | Recovery Rate | Daily Landfill | Public Housing Impact |
|--------|--------------|---------------|----------------|----------------------|
| **Textiles** | 78% | 11% | 388 tpd | 106/241 estates >500m away |
| **Glass** | 76% | 5% | 211 tpd | 10/241 estates >500m away |
| **Hazardous** | 69% | 30% | 50 tpd | 17/241 estates >500m away |

### The Equity Gap

```
Public housing median distance to textile recycling:  440m
Private building median distance:                     175m
Equity multiplier:                                    2.5×
```

**106 out of 241 public housing estates** (1,031,670 residents) are >500m from public textile recycling—a distance proven to dramatically reduce participation.

---

## 💡 Our Solution: 10 Multi-Stream Micro-Hubs

### The Innovation

Instead of expensive single-location GREEN@ stations (HK$20-30M each), we propose **10 strategically placed micro-hubs** using greedy max-coverage optimization:

**Hub Locations** (see [optimized_hubs.csv](data/processed/optimized_hubs.csv)):

| # | Location | District | Catchment (800m) |
|---|----------|----------|------------------|
| 1 | Po Tat Estate | Kwun Tong | 100,980 residents |
| 2 | Cheung Shan Estate | Tsuen Wan | 50,220 residents |
| 3 | Wing Cheong Estate | Sham Shui Po | 58,590 residents |
| 4 | Wah Fu (I) Estate | Southern | 26,730 residents |
| 5 | Wang Tau Hom Estate | Wong Tai Sin | 73,980 residents |
| 6 | Queens Hill Estate | North | 24,030 residents |
| 7 | Ying Tung Estate | Islands | 22,680 residents |
| 8 | Wo Che Estate | Sha Tin | 29,970 residents |
| 9 | Wan Tau Tong Estate | Tai Po | 18,900 residents |
| 10 | Tak Long Estate | Kowloon City | 80,190 residents |

**Total Coverage**: 486,270 residents within walkable distance (800m)

### Impact Metrics

**Textiles** (biggest improvement):
- Before: 106 estates >500m
- After: 83 estates >500m
- **23 estates improved**, **266,220 residents saved**
- Median distance: 440m → 366m (-17%)

**Combined Impact**:
- 13,300–26,700 tonnes/year diverted from landfill
- HK$4.9–9.7M/year in landfill gate fee savings
- **Payback period: 2.1–10.3 years**

### Cost Comparison

| Option | Capital Cost | Coverage | Cost per Resident |
|--------|--------------|----------|-------------------|
| 1 GREEN@ station | HK$20-30M | ~50K residents | HK$400-600 |
| 10 Micro-hubs | HK$20-50M | 486K residents | HK$41-103 |
| **Our advantage** | **Same budget** | **10× coverage** | **5-10× efficiency** |

---

## 🗂️ Repository Structure

```
datahack/
├── run_analysis.py                          # Complete analysis pipeline
├── data/
│   ├── raw/
│   │   ├── collection_points.csv            # 8,858 recycling points
│   │   └── public_housing.json              # 241 estates, 2.2M residents
│   └── processed/
│       ├── baseline_metrics.json            # Current state per stream
│       ├── optimized_hubs.csv               # 10 hub locations + metadata
│       ├── estates_full_analysis.csv        # Per-estate per-stream distances
│       └── impact_report.json               # Before/after + cost-benefit
├── visualizations/
│   ├── 01_landfill_composition.png          # MSW breakdown + lockout paradox
│   ├── 02_stream_inequality.png             # Public vs private equity gap
│   ├── 03_textiles_deep_dive.png            # Textiles by district
│   ├── 04_hub_impact.png                    # Before/after comparison
│   └── 05_interactive_map.html              # Full interactive visualization
├── README.md                                # This file
├── FINAL_STRATEGY.md                        # Complete strategic rationale
├── NEXT_STEPS.md                            # Tasks for presentation prep
└── STATUS.md                                # Current progress
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment with dependencies (see [requirements.txt](requirements.txt))

### Run Analysis

```bash
# Activate environment
source venv/bin/activate

# Run complete pipeline
python run_analysis.py

# Outputs:
# - 4 processed data files in data/processed/
# - 5 visualizations in visualizations/
# - Console summary with key metrics
```

### Analysis Pipeline

**Phase 1 — Analyze & Uncover**: Calculate per-stream lockout rates, equity gaps, and baseline accessibility

**Phase 2 — Innovate & Propose**: Greedy max-coverage algorithm to place 10 hubs optimally

**Phase 3 — Justify & Measure**: Before/after impact quantification + cost-benefit analysis

---

## 📈 Data Sources

All datasets from [data.gov.hk](https://data.gov.hk):

1. **Recyclable Collection Points** (8,858 points) - waste type, location, accessibility
2. **Public Housing Estates** (241 estates) - location, population, district
3. Additional geo datasets (optional): private buildings, GREEN@ stations, waste facilities

---

## 🎤 Presentation Hook

> "Hong Kong has 8,858 recycling points. Sounds great, right?
>
> But 78% of textile recycling is locked behind private estate gates.
>
> Result: Over 1 million public housing residents walk 2.5× farther than their wealthy neighbors—and 388 tonnes of textiles go to landfill every day.
>
> We found a solution: 10 micro-hubs for the same cost as 1 GREEN@ station, but serving 10× more people."

---

## 👥 Team

- **Saleh Furqan** - Data analysis & strategy
- **Ibrahim Malik** - Visualization & presentation

**Competition**: DataHack 2026 — The Green Loop Challenge
**Submission Date**: March 2026

---

## 📝 License

This analysis uses open government data and is created for educational/competition purposes.

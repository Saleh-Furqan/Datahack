# DataHack 2026: Hidden Inequality in Recycling Access

## Project Overview

This repository contains our team's submission for CUHK DataHack 2026, analyzing **Hong Kong's recycling infrastructure** through spatial data science.

**Key Finding:** While Hong Kong's 8,858 recycling collection points provide excellent nominal coverage (median 27m), 40% are access-restricted (residents/staff only), creating hidden inequality for specific communities.

## UN Sustainable Development Goals

- **SDG 11**: Sustainable Cities and Communities
- **SDG 12**: Responsible Consumption and Production

## Our Discovery

### The Open-Access Gap

**Two-Scenario Analysis:**
1. **All Points (8,858):** Median distance 27m - appears world-class
2. **Public-Access Only (5,301):** Median distance 39m - still excellent
3. **System-wide penalty:** +12m (modest)

**BUT:** 15 specific estates face severe "Openness Penalties" of 80-220 meters when restricted points are excluded, revealing hidden inequality within nominal coverage.

### Our Solution

Targeted placement of 10-15 public micro-hubs for high-penalty estates to eliminate accessibility inequality at estimated cost of $50-150K.

## Repository Structure

```
datahack/
├── data/
│   ├── raw/            # Downloaded datasets
│   └── processed/      # Analysis outputs
├── visualizations/     # Charts, maps, and figures
├── docs/               # Strategy and documentation
├── scripts/            # Data download & validation
└── run_public_access_analysis.py  # Main analysis script
```

## Datasets Used

- **Recyclable Collection Points Data** (8,858 points)
  - Includes `accessibilty_notes` field (public vs restricted)
  - 5,301 public-access, 3,557 restricted
- **Public Housing Estates** (241 estates)
  - ~2.2 million residents (29% of HK population)
  - Full coordinates and population data

## Evaluation Criteria

Our project addresses:

1. **Innovation & Originality (20%)** - Discovered public vs restricted access distinction
2. **Impact & Practical Feasibility (30%)** - Targeted, cost-effective solution for inequality
3. **Analytical Rigor & Data Competency (30%)** - Two-scenario comparison, openness penalty metric
4. **Presentation & Collaboration (20%)** - Honest, nuanced storytelling

## Team Members

- Saleh Furqan
- Ibrahim Malik (vxibrahimmalikxv@gmail.com)

## Getting Started

### Setup

```bash
# Clone the repository
git clone https://github.com/Saleh-Furqan/Datahack.git
cd Datahack

# Activate virtual environment
source venv/bin/activate

# Run the analysis
python3 run_public_access_analysis.py
```

### View Results

- **Visualizations:** `visualizations/open_access_gap.png`
- **Interactive Map:** `visualizations/access_gap_map.html`
- **Data:** `data/processed/estates_access_gap.csv`
- **Stats:** `data/processed/access_gap_stats.json`

### Key Files

- **[FINAL_STRATEGY.md](FINAL_STRATEGY.md)** - Complete project overview and rationale
- **[STATUS.md](STATUS.md)** - Current progress and next steps
- **`run_public_access_analysis.py`** - Main two-scenario analysis script

## Progress Tracker

- [x] Data collection and preprocessing
- [x] Exploratory data analysis
- [x] Two-scenario spatial analysis (all vs public-only)
- [x] Openness Penalty calculation for all estates
- [x] High-penalty estate identification (top 15)
- [x] Visualization development
- [ ] Targeted hub placement for high-penalty estates
- [ ] Final presentation preparation

## Key Results

### The Numbers

- **40.2%** of collection points are access-restricted
- **+12m** median penalty system-wide (modest)
- **15 estates** with severe penalties (80-222m)
- **~50,000 residents** affected by severe inequality
- **10-15 hubs** needed to eliminate penalties

### Top 5 High-Penalty Estates

1. Hing Tin Estate: +222m penalty (17m → 239m)
2. Wah Kwai Estate: +185m penalty (2m → 187m)
3. Fung Wah Estate: +165m penalty (75m → 240m)
4. Kwai Hing Estate: +138m penalty (5m → 143m)
5. Yung Shing Court: +131m penalty (38m → 169m)

## Resources

- [Competition Details](https://libguides.lib.cuhk.edu.hk/datahack/2026-data)
- [Evaluation Criteria](https://libguides.lib.cuhk.edu.hk/datahack)
- [DATA.GOV.HK](https://data.gov.hk/en/)

## License

MIT License - Educational Use

---

**Last Updated**: March 13, 2026

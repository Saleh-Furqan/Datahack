# DataHack 2026 - Open-Access Gap in Hong Kong Recycling

This repository contains our CUHK DataHack 2026 analysis of recycling accessibility in Hong Kong.

## Current Verified Finding (March 13, 2026)

- Total collection points analyzed: **8,858**
- Public-access points: **5,301 (59.8%)**
- Access-restricted points: **3,557 (40.2%)**
- Median nearest distance to a point:
  - All points: **27m**
  - Public-only points: **39m**
  - Median penalty: **+12m**
- Estates with severe openness penalty (>=80m): **16 estates**
- Population proxy in severe-penalty estates: **31,590 residents**

## Quick Start (Teammates)

```bash
git clone https://github.com/Saleh-Furqan/Datahack.git
cd Datahack

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 1) Download required raw datasets

Run:

```bash
python3 scripts/download_data.py
```

Then manually download and place these files in `data/raw/`:

- `collection_points.csv`
- `public_housing.json`

### 2) Validate data

```bash
python3 scripts/validate_data.py
```

### 3) Run analysis

```bash
python3 run_public_access_analysis.py
```

## Outputs

After running analysis:

- `data/processed/estates_access_gap.csv`
- `data/processed/access_gap_stats.json`
- `visualizations/open_access_gap.png`
- `visualizations/access_gap_map.html`

## Repository Layout

```text
data/
  raw/                  # Local downloaded datasets (not committed)
  processed/            # Committed analysis outputs
scripts/
  download_data.py
  validate_data.py
run_public_access_analysis.py
visualizations/
docs/
```

## Team Workflow

```bash
git checkout -b <feature-name>
# make changes
git add .
git commit -m "Describe change"
git push -u origin <feature-name>
```

Then open a PR to `main` so everyone can review.

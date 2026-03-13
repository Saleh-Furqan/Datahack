# Next Steps for Team Collaboration

## 1) Pull latest `main`

```bash
git checkout main
git pull origin main
```

## 2) Set up local environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3) Ensure required data exists

Required files under `data/raw/`:

- `collection_points.csv`
- `public_housing.json`

Run:

```bash
python3 scripts/validate_data.py
```

## 4) Re-run baseline analysis

```bash
python3 run_public_access_analysis.py
```

Expected outputs:

- `data/processed/estates_access_gap.csv`
- `data/processed/access_gap_stats.json`
- `visualizations/open_access_gap.png`
- `visualizations/access_gap_map.html`

## 5) Split team work

- Person A: Build top-15 hub placement proposal (`proposed_hubs.csv` + map layer).
- Person B: Build final deck and pull charts/maps from `visualizations/`.
- Both: Practice final pitch and Q&A.

## 6) Collaboration rule

Use short feature branches and PRs so changes do not collide:

```bash
git checkout -b feature/<name>
git add .
git commit -m "..."
git push -u origin feature/<name>
```

# Data Directory

## Structure

- `raw/` local downloaded source datasets (not committed)
- `processed/` generated outputs used by the team (committed)

## Required Raw Files for Current Pipeline

Place these in `data/raw/`:

1. `collection_points.csv`
2. `public_housing.json`

Use `python3 scripts/download_data.py` for source URLs and naming guidance.

## Validation

Run:

```bash
python3 scripts/validate_data.py
```

Validation report will be written to:

- `data/validation_report.json`

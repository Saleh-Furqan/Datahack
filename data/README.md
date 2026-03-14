# Data Directory

## Structure

- `raw/` local downloaded source datasets (not committed)
- `geo/` optional geospatial sources (gml/gdb/geojson/shp)
- `processed/` generated outputs used by the team (committed)

## Required Raw Files for Current Pipeline

Place these in `data/raw/`:

1. `collection_points.csv`
2. `public_housing.json`

Use `python3 scripts/download_data.py` for source URLs and naming guidance.

Optional for private-vs-public comparator metrics:

- `raw/private_buildings.csv` or `raw/private_buildings.json`
- `geo/private_buildings/*` (gml/geojson/gpkg/shp)

## Validation

Run:

```bash
python3 scripts/validate_data.py
```

Validation report will be written to:

- `data/validation_report.json`

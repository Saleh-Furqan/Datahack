#!/usr/bin/env python3
"""
Data validation script for DataHack 2026
Checks that downloaded datasets are ready for analysis
"""

import pandas as pd
from pathlib import Path
import json
import re

data_dir = Path(__file__).parent.parent / 'data' / 'raw'

print("DataHack 2026 - Data Validation Script")
print("=" * 50)

# Hong Kong coordinate boundaries
HK_LAT_MIN, HK_LAT_MAX = 22.15, 22.58
HK_LON_MIN, HK_LON_MAX = 113.83, 114.41

validation_results = {}

LAT_ALIASES = {
    "latitude",
    "lat",
    "y",
    "northing",
}

LON_ALIASES = {
    "longitude",
    "lon",
    "lng",
    "lgt",
    "x",
    "easting",
}


def normalize_column_name(name):
    """Normalize column names for robust matching across datasets."""
    if name is None:
        return ""
    text = str(name).replace("\ufeff", "").strip().lower()
    return re.sub(r"[^a-z0-9]", "", text)


def find_matching_column(columns, aliases):
    """Return the first column whose normalized name matches an alias."""
    normalized = {normalize_column_name(col): col for col in columns}
    for alias in aliases:
        match = normalized.get(normalize_column_name(alias))
        if match:
            return match
    return None


def resolve_coordinate_columns(columns, preferred_lat=None, preferred_lon=None):
    """Resolve coordinate columns from common naming variants."""
    lat_aliases = set(LAT_ALIASES)
    lon_aliases = set(LON_ALIASES)

    if preferred_lat:
        lat_aliases.add(preferred_lat)
    if preferred_lon:
        lon_aliases.add(preferred_lon)

    lat_col = find_matching_column(columns, lat_aliases)
    lon_col = find_matching_column(columns, lon_aliases)
    return lat_col, lon_col

def validate_coordinates(df, lat_col, lon_col, dataset_name):
    """Validate that coordinates are within Hong Kong bounds"""
    issues = []

    if lat_col not in df.columns or lon_col not in df.columns:
        return [f"Missing coordinate columns: {lat_col}, {lon_col}"]

    # Check for missing values
    missing_lat = df[lat_col].isna().sum()
    missing_lon = df[lon_col].isna().sum()
    if missing_lat > 0 or missing_lon > 0:
        issues.append(f"Missing coordinates: {missing_lat} lat, {missing_lon} lon")

    # Check bounds
    valid_df = df.dropna(subset=[lat_col, lon_col])
    if len(valid_df) > 0:
        out_of_bounds = (
            (valid_df[lat_col] < HK_LAT_MIN) | (valid_df[lat_col] > HK_LAT_MAX) |
            (valid_df[lon_col] < HK_LON_MIN) | (valid_df[lon_col] > HK_LON_MAX)
        ).sum()

        if out_of_bounds > 0:
            issues.append(f"Coordinates out of HK bounds: {out_of_bounds} rows")

    return issues

def check_file(filename, expected_cols=None, lat_col=None, lon_col=None):
    """Check if file exists and has required structure"""
    filepath = data_dir / filename

    result = {
        "exists": False,
        "readable": False,
        "row_count": 0,
        "columns": [],
        "coordinate_columns": {},
        "issues": []
    }

    if not filepath.exists():
        result["issues"].append("File not found")
        return result

    result["exists"] = True

    try:
        # Try reading as CSV
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.json'):
            df = pd.read_json(filepath)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            result["issues"].append(f"Unknown file format: {filename}")
            return result

        result["readable"] = True
        result["row_count"] = len(df)
        result["columns"] = list(df.columns)

        # Check for expected columns (normalized match)
        if expected_cols:
            normalized_columns = {normalize_column_name(col) for col in df.columns}
            missing_cols = [
                col for col in expected_cols
                if normalize_column_name(col) not in normalized_columns
            ]
            if missing_cols:
                result["issues"].append(f"Missing expected columns: {set(missing_cols)}")

        # Validate coordinates with flexible column matching
        resolved_lat, resolved_lon = resolve_coordinate_columns(df.columns, lat_col, lon_col)
        if resolved_lat and resolved_lon:
            result["coordinate_columns"] = {"lat": resolved_lat, "lon": resolved_lon}
            coord_issues = validate_coordinates(df, resolved_lat, resolved_lon, filename)
            result["issues"].extend(coord_issues)
        elif lat_col or lon_col:
            result["issues"].append(
                "Missing coordinate columns (accepted aliases: latitude/lat and longitude/lon/lgt)"
            )

        # Check for duplicates
        if len(df) != len(df.drop_duplicates()):
            dup_count = len(df) - len(df.drop_duplicates())
            result["issues"].append(f"Duplicate rows: {dup_count}")

    except Exception as e:
        result["issues"].append(f"Error reading file: {str(e)}")

    return result

# Define expected structure for each dataset
datasets_to_check = {
    "recycling_stations.csv": {
        "expected_cols": [],
        "lat_col": "Latitude",
        "lon_col": "Longitude",
        "priority": "CRITICAL"
    },
    "collection_points.csv": {
        "expected_cols": [],
        "lat_col": "Latitude",
        "lon_col": "Longitude",
        "priority": "CRITICAL"
    },
    "public_housing.csv": {
        "expected_cols": [],
        "lat_col": "Latitude",
        "lon_col": "Longitude",
        "priority": "CRITICAL"
    },
    "private_buildings.csv": {
        "expected_cols": ["District"],  # May not have coordinates
        "lat_col": None,
        "lon_col": None,
        "priority": "IMPORTANT"
    }
}

print("\nValidating datasets...\n")

critical_ready = True
for filename, spec in datasets_to_check.items():
    print(f"[{spec['priority']}] {filename}")
    result = check_file(filename, spec["expected_cols"],
                       spec.get("lat_col"), spec.get("lon_col"))

    validation_results[filename] = result

    if result["exists"]:
        print(f"  ✓ File exists")
    else:
        print(f"  ✗ File not found")
        if spec['priority'] == 'CRITICAL':
            critical_ready = False

    if result["readable"]:
        print(f"  ✓ Readable ({result['row_count']} rows)")
        print(f"  Columns: {', '.join(result['columns'][:5])}...")
        if result["coordinate_columns"]:
            print(
                f"  ✓ Coordinate columns detected: "
                f"{result['coordinate_columns']['lat']}, {result['coordinate_columns']['lon']}"
            )
    elif result["exists"]:
        print(f"  ✗ Cannot read file")
        if spec['priority'] == 'CRITICAL':
            critical_ready = False

    if result["issues"]:
        for issue in result["issues"]:
            print(f"  ⚠ {issue}")

    print()

print("=" * 50)
print("VALIDATION SUMMARY")
print("=" * 50)

if critical_ready:
    print("✓ All CRITICAL datasets ready")
    print("You can proceed to data cleaning phase")
    print("\nNext step: Open notebooks/02_data_cleaning.ipynb")
else:
    print("✗ CRITICAL datasets missing or have issues")
    print("\nOPTIONS:")
    print("1. Fix the issues listed above")
    print("2. PIVOT to Public Housing Only mode")
    print("   - Focus analysis on just public housing + recycling points")
    print("   - Still high impact (45% of HK population)")
    print("   - Simpler, faster analysis")

print("\n" + "=" * 50)

# Save validation report
report_path = data_dir.parent / 'validation_report.json'
with open(report_path, 'w') as f:
    json.dump(validation_results, f, indent=2)
print(f"\nValidation report saved to: {report_path}")

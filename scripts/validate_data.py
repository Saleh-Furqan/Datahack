#!/usr/bin/env python3
"""
Validate local datasets needed for the current analysis pipeline.

Required inputs:
  - data/raw/collection_points.csv
  - data/raw/public_housing.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "raw"
REPORT_PATH = ROOT / "data" / "validation_report.json"

HK_BOUNDS = {
    "lat_min": 22.0,
    "lat_max": 22.7,
    "lon_min": 113.7,
    "lon_max": 114.6,
}


def parse_flat_count(value: object) -> int | None:
    """Extract rental-flat integer from values like '1 000 * as at 31.12.2025'."""
    if isinstance(value, dict):
        value = value.get("en") or value.get("zh-Hant") or value.get("zh-Hans")
    if not isinstance(value, str):
        return None

    head = value.split("as at")[0]
    match = re.search(r"\d[\d ,]*", head)
    if not match:
        return None

    digits = re.sub(r"[^\d]", "", match.group(0))
    return int(digits) if digits else None


def validate_collection_points(path: Path) -> dict:
    report = {
        "exists": path.exists(),
        "readable": False,
        "row_count": 0,
        "columns": [],
        "issues": [],
        "public_access_points": 0,
        "restricted_points": 0,
        "invalid_coordinate_rows": 0,
        "out_of_hk_bounds_rows": 0,
    }

    if not path.exists():
        report["issues"].append("File not found")
        return report

    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except Exception as exc:  # pragma: no cover - defensive
        report["issues"].append(f"Unable to read CSV: {exc}")
        return report

    report["readable"] = True
    report["row_count"] = int(len(df))
    report["columns"] = [str(c) for c in df.columns]

    required_cols = {"lat", "lgt", "accessibilty_notes"}
    missing_cols = sorted(required_cols - set(df.columns))
    if missing_cols:
        report["issues"].append(
            f"Missing required columns: {', '.join(missing_cols)}"
        )
        return report

    lat = pd.to_numeric(df["lat"], errors="coerce")
    lon = pd.to_numeric(df["lgt"], errors="coerce")
    invalid_mask = lat.isna() | lon.isna()
    report["invalid_coordinate_rows"] = int(invalid_mask.sum())

    in_bounds_mask = (
        (lat >= HK_BOUNDS["lat_min"])
        & (lat <= HK_BOUNDS["lat_max"])
        & (lon >= HK_BOUNDS["lon_min"])
        & (lon <= HK_BOUNDS["lon_max"])
    )
    out_of_bounds_mask = (~invalid_mask) & (~in_bounds_mask)
    report["out_of_hk_bounds_rows"] = int(out_of_bounds_mask.sum())

    access = df["accessibilty_notes"].fillna("").astype(str)
    public_mask = access.str.contains("For public use", case=False, na=False)
    report["public_access_points"] = int(public_mask.sum())
    report["restricted_points"] = int((~public_mask).sum())

    if report["row_count"] == 0:
        report["issues"].append("No rows found")
    if report["invalid_coordinate_rows"] > 0:
        report["issues"].append(
            f"Invalid coordinates: {report['invalid_coordinate_rows']} rows"
        )
    if report["out_of_hk_bounds_rows"] > 0:
        report["issues"].append(
            f"Coordinates out of HK bounds: {report['out_of_hk_bounds_rows']} rows"
        )
    if report["public_access_points"] == 0:
        report["issues"].append("No public-access points detected")

    return report


def validate_public_housing_json(path: Path) -> dict:
    report = {
        "exists": path.exists(),
        "readable": False,
        "row_count": 0,
        "issues": [],
        "invalid_coordinate_rows": 0,
        "flats_parse_fail_rows": 0,
        "population_proxy_total": 0,
    }

    if not path.exists():
        report["issues"].append("File not found")
        return report

    try:
        with path.open() as f:
            data = json.load(f)
    except Exception as exc:  # pragma: no cover - defensive
        report["issues"].append(f"Unable to read JSON: {exc}")
        return report

    if not isinstance(data, list):
        report["issues"].append("Expected a JSON list of estates")
        return report

    report["readable"] = True
    report["row_count"] = len(data)
    if report["row_count"] == 0:
        report["issues"].append("No rows found")
        return report

    invalid_coord = 0
    parse_fail = 0
    pop_total = 0
    for row in data:
        try:
            lat = float(row.get("Estate Map Latitude"))
            lon = float(row.get("Estate Map Longitude"))
        except Exception:
            lat, lon = None, None

        if lat is None or lon is None:
            invalid_coord += 1
        else:
            in_bounds = (
                HK_BOUNDS["lat_min"] <= lat <= HK_BOUNDS["lat_max"]
                and HK_BOUNDS["lon_min"] <= lon <= HK_BOUNDS["lon_max"]
            )
            if not in_bounds:
                invalid_coord += 1

        flats = parse_flat_count(row.get("No. of Rental Flats"))
        if flats is None:
            parse_fail += 1
        else:
            pop_total += int(flats * 2.7)

    report["invalid_coordinate_rows"] = int(invalid_coord)
    report["flats_parse_fail_rows"] = int(parse_fail)
    report["population_proxy_total"] = int(pop_total)

    if report["invalid_coordinate_rows"] > 0:
        report["issues"].append(
            f"Invalid/out-of-bounds coordinates: {report['invalid_coordinate_rows']} rows"
        )
    if report["flats_parse_fail_rows"] > 0:
        report["issues"].append(
            f"Could not parse rental flats: {report['flats_parse_fail_rows']} rows"
        )

    return report


def optional_file_status(path: Path) -> dict:
    return {
        "exists": path.exists(),
        "readable": path.exists(),
        "issues": [] if path.exists() else ["File not found (optional)"],
    }


def main() -> int:
    print("DataHack 2026 - Data Validation")
    print("=" * 50)

    results = {
        "collection_points.csv": validate_collection_points(
            RAW_DIR / "collection_points.csv"
        ),
        "public_housing.json": validate_public_housing_json(
            RAW_DIR / "public_housing.json"
        ),
        "recycling_stations.csv": optional_file_status(RAW_DIR / "recycling_stations.csv"),
        "private_buildings.csv": optional_file_status(RAW_DIR / "private_buildings.csv"),
        "private_buildings.json": optional_file_status(RAW_DIR / "private_buildings.json"),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w") as f:
        json.dump(results, f, indent=2)

    required = ["collection_points.csv", "public_housing.json"]
    has_required_failure = False

    for name, status in results.items():
        issues = status.get("issues", [])
        if name in required:
            valid = status.get("exists") and status.get("readable") and not issues
            label = "PASS" if valid else "FAIL"
            if not valid:
                has_required_failure = True
        else:
            label = "OK" if status.get("exists") else "SKIP"

        print(f"[{label}] {name}")
        if status.get("exists"):
            row_count = status.get("row_count")
            if row_count is not None:
                print(f"  Rows: {row_count:,}")
        for issue in issues:
            print(f"  - {issue}")

    print("\nReport saved to data/validation_report.json")
    if has_required_failure:
        print("Validation failed for required datasets.")
        return 1

    print("Required datasets validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Shared data-loading utilities for the Green Loop Control Tower."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CONTROL_TOWER = ROOT / "control_tower"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_RAW = ROOT / "data" / "raw"
CT_DATA = CONTROL_TOWER / "data"
CT_ASSETS = CONTROL_TOWER / "assets"

STREAM_FILTERS = {
    "glass": "Glass Bottles",
    "textiles": "Clothes",
    "hazardous": "Fluorescent Lamp",
    "batteries": "Rechargeable Batteries",
    "ewaste": "Small Electrical and Electronic Equipment",
}


def _read_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def load_scenario_outputs() -> dict[str, Any]:
    return _read_json(CT_DATA / "scenario_outputs.json")


def load_baseline_metrics() -> dict[str, Any]:
    return _read_json(DATA_PROCESSED / "baseline_metrics.json")


def load_impact_report() -> dict[str, Any]:
    return _read_json(DATA_PROCESSED / "impact_report.json")


def load_estates() -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / "estates_full_analysis.csv")


def load_hubs() -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / "optimized_hubs.csv")


def load_collection_points(public_only: bool = True) -> pd.DataFrame:
    points = pd.read_csv(DATA_RAW / "collection_points.csv", encoding="utf-8-sig")
    points = points.rename(columns={"lgt": "lon"})
    points["waste_type"] = points["waste_type"].fillna("")
    points["accessibilty_notes"] = points["accessibilty_notes"].fillna("")

    points = points[pd.to_numeric(points["lat"], errors="coerce").notna()]
    points = points[pd.to_numeric(points["lon"], errors="coerce").notna()]
    points["lat"] = points["lat"].astype(float)
    points["lon"] = points["lon"].astype(float)

    if public_only:
        points = points[points["accessibilty_notes"].str.contains("For public use", case=False, na=False)]

    return points.reset_index(drop=True)


def stream_points(points: pd.DataFrame, stream_key: str) -> pd.DataFrame:
    pattern = STREAM_FILTERS[stream_key]
    return points[points["waste_type"].str.contains(pattern, case=False, na=False)].copy()


def load_district_geojson() -> dict[str, Any] | None:
    geo_path = CT_ASSETS / "hk_districts.geojson"
    if not geo_path.exists():
        return None
    return _read_json(geo_path)


def load_optional_points_csv(name: str) -> pd.DataFrame | None:
    """Load optional raw CSV if present (e.g., recycling_stations.csv)."""
    path = DATA_RAW / name
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path)
    return df

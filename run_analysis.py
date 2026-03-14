#!/usr/bin/env python3
"""
DataHack 2026 - Complexity Lockout Analysis (Approach 2)

This pipeline is designed to be:
1) Methodologically explicit
2) Reproducible end-to-end
3) Presentation-ready with clean visual outputs
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
GEO = ROOT / "data" / "geo"
OUT = ROOT / "data" / "processed"
VIZ = ROOT / "visualizations"

for folder in (OUT, VIZ):
    folder.mkdir(parents=True, exist_ok=True)

CACHE = ROOT / ".cache" / "matplotlib"
CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(CACHE))

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

try:
    import geopandas as gpd

    HAS_GEO = True
except ImportError:
    HAS_GEO = False

try:
    import folium

    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False


EARTH_R_M = 6_371_000.0
HK_BOUNDS = {"lat_min": 22.0, "lat_max": 22.7, "lon_min": 113.7, "lon_max": 114.6}

NUM_HUBS = 10
HUB_SERVICE_RADIUS_M = 800
UNDERSERVED_THRESHOLD_M = 500
HUB_MIN_SEPARATION_M = 700

MULTISTREAM_SCORE_WEIGHT = 0.35
TEXTILE_RESCUE_WEIGHT = 0.55
EQUITY_BONUS_WEIGHT = 0.10

CAPEX_PER_HUB_MIN = 2_000_000  # HKD
CAPEX_PER_HUB_MAX = 5_000_000  # HKD
LANDFILL_GATE_FEE_HKD_PER_TONNE = 365

# Fraction of previously underserved unrecovered waste captured after access improvement.
CAPTURE_FACTOR_LOW = 0.20
CAPTURE_FACTOR_HIGH = 0.35


STREAMS: Dict[str, Dict[str, Any]] = {
    "glass": {
        "pattern": "Glass Bottles",
        "label": "Glass",
        "tpd": 211,
        "recovery_pct": 5,
        "color": "#FB8C00",
    },
    "textiles": {
        "pattern": "Clothes",
        "label": "Textiles",
        "tpd": 388,
        "recovery_pct": 11,
        "color": "#D81B60",
    },
    "hazardous": {
        "pattern": "Fluorescent Lamp",
        "label": "Hazardous",
        "tpd": 50,
        "recovery_pct": 30,
        "color": "#8E24AA",
    },
    "batteries": {
        "pattern": "Rechargeable Batteries",
        "label": "Batteries",
        "tpd": 40,
        "recovery_pct": 30,
        "color": "#FBC02D",
    },
    "ewaste": {
        "pattern": "Small Electrical and Electronic Equipment",
        "label": "E-waste",
        "tpd": 42,
        "recovery_pct": 45,
        "color": "#3949AB",
    },
}

ALL_STREAM_PATTERNS = {
    "Metals": "Metals",
    "Paper": "Paper",
    "Plastics": "Plastics",
    "Glass": "Glass Bottles",
    "Food Waste": "Food Waste",
    "Textiles": "Clothes",
    "Batteries": "Rechargeable Batteries",
    "Hazardous": "Fluorescent Lamp",
    "E-waste": "Small Electrical",
    "Cartons": "Beverage Cartons",
}

MSW_COMPOSITION_TPD = {
    "Food Waste": 3495,
    "Plastics": 2369,
    "Paper": 2244,
    "Textiles": 388,
    "Metals": 248,
    "Glass": 211,
    "Wood": 207,
    "Household Hazardous": 132,
    "Others": 1834,
}

RECOVERY_REFERENCE = {
    "Food Waste": 3,
    "Paper": 43,
    "Plastics": 11,
    "Metals": 92,
    "Glass": 5,
    "Textiles": 11,
    "Household Hazardous": 30,
}


def set_plot_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D4D9E2",
            "axes.linewidth": 0.9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#E9EDF3",
            "grid.linewidth": 0.8,
            "grid.alpha": 0.85,
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.labelcolor": "#23313F",
            "xtick.color": "#4E5D6C",
            "ytick.color": "#4E5D6C",
            "legend.frameon": False,
            "savefig.facecolor": "white",
        }
    )


THEME = {
    "text_dark": "#1F2937",
    "text_muted": "#607080",
    "accent": "#C2185B",
    "accent_alt": "#1D4ED8",
    "good": "#2E7D32",
    "warn": "#D1495B",
    "neutral": "#AAB7C4",
    "bg_soft": "#F8FAFC",
}


def fmt_int(value: float) -> str:
    return f"{int(round(value)):,}"


def fmt_k(value: float) -> str:
    abs_v = abs(value)
    if abs_v >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs_v >= 1_000:
        return f"{value / 1_000:.1f}k"
    return f"{value:.0f}"


def haversine_min(
    lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray
) -> np.ndarray:
    """Nearest-neighbor distance from each point in set 1 to set 2."""
    if len(lat2) == 0:
        return np.full(len(lat1), np.inf, dtype=float)
    la1 = np.radians(lat1)[:, None]
    lo1 = np.radians(lon1)[:, None]
    la2 = np.radians(lat2)[None, :]
    lo2 = np.radians(lon2)[None, :]
    dlat = la2 - la1
    dlon = lo2 - lo1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(la1) * np.cos(la2) * np.sin(dlon / 2.0) ** 2
    return (2.0 * EARTH_R_M * np.arcsin(np.sqrt(a))).min(axis=1)


def detect_lat_lon_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    lat_candidates = [
        "lat",
        "latitude",
        "y",
        "estate map latitude",
    ]
    lon_candidates = [
        "lon",
        "lng",
        "lgt",
        "longitude",
        "x",
        "estate map longitude",
    ]

    normalized = {str(c).strip().lower(): c for c in df.columns}

    lat_col = next((normalized[c] for c in lat_candidates if c in normalized), None)
    lon_col = next((normalized[c] for c in lon_candidates if c in normalized), None)
    return lat_col, lon_col


def parse_flats(value: object) -> Optional[int]:
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


def filter_hk_bounds(df: pd.DataFrame, lat_col: str, lon_col: str) -> pd.DataFrame:
    mask = (
        (df[lat_col] >= HK_BOUNDS["lat_min"])
        & (df[lat_col] <= HK_BOUNDS["lat_max"])
        & (df[lon_col] >= HK_BOUNDS["lon_min"])
        & (df[lon_col] <= HK_BOUNDS["lon_max"])
    )
    return df.loc[mask].copy()


def load_district_vulnerability_override() -> Optional[pd.DataFrame]:
    """
    Optional override file for district vulnerability.

    Expected file: data/raw/district_vulnerability.csv
    Expected columns (case-insensitive):
      - district
      - vulnerability_score  (0 to 1)
    """
    path = RAW / "district_vulnerability.csv"
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return None

    normalized = {str(c).strip().lower(): c for c in df.columns}
    if "district" not in normalized or "vulnerability_score" not in normalized:
        return None

    district_col = normalized["district"]
    score_col = normalized["vulnerability_score"]
    out = df[[district_col, score_col]].copy()
    out.columns = ["district", "vulnerability_score"]
    out["district"] = out["district"].astype(str).str.strip()
    out["vulnerability_score"] = pd.to_numeric(out["vulnerability_score"], errors="coerce")
    out = out.dropna(subset=["district", "vulnerability_score"]).copy()
    if out.empty:
        return None
    out["vulnerability_score"] = out["vulnerability_score"].clip(0, 1)
    return out


def load_collection_points() -> pd.DataFrame:
    path = RAW / "collection_points.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    cp = pd.read_csv(path, encoding="utf-8-sig")
    required = {"lat", "lgt", "waste_type", "accessibilty_notes"}
    missing = sorted(required - set(cp.columns))
    if missing:
        raise ValueError(f"collection_points.csv missing columns: {', '.join(missing)}")

    cp["lat"] = pd.to_numeric(cp["lat"], errors="coerce")
    cp["lon"] = pd.to_numeric(cp["lgt"], errors="coerce")
    cp = cp.dropna(subset=["lat", "lon"]).copy()
    cp = filter_hk_bounds(cp, "lat", "lon")
    cp["is_public"] = (
        cp["accessibilty_notes"].fillna("").astype(str).str.contains("For public use", case=False, na=False)
    )
    return cp


def load_public_housing() -> pd.DataFrame:
    path = RAW / "public_housing.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    with path.open() as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("public_housing.json must be a JSON list")

    rows = []
    missing_pop = 0
    for record in raw:
        try:
            lat = float(record["Estate Map Latitude"])
            lon = float(record["Estate Map Longitude"])
        except Exception:
            continue

        flats = parse_flats(record.get("No. of Rental Flats"))
        if flats is None:
            missing_pop += 1

        rows.append(
            {
                "estate": record.get("Estate Name", {}).get("en", "Unknown"),
                "district": record.get("District Name", {}).get("en", "Unknown"),
                "lat": lat,
                "lon": lon,
                "flats": flats,
                "population": int(flats * 2.7) if flats is not None else np.nan,
            }
        )

    est = pd.DataFrame(rows)
    if est.empty:
        raise ValueError("No valid estate rows found in public_housing.json")

    est = filter_hk_bounds(est, "lat", "lon")
    if est["population"].isna().any():
        fill_value = est["population"].dropna().median()
        if pd.isna(fill_value):
            fill_value = 0
        est["population"] = est["population"].fillna(fill_value)
    est["population"] = pd.to_numeric(est["population"], errors="coerce").fillna(0).astype(int)

    if missing_pop > 0:
        print(f"  [WARN] Filled {missing_pop} housing rows with median population proxy.")

    return est


def _load_private_from_geofile(path: Path) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    if not HAS_GEO:
        return None
    try:
        gdf = gpd.read_file(path)
    except Exception:
        return None
    if gdf.empty or gdf.geometry.isna().all():
        return None
    if gdf.crs is not None:
        gdf = gdf.to_crs(epsg=4326)
    geom = gdf.geometry
    if not geom.geom_type.isin(["Point"]).all():
        geom = geom.centroid
    lon = geom.x.astype(float).to_numpy()
    lat = geom.y.astype(float).to_numpy()
    keep = (
        (lat >= HK_BOUNDS["lat_min"])
        & (lat <= HK_BOUNDS["lat_max"])
        & (lon >= HK_BOUNDS["lon_min"])
        & (lon <= HK_BOUNDS["lon_max"])
    )
    return lat[keep], lon[keep]


def _load_private_from_csv(path: Path) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        return None
    lat_col, lon_col = detect_lat_lon_columns(df)
    if lat_col is None or lon_col is None:
        return None
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col]).copy()
    df = filter_hk_bounds(df, lat_col, lon_col)
    if df.empty:
        return None
    return df[lat_col].to_numpy(dtype=float), df[lon_col].to_numpy(dtype=float)


def _load_private_from_json(path: Path) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    try:
        with path.open() as f:
            data = json.load(f)
    except Exception:
        return None
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            data = data["data"]
        else:
            return None
    if not isinstance(data, list) or not data:
        return None
    df = pd.DataFrame(data)
    lat_col, lon_col = detect_lat_lon_columns(df)
    if lat_col is None or lon_col is None:
        return None
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col]).copy()
    df = filter_hk_bounds(df, lat_col, lon_col)
    if df.empty:
        return None
    return df[lat_col].to_numpy(dtype=float), df[lon_col].to_numpy(dtype=float)


def load_private_buildings() -> Tuple[np.ndarray, np.ndarray, Optional[str]]:
    """Load private-building coordinates from optional sources."""
    geo_candidates = []
    for pattern in ("*.gml", "*.geojson", "*.gpkg", "*.shp"):
        geo_candidates.extend((GEO / "private_buildings").glob(pattern))
    for path in geo_candidates:
        loaded = _load_private_from_geofile(path)
        if loaded is not None:
            return loaded[0], loaded[1], str(path.relative_to(ROOT))

    raw_csv = RAW / "private_buildings.csv"
    if raw_csv.exists():
        loaded = _load_private_from_csv(raw_csv)
        if loaded is not None:
            return loaded[0], loaded[1], str(raw_csv.relative_to(ROOT))

    raw_json = RAW / "private_buildings.json"
    if raw_json.exists():
        loaded = _load_private_from_json(raw_json)
        if loaded is not None:
            return loaded[0], loaded[1], str(raw_json.relative_to(ROOT))

    return np.array([]), np.array([]), None


def load_green_stations() -> Tuple[np.ndarray, np.ndarray, List[str], Optional[str]]:
    """
    Optional layer for maps.
    Supports CSV in data/raw or geofile in data/geo.
    """
    csv_path = RAW / "recycling_stations.csv"
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path, encoding="utf-8-sig")
            lat_col, lon_col = detect_lat_lon_columns(df)
            if lat_col and lon_col:
                df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
                df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
                df = df.dropna(subset=[lat_col, lon_col]).copy()
                df = filter_hk_bounds(df, lat_col, lon_col)
                names = (
                    df.get("name")
                    if "name" in df.columns
                    else df.get("BLDG_ENGNM", pd.Series(["GREEN@ station"] * len(df)))
                )
                return (
                    df[lat_col].to_numpy(dtype=float),
                    df[lon_col].to_numpy(dtype=float),
                    names.astype(str).tolist(),
                    str(csv_path.relative_to(ROOT)),
                )
        except Exception:
            pass

    if HAS_GEO:
        geofiles = list((GEO / "recycling_stations").glob("*.gdb"))
        for path in geofiles:
            try:
                gdf = gpd.read_file(path).to_crs(epsg=4326)
                cent = gdf.geometry.centroid
                names = (
                    gdf["BLDG_ENGNM"].astype(str).tolist()
                    if "BLDG_ENGNM" in gdf.columns
                    else ["GREEN@ station"] * len(gdf)
                )
                return (
                    cent.y.to_numpy(dtype=float),
                    cent.x.to_numpy(dtype=float),
                    names,
                    str(path.relative_to(ROOT)),
                )
            except Exception:
                continue

    return np.array([]), np.array([]), [], None


def load_all_data() -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, Dict[str, Any]]:
    print("=" * 72)
    print("LOADING DATA")
    print("=" * 72)

    cp = load_collection_points()
    est = load_public_housing()
    pb_lat, pb_lon, private_source = load_private_buildings()
    rs_lat, rs_lon, rs_names, rs_source = load_green_stations()

    print(f"  Collection points: {len(cp):,} ({int(cp['is_public'].sum()):,} public)")
    print(f"  Public housing:    {len(est):,} estates, {int(est['population'].sum()):,} residents")
    if len(pb_lat) > 0:
        print(f"  Private buildings: {len(pb_lat):,} coordinates ({private_source})")
    else:
        print("  Private buildings: not loaded (equity multipliers will be omitted)")
    if len(rs_lat) > 0:
        print(f"  GREEN@ stations:   {len(rs_lat):,} ({rs_source})")
    else:
        print("  GREEN@ stations:   not loaded (map layer omitted)")

    meta = {
        "private_buildings_loaded": bool(len(pb_lat) > 0),
        "private_buildings_source": private_source,
        "green_stations_loaded": bool(len(rs_lat) > 0),
        "green_stations_source": rs_source,
        "green_station_names": rs_names,
        "green_station_lat": rs_lat,
        "green_station_lon": rs_lon,
    }
    return cp, est, pb_lat, pb_lon, meta


def phase1_analyze(
    cp: pd.DataFrame,
    est: pd.DataFrame,
    pb_lat: np.ndarray,
    pb_lon: np.ndarray,
    meta: Dict[str, Any],
) -> Dict[str, Any]:
    print("\n" + "=" * 72)
    print("PHASE 1 - BASELINE AND INEQUALITY ANALYSIS")
    print("=" * 72)

    estate_lat = est["lat"].to_numpy(dtype=float)
    estate_lon = est["lon"].to_numpy(dtype=float)
    pop = est["population"].to_numpy(dtype=float)
    has_private = len(pb_lat) > 0

    baseline: Dict[str, Any] = {"metadata": {}, "streams": {}, "all_streams": {}}

    if has_private:
        print(
            f"\n{'Stream':<11} {'Lock%':>6} {'Rec%':>6} {'Med PH':>8} "
            f"{'Med Private':>12} {'Gap':>7} {'Est>500':>8} {'Pop>500':>10}"
        )
        print("-" * 78)
    else:
        print(
            f"\n{'Stream':<11} {'Lock%':>6} {'Rec%':>6} {'Med PH':>8} "
            f"{'Est>500':>8} {'Pop>500':>10}"
        )
        print("-" * 58)

    for key, cfg in STREAMS.items():
        pattern = cfg["pattern"]
        mask_total = cp["waste_type"].str.contains(pattern, case=False, na=False)
        points_total = cp.loc[mask_total]
        points_public = points_total[points_total["is_public"]]

        total_n = int(len(points_total))
        public_n = int(len(points_public))
        lockout_pct = float((1.0 - (public_n / total_n)) * 100.0) if total_n else 0.0

        dist_est_public = haversine_min(
            estate_lat,
            estate_lon,
            points_public["lat"].to_numpy(dtype=float),
            points_public["lon"].to_numpy(dtype=float),
        )
        est[f"dist_{key}"] = dist_est_public

        over_mask = dist_est_public > UNDERSERVED_THRESHOLD_M
        over_estates = int(over_mask.sum())
        over_pop = int(pop[over_mask].sum())
        med_est = float(np.median(dist_est_public))

        private_med: Optional[float] = None
        multiplier: Optional[float] = None
        if has_private:
            dist_private_all = haversine_min(
                pb_lat,
                pb_lon,
                points_total["lat"].to_numpy(dtype=float),
                points_total["lon"].to_numpy(dtype=float),
            )
            private_med = float(np.median(dist_private_all))
            if private_med > 0:
                multiplier = float(med_est / private_med)

        baseline["streams"][key] = {
            "label": cfg["label"],
            "pattern": pattern,
            "total_points": total_n,
            "public_points": public_n,
            "lockout_pct": round(lockout_pct, 1),
            "tpd": cfg["tpd"],
            "recovery_pct": cfg["recovery_pct"],
            "median_estate_distance_m": round(med_est, 1),
            "median_private_distance_m": round(private_med, 1) if private_med is not None else None,
            "equity_multiplier": round(multiplier, 2) if multiplier is not None else None,
            "estates_over_500m": over_estates,
            "population_over_500m": over_pop,
        }

        if has_private:
            gap_text = f"{multiplier:>6.2f}x" if multiplier is not None else "   N/A"
            print(
                f"  {cfg['label']:<11} {lockout_pct:>5.1f}% {cfg['recovery_pct']:>5.0f}% "
                f"{med_est:>7.0f}m {private_med:>11.0f}m {gap_text:>7} "
                f"{over_estates:>8} {over_pop:>10,}"
            )
        else:
            print(
                f"  {cfg['label']:<11} {lockout_pct:>5.1f}% {cfg['recovery_pct']:>5.0f}% "
                f"{med_est:>7.0f}m {over_estates:>8} {over_pop:>10,}"
            )

    print("\n  All-stream lockout breakdown:")
    for label, pattern in ALL_STREAM_PATTERNS.items():
        mask = cp["waste_type"].str.contains(pattern, case=False, na=False)
        total_n = int(mask.sum())
        public_n = int((mask & cp["is_public"]).sum())
        lockout_pct = ((total_n - public_n) / total_n * 100.0) if total_n else 0.0
        baseline["all_streams"][label] = {
            "total_points": total_n,
            "public_points": public_n,
            "lockout_pct": round(lockout_pct, 1),
        }
        print(f"    {label:<11} {public_n:>5,}/{total_n:<5,} public ({lockout_pct:>5.1f}% locked)")

    # Single fairness metric (hero metric): population burden in textile >500m zone
    total_pop = int(est["population"].sum())
    textiles_pop_over_500 = int(baseline["streams"]["textiles"]["population_over_500m"])
    fairness_gap_pct = (textiles_pop_over_500 / total_pop * 100.0) if total_pop else 0.0

    # District vulnerability index (data-driven fallback + optional override)
    district_stats = (
        est.groupby("district", as_index=False)
        .agg(
            district_pop=("population", "sum"),
            textile_med=("dist_textiles", "median"),
            textile_pop_over_500=(
                "population",
                lambda s: int(s[est.loc[s.index, "dist_textiles"] > UNDERSERVED_THRESHOLD_M].sum()),
            ),
        )
        .copy()
    )
    district_stats["textile_over500_share"] = (
        district_stats["textile_pop_over_500"] / district_stats["district_pop"].replace(0, np.nan)
    ).fillna(0.0)

    # Normalize district metrics for a smooth 0-1 vulnerability score
    share = district_stats["textile_over500_share"].to_numpy(dtype=float)
    med = district_stats["textile_med"].to_numpy(dtype=float)
    med_norm = (med - med.min()) / (med.max() - med.min() + 1e-9)
    vulnerability_fallback = 0.75 * share + 0.25 * med_norm

    override = load_district_vulnerability_override()
    if override is not None:
        district_stats = district_stats.merge(override, on="district", how="left")
        district_stats["district_vulnerability"] = district_stats["vulnerability_score"].fillna(vulnerability_fallback)
        vulnerability_source = "district_vulnerability.csv override + fallback blend"
    else:
        district_stats["district_vulnerability"] = vulnerability_fallback
        vulnerability_source = "derived from textile burden (over500 share + median distance)"

    district_stats["district_vulnerability"] = district_stats["district_vulnerability"].clip(0, 1)
    vulnerability_map = dict(
        zip(district_stats["district"], district_stats["district_vulnerability"])
    )
    est["district_vulnerability"] = est["district"].map(vulnerability_map).fillna(0.0)

    top_vulnerable = (
        district_stats.sort_values("district_vulnerability", ascending=False)
        .head(8)[["district", "district_vulnerability", "textile_over500_share"]]
    )

    print(
        f"\n  Fairness metric (textile population >500m): "
        f"{fairness_gap_pct:.1f}% ({textiles_pop_over_500:,}/{total_pop:,})"
    )
    print(f"  Vulnerability index source: {vulnerability_source}")

    baseline["metadata"] = {
        "private_comparator_available": has_private,
        "private_comparator_source": meta["private_buildings_source"],
        "underserved_threshold_m": UNDERSERVED_THRESHOLD_M,
        "population_proxy_note": "Public housing population proxy = rental_flats * 2.7",
        "vulnerability_source": vulnerability_source,
    }
    baseline["fairness_metric"] = {
        "name": "Textile Population Burden (>500m)",
        "value_pct": round(fairness_gap_pct, 2),
        "numerator_population": textiles_pop_over_500,
        "denominator_population": total_pop,
        "threshold_m": UNDERSERVED_THRESHOLD_M,
    }
    baseline["district_vulnerability"] = {
        "top_districts": [
            {
                "district": str(r["district"]),
                "vulnerability": round(float(r["district_vulnerability"]), 3),
                "textile_over500_share": round(float(r["textile_over500_share"]), 3),
            }
            for _, r in top_vulnerable.iterrows()
        ]
    }

    with (OUT / "baseline_metrics.json").open("w") as f:
        json.dump(baseline, f, indent=2)
    print(f"\n  Saved: {OUT / 'baseline_metrics.json'}")

    return baseline


def phase2_optimize_hubs(est: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    print("\n" + "=" * 72)
    print("PHASE 2 - HUB PLACEMENT OPTIMIZATION (GREEDY MAX-COVERAGE)")
    print("=" * 72)

    estate_lat = est["lat"].to_numpy(dtype=float)
    estate_lon = est["lon"].to_numpy(dtype=float)
    pop = est["population"].to_numpy(dtype=float)
    vulnerability = est.get("district_vulnerability", pd.Series(np.zeros(len(est)))).to_numpy(dtype=float)

    keys = list(STREAMS.keys())
    weights = {k: STREAMS[k]["tpd"] for k in keys}
    weight_total = float(sum(weights.values()))
    for k in keys:
        weights[k] = weights[k] / weight_total

    current_dist = {k: est[f"dist_{k}"].to_numpy(dtype=float).copy() for k in keys}
    candidates = set(est.index.tolist())
    selected_coords: List[Tuple[float, float]] = []
    selected_rows: List[Dict[str, Any]] = []
    global_served = np.zeros(len(est), dtype=bool)

    def candidate_score(idx: int) -> Tuple[float, np.ndarray, float, float, float]:
        clat = float(est.at[idx, "lat"])
        clon = float(est.at[idx, "lon"])
        d_to_candidate = haversine_min(
            estate_lat, estate_lon, np.array([clat]), np.array([clon])
        )

        multistream_score = 0.0
        for key in keys:
            before = current_dist[key]
            after = np.minimum(before, d_to_candidate)

            rescued_mask = (before > UNDERSERVED_THRESHOLD_M) & (after <= HUB_SERVICE_RADIUS_M)
            rescued_pop = float(pop[rescued_mask].sum())

            dist_reduction = np.maximum(0.0, before - after)
            weighted_dist_reduction = float((dist_reduction * pop).sum()) / 1000.0

            multistream_score += weights[key] * (rescued_pop + 0.03 * weighted_dist_reduction)

        before_textiles = current_dist["textiles"]
        after_textiles = np.minimum(before_textiles, d_to_candidate)
        rescued_textile_mask = (
            (before_textiles > UNDERSERVED_THRESHOLD_M)
            & (after_textiles <= HUB_SERVICE_RADIUS_M)
        )
        rescued_textile_pop = float(pop[rescued_textile_mask].sum())
        equity_bonus = float((pop[rescued_textile_mask] * vulnerability[rescued_textile_mask]).sum())

        score = (
            MULTISTREAM_SCORE_WEIGHT * multistream_score
            + TEXTILE_RESCUE_WEIGHT * rescued_textile_pop
            + EQUITY_BONUS_WEIGHT * equity_bonus
        )

        return score, d_to_candidate, multistream_score, rescued_textile_pop, equity_bonus

    for hub_rank in range(1, NUM_HUBS + 1):
        best_idx = None
        best_score = -1.0
        best_dist = None
        best_multistream = 0.0
        best_textile_rescue = 0.0
        best_equity_bonus = 0.0

        for enforce_separation in (True, False):
            for idx in list(candidates):
                if enforce_separation and selected_coords:
                    d_to_selected = haversine_min(
                        np.array([float(est.at[idx, "lat"])]),
                        np.array([float(est.at[idx, "lon"])]),
                        np.array([c[0] for c in selected_coords]),
                        np.array([c[1] for c in selected_coords]),
                    )[0]
                    if d_to_selected < HUB_MIN_SEPARATION_M:
                        continue

                score, d_to_candidate, ms_score, textile_rescue, eq_bonus = candidate_score(idx)
                if score > best_score:
                    best_idx = idx
                    best_score = score
                    best_dist = d_to_candidate
                    best_multistream = ms_score
                    best_textile_rescue = textile_rescue
                    best_equity_bonus = eq_bonus

            if best_idx is not None:
                break

        if best_idx is None or best_dist is None:
            break

        for key in keys:
            current_dist[key] = np.minimum(current_dist[key], best_dist)

        in_radius = best_dist <= HUB_SERVICE_RADIUS_M
        new_in_radius = in_radius & (~global_served)
        global_served = global_served | in_radius

        row = est.loc[best_idx]
        selected_rows.append(
            {
                "hub_rank": int(hub_rank),
                "estate": row["estate"],
                "district": row["district"],
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "estate_population": int(row["population"]),
                "estates_in_radius": int(in_radius.sum()),
                "population_in_radius": int(est.loc[in_radius, "population"].sum()),
                "new_estates_covered": int(new_in_radius.sum()),
                "new_population_covered": int(est.loc[new_in_radius, "population"].sum()),
                "weighted_score": round(float(best_score), 2),
                "score_multistream": round(float(best_multistream), 2),
                "score_textile_rescue": round(float(best_textile_rescue), 2),
                "score_equity_bonus": round(float(best_equity_bonus), 2),
            }
        )

        selected_coords.append((float(row["lat"]), float(row["lon"])))
        candidates.remove(best_idx)

    hubs = pd.DataFrame(selected_rows)
    hubs.to_csv(OUT / "optimized_hubs.csv", index=False)

    summary = {
        "num_hubs_selected": int(len(hubs)),
        "hub_service_radius_m": HUB_SERVICE_RADIUS_M,
        "hub_min_separation_m": HUB_MIN_SEPARATION_M,
        "scoring_weights": {
            "multistream_score_weight": MULTISTREAM_SCORE_WEIGHT,
            "textile_rescue_weight": TEXTILE_RESCUE_WEIGHT,
            "equity_bonus_weight": EQUITY_BONUS_WEIGHT,
        },
        "unique_estates_covered": int(global_served.sum()),
        "unique_population_covered": int(est.loc[global_served, "population"].sum()),
    }

    print(
        f"\n  Selected {summary['num_hubs_selected']} hubs | "
        f"Unique coverage: {summary['unique_estates_covered']} estates, "
        f"{summary['unique_population_covered']:,} residents"
    )
    print(f"  Saved: {OUT / 'optimized_hubs.csv'}")

    return hubs, summary


def estimate_diversion(
    impact: Dict[str, Any], baseline: Dict[str, Any], total_population: int
) -> Dict[str, Any]:
    stream_details: Dict[str, Any] = {}
    additional_low_tpd = 0.0
    additional_high_tpd = 0.0

    for key, cfg in STREAMS.items():
        base = baseline["streams"][key]
        imp = impact[key]

        before_over_pop = imp["before_population_over_500m"]
        pop_saved = imp["population_saved"]
        if before_over_pop <= 0 or pop_saved <= 0:
            stream_details[key] = {
                "additional_low_tpd": 0.0,
                "additional_high_tpd": 0.0,
                "underserved_share": 0.0,
                "rescue_ratio": 0.0,
            }
            continue

        unrecovered_tpd = cfg["tpd"] * (1.0 - cfg["recovery_pct"] / 100.0)
        underserved_share = before_over_pop / total_population
        rescue_ratio = pop_saved / before_over_pop

        add_low = unrecovered_tpd * underserved_share * rescue_ratio * CAPTURE_FACTOR_LOW
        add_high = unrecovered_tpd * underserved_share * rescue_ratio * CAPTURE_FACTOR_HIGH

        additional_low_tpd += add_low
        additional_high_tpd += add_high

        stream_details[key] = {
            "unrecovered_tpd": round(unrecovered_tpd, 3),
            "underserved_share": round(underserved_share, 4),
            "rescue_ratio": round(rescue_ratio, 4),
            "additional_low_tpd": round(add_low, 3),
            "additional_high_tpd": round(add_high, 3),
        }

    annual_low = additional_low_tpd * 365.0
    annual_high = additional_high_tpd * 365.0

    savings_low = annual_low * LANDFILL_GATE_FEE_HKD_PER_TONNE
    savings_high = annual_high * LANDFILL_GATE_FEE_HKD_PER_TONNE

    capex_min = NUM_HUBS * CAPEX_PER_HUB_MIN
    capex_max = NUM_HUBS * CAPEX_PER_HUB_MAX

    payback_best = capex_min / savings_high if savings_high > 0 else None
    payback_worst = capex_max / savings_low if savings_low > 0 else None

    return {
        "assumptions": {
            "capture_factor_low": CAPTURE_FACTOR_LOW,
            "capture_factor_high": CAPTURE_FACTOR_HIGH,
            "landfill_gate_fee_hkd_per_tonne": LANDFILL_GATE_FEE_HKD_PER_TONNE,
            "model_note": (
                "Additional diversion is estimated from stream-level unrecovered waste, "
                "share of population previously underserved (>500m), and share rescued by hubs."
            ),
        },
        "stream_details": stream_details,
        "additional_diversion_tpd_low": round(additional_low_tpd, 2),
        "additional_diversion_tpd_high": round(additional_high_tpd, 2),
        "additional_diversion_annual_tonnes_low": round(annual_low),
        "additional_diversion_annual_tonnes_high": round(annual_high),
        "landfill_savings_hkd_per_year_low": round(savings_low),
        "landfill_savings_hkd_per_year_high": round(savings_high),
        "capex_hkd_min": capex_min,
        "capex_hkd_max": capex_max,
        "payback_years_best_case": round(payback_best, 2) if payback_best is not None else None,
        "payback_years_worst_case": round(payback_worst, 2) if payback_worst is not None else None,
    }


def phase3_measure_impact(
    est: pd.DataFrame, hubs: pd.DataFrame, baseline: Dict[str, Any], optimization_summary: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    print("\n" + "=" * 72)
    print("PHASE 3 - IMPACT AND COST-BENEFIT")
    print("=" * 72)

    if hubs.empty:
        raise ValueError("No hubs selected; cannot compute impact")

    hub_dist = haversine_min(
        est["lat"].to_numpy(dtype=float),
        est["lon"].to_numpy(dtype=float),
        hubs["lat"].to_numpy(dtype=float),
        hubs["lon"].to_numpy(dtype=float),
    )
    est["nearest_hub_distance_m"] = hub_dist

    impact: Dict[str, Any] = {}
    print(
        f"\n{'Stream':<11} {'Before>500':>10} {'After>500':>9} "
        f"{'Delta':>7} {'Pop Saved':>12} {'Median B':>10} {'Median A':>10}"
    )
    print("-" * 80)

    for key, cfg in STREAMS.items():
        before = est[f"dist_{key}"].to_numpy(dtype=float)
        after = np.minimum(before, hub_dist)
        est[f"dist_{key}_after"] = after

        before_over = before > UNDERSERVED_THRESHOLD_M
        after_over = after > UNDERSERVED_THRESHOLD_M

        before_count = int(before_over.sum())
        after_count = int(after_over.sum())
        before_pop = int(est.loc[before_over, "population"].sum())
        after_pop = int(est.loc[after_over, "population"].sum())
        pop_saved = before_pop - after_pop

        impact[key] = {
            "label": cfg["label"],
            "before_estates_over_500m": before_count,
            "after_estates_over_500m": after_count,
            "delta_estates_over_500m": before_count - after_count,
            "before_population_over_500m": before_pop,
            "after_population_over_500m": after_pop,
            "population_saved": pop_saved,
            "median_distance_before_m": round(float(np.median(before)), 1),
            "median_distance_after_m": round(float(np.median(after)), 1),
        }

        print(
            f"  {cfg['label']:<11} {before_count:>10} {after_count:>9} "
            f"{before_count - after_count:>7} {pop_saved:>12,} "
            f"{np.median(before):>9.0f}m {np.median(after):>9.0f}m"
        )

    total_population = int(est["population"].sum())
    diversion = estimate_diversion(impact, baseline, total_population)

    cost_summary = {
        "num_hubs": NUM_HUBS,
        "capex_range_hkd": [NUM_HUBS * CAPEX_PER_HUB_MIN, NUM_HUBS * CAPEX_PER_HUB_MAX],
        "additional_diversion_tpd_range": [
            diversion["additional_diversion_tpd_low"],
            diversion["additional_diversion_tpd_high"],
        ],
        "additional_diversion_annual_tonnes_range": [
            diversion["additional_diversion_annual_tonnes_low"],
            diversion["additional_diversion_annual_tonnes_high"],
        ],
        "landfill_savings_hkd_per_year_range": [
            diversion["landfill_savings_hkd_per_year_low"],
            diversion["landfill_savings_hkd_per_year_high"],
        ],
        "payback_years_range": [
            diversion["payback_years_best_case"],
            diversion["payback_years_worst_case"],
        ],
    }

    print(
        f"\n  Diversion (modeled): {diversion['additional_diversion_annual_tonnes_low']:,} - "
        f"{diversion['additional_diversion_annual_tonnes_high']:,} tonnes/year"
    )
    print(
        f"  Savings (gate fee): HK${diversion['landfill_savings_hkd_per_year_low'] / 1e6:.1f}M - "
        f"HK${diversion['landfill_savings_hkd_per_year_high'] / 1e6:.1f}M/year"
    )
    if diversion["payback_years_best_case"] is not None and diversion["payback_years_worst_case"] is not None:
        print(
            f"  Payback range: {diversion['payback_years_best_case']:.1f} - "
            f"{diversion['payback_years_worst_case']:.1f} years"
        )

    report = {
        "metadata": {
            "analysis_type": "complexity_lockout_approach2",
            "underserved_threshold_m": UNDERSERVED_THRESHOLD_M,
            "hub_service_radius_m": HUB_SERVICE_RADIUS_M,
            "num_hubs": NUM_HUBS,
        },
        "fairness_metric": baseline.get("fairness_metric"),
        "optimization_summary": optimization_summary,
        "impact": impact,
        "diversion_model": diversion,
        "cost_summary": cost_summary,
    }

    with (OUT / "impact_report.json").open("w") as f:
        json.dump(report, f, indent=2)
    est.to_csv(OUT / "estates_full_analysis.csv", index=False)
    print(f"  Saved: {OUT / 'impact_report.json'}")
    print(f"  Saved: {OUT / 'estates_full_analysis.csv'}")

    return impact, report


def viz_01_landfill_and_lockout(
    baseline: Dict[str, Any], impact: Dict[str, Any], optimization_summary: Dict[str, Any]
) -> None:
    """Hero slide visual: one-stream textiles thesis with crisp before/after evidence."""
    textiles = baseline["streams"]["textiles"]
    fairness = baseline["fairness_metric"]
    t_impact = impact["textiles"]

    total_pop = max(int(fairness["denominator_population"]), 1)
    before_over = int(t_impact["before_population_over_500m"])
    after_over = int(t_impact["after_population_over_500m"])
    before_within = total_pop - before_over
    after_within = total_pop - after_over

    fig = plt.figure(figsize=(16, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.95, 1.65], wspace=0.18, hspace=0.30)

    ax_cards = fig.add_subplot(gs[0, :])
    ax_cards.axis("off")
    cards = [
        ("Textile lockout", f"{textiles['lockout_pct']:.1f}%", "Share of textile points not public"),
        ("Fairness metric", f"{fairness['value_pct']:.1f}%", "Residents >500m from textile access"),
        (
            "Population rescued",
            fmt_int(t_impact["population_saved"]),
            "Moved out of >500m zone by 10 hubs",
        ),
        (
            "Hub footprint",
            fmt_int(optimization_summary["unique_population_covered"]),
            "Residents within 800m of selected hubs",
        ),
    ]

    card_w = 0.235
    gap = 0.02
    for i, (title, value, subtitle) in enumerate(cards):
        x0 = i * (card_w + gap)
        rect = plt.Rectangle(
            (x0, 0.04),
            card_w,
            0.90,
            transform=ax_cards.transAxes,
            facecolor=THEME["bg_soft"],
            edgecolor="#DFE5EC",
            linewidth=1.0,
            zorder=0,
        )
        ax_cards.add_patch(rect)
        ax_cards.text(
            x0 + 0.02,
            0.80,
            title,
            transform=ax_cards.transAxes,
            fontsize=11,
            color=THEME["text_muted"],
            fontweight="semibold",
        )
        ax_cards.text(
            x0 + 0.02,
            0.46,
            value,
            transform=ax_cards.transAxes,
            fontsize=30,
            color=THEME["accent"] if i < 2 else THEME["text_dark"],
            fontweight="bold",
        )
        ax_cards.text(
            x0 + 0.02,
            0.19,
            subtitle,
            transform=ax_cards.transAxes,
            fontsize=10,
            color=THEME["text_muted"],
        )

    ax_share = fig.add_subplot(gs[1, 0])
    labels = ["Before hubs", "After hubs"]
    within_shares = [before_within / total_pop * 100, after_within / total_pop * 100]
    over_shares = [before_over / total_pop * 100, after_over / total_pop * 100]
    y = np.arange(2)
    ax_share.barh(y, within_shares, color="#D9F2E6", label="Within 500m")
    ax_share.barh(y, over_shares, left=within_shares, color=THEME["warn"], label="Beyond 500m")
    ax_share.set_yticks(y)
    ax_share.set_yticklabels(labels)
    ax_share.set_xlim(0, 100)
    ax_share.xaxis.set_major_formatter(mticker.PercentFormatter())
    ax_share.set_xlabel("Share of public-housing population")
    ax_share.set_title("Textile Access Split")
    ax_share.invert_yaxis()
    ax_share.grid(axis="x")
    ax_share.grid(axis="y", visible=False)
    for idx in range(2):
        ax_share.text(
            within_shares[idx] + over_shares[idx] - 1.3,
            idx,
            f"{over_shares[idx]:.1f}%",
            ha="right",
            va="center",
            fontsize=10,
            color="white",
            fontweight="semibold",
        )
    ax_share.legend(loc="lower right")

    ax_shift = fig.add_subplot(gs[1, 1])
    metrics = [
        ("Median distance", t_impact["median_distance_before_m"], t_impact["median_distance_after_m"], "m"),
        ("Estates >500m", t_impact["before_estates_over_500m"], t_impact["after_estates_over_500m"], ""),
        (
            "Population >500m",
            t_impact["before_population_over_500m"],
            t_impact["after_population_over_500m"],
            "",
        ),
    ]
    labels = [m[0] for m in metrics][::-1]
    reductions = []
    for _, before, after, _ in metrics[::-1]:
        reductions.append(((before - after) / before * 100.0) if before > 0 else 0.0)
    y = np.arange(len(labels))
    bars = ax_shift.barh(y, reductions, color=THEME["accent"], alpha=0.9, height=0.55)
    ax_shift.set_yticks(y)
    ax_shift.set_yticklabels(labels)
    ax_shift.set_xlim(0, max(8.0, max(reductions) * 1.28))
    ax_shift.xaxis.set_major_formatter(mticker.PercentFormatter())
    ax_shift.set_xlabel("Reduction from baseline")
    ax_shift.set_title("Optimization Impact (Relative Improvement)")
    ax_shift.grid(axis="x")
    ax_shift.grid(axis="y", visible=False)
    for bar, (_, before, after, unit) in zip(bars, metrics[::-1]):
        x = bar.get_width()
        y_mid = bar.get_y() + bar.get_height() / 2
        before_txt = f"{before:.0f}{unit}" if before < 10_000 else fmt_int(before)
        after_txt = f"{after:.0f}{unit}" if after < 10_000 else fmt_int(after)
        ax_shift.text(x + 0.7, y_mid, f"{before_txt} → {after_txt}", va="center", fontsize=9, color=THEME["text_muted"])

    fig.suptitle("Hero Stream: Textiles Access Barrier and Improvement", fontsize=20, fontweight="bold", y=0.99)
    fig.text(
        0.5,
        0.955,
        "10 equity-prioritized hubs reduce distance burden without overcomplicating the solution.",
        ha="center",
        va="center",
        fontsize=11,
        color=THEME["text_muted"],
    )
    fig.savefig(VIZ / "01_landfill_composition.png", dpi=320, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {VIZ / '01_landfill_composition.png'}")


def viz_02_inequality(baseline: Dict[str, Any], est: pd.DataFrame) -> None:
    """Single fairness metric slide: where burden concentrates."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={"width_ratios": [1.2, 1]})

    d = np.sort(est["dist_textiles"].to_numpy(dtype=float))
    cdf = np.arange(1, len(d) + 1) / len(d)
    fairness = baseline["fairness_metric"]

    axes[0].plot(d, cdf, color=THEME["accent_alt"], linewidth=3)
    axes[0].axvline(UNDERSERVED_THRESHOLD_M, color=THEME["warn"], linestyle="--", linewidth=1.6)
    axes[0].fill_betweenx(cdf, UNDERSERVED_THRESHOLD_M, d.max(), color="#FDEBEC", alpha=0.8)
    axes[0].annotate(
        "500m threshold",
        xy=(UNDERSERVED_THRESHOLD_M, 0.90),
        xytext=(UNDERSERVED_THRESHOLD_M + 95, 0.80),
        arrowprops=dict(arrowstyle="-", color=THEME["warn"], lw=1.2),
        color=THEME["warn"],
        fontsize=10,
    )
    axes[0].text(
        0.98,
        0.08,
        f"Fairness metric\n{fairness['value_pct']:.1f}% of residents\nare beyond 500m",
        transform=axes[0].transAxes,
        ha="right",
        va="bottom",
        fontsize=11,
        color=THEME["text_dark"],
        bbox=dict(boxstyle="round,pad=0.45", facecolor=THEME["bg_soft"], edgecolor="#DCE4ED"),
    )
    axes[0].set_title("Textile Access Distribution (CDF)")
    axes[0].set_xlabel("Distance to nearest public textile point (m)")
    axes[0].set_ylabel("Cumulative share of estates")
    axes[0].set_xlim(0, max(1200, int(d.max() + 40)))
    axes[0].set_ylim(0, 1.02)
    axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(1.0))

    district = (
        est.groupby("district", as_index=False)
        .agg(
            district_pop=("population", "sum"),
            pop_over_500=("population", lambda s: int(s[est.loc[s.index, "dist_textiles"] > UNDERSERVED_THRESHOLD_M].sum())),
        )
        .copy()
    )
    district["share_over_500"] = (
        district["pop_over_500"] / district["district_pop"].replace(0, np.nan)
    ).fillna(0.0)
    top = district.sort_values("share_over_500", ascending=False).head(8)

    bar_colors = [THEME["warn"]] + ["#EE6D72"] * (len(top) - 1)
    bars = axes[1].barh(top["district"], top["share_over_500"] * 100, color=bar_colors, height=0.75)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Residents beyond 500m (%)")
    axes[1].set_title("Highest-Burden Districts")
    axes[1].set_xlim(0, max(8, float((top["share_over_500"] * 100).max()) + 8))
    axes[1].grid(axis="x")
    axes[1].grid(axis="y", visible=False)
    for bar, share in zip(bars, top["share_over_500"]):
        axes[1].text(
            bar.get_width() + 0.7,
            bar.get_y() + bar.get_height() / 2,
            f"{share * 100:.1f}%",
            va="center",
            fontsize=10,
            color=THEME["text_dark"],
        )

    fig.suptitle("Fairness Metric: Textile Distance Burden", fontsize=19, fontweight="bold", y=0.98)
    fig.text(
        0.5,
        0.94,
        "One metric, one message: distance burden is concentrated and measurable.",
        ha="center",
        color=THEME["text_muted"],
        fontsize=11,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(VIZ / "02_stream_inequality.png", dpi=320, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {VIZ / '02_stream_inequality.png'}")


def viz_03_textiles_deep_dive(
    est: pd.DataFrame, hubs: pd.DataFrame, impact: Dict[str, Any], optimization_summary: Dict[str, Any]
) -> None:
    """Optimization map: static, decluttered, and slide-ready."""
    fig, ax = plt.subplots(figsize=(11.5, 9))

    base = est.copy()
    base["severity"] = pd.cut(
        base["dist_textiles"],
        bins=[-np.inf, UNDERSERVED_THRESHOLD_M, 1000, np.inf],
        labels=["served", "underserved", "critical"],
    )

    served = base[base["severity"] == "served"]
    underserved = base[base["severity"] == "underserved"]
    critical = base[base["severity"] == "critical"]

    ax.scatter(
        served["lon"],
        served["lat"],
        s=18,
        c="#D5DEE8",
        alpha=0.50,
        linewidths=0,
        label="Served estates (<=500m)",
        zorder=1,
    )
    ax.scatter(
        underserved["lon"],
        underserved["lat"],
        s=np.clip(underserved["population"] / 1200, 35, 120),
        c="#F4A261",
        alpha=0.78,
        edgecolor="white",
        linewidth=0.5,
        label="Underserved (500-1000m)",
        zorder=2,
    )
    ax.scatter(
        critical["lon"],
        critical["lat"],
        s=np.clip(critical["population"] / 1000, 45, 150),
        c=THEME["warn"],
        alpha=0.90,
        edgecolor="white",
        linewidth=0.6,
        label="Critical (>1000m)",
        zorder=3,
    )

    radius_deg = HUB_SERVICE_RADIUS_M / 111_000.0
    for _, row in hubs.iterrows():
        coverage = mpatches.Circle(
            (row["lon"], row["lat"]),
            radius=radius_deg,
            facecolor="#3B82F622",
            edgecolor="#3B82F6",
            linewidth=1.0,
            zorder=2.4,
        )
        ax.add_patch(coverage)

    ax.scatter(
        hubs["lon"],
        hubs["lat"],
        s=170,
        c="#0F4C81",
        marker="*",
        edgecolor="white",
        linewidth=0.8,
        label="Proposed hubs",
        zorder=4,
    )

    top_hubs = hubs.sort_values("new_population_covered", ascending=False).head(6)
    for _, row in top_hubs.iterrows():
        ax.text(
            row["lon"] + 0.006,
            row["lat"] + 0.003,
            f"H{int(row['hub_rank'])}\n+{fmt_k(row['new_population_covered'])}",
            fontsize=8.8,
            color=THEME["text_dark"],
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#D4DEE8"),
            zorder=5,
        )

    t_impact = impact["textiles"]
    before = t_impact["before_estates_over_500m"]
    after = t_impact["after_estates_over_500m"]
    summary = (
        f"10 hubs selected  •  {before} → {after} estates >500m\n"
        f"Population rescued: {fmt_int(t_impact['population_saved'])}  •  "
        f"Unique coverage: {fmt_int(optimization_summary['unique_population_covered'])}"
    )
    ax.text(
        0.01,
        0.02,
        summary,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10.2,
        color=THEME["text_dark"],
        bbox=dict(boxstyle="round,pad=0.45", facecolor=THEME["bg_soft"], edgecolor="#DCE4ED"),
    )

    ax.set_title("Optimization Map: Textile Access Gaps and Proposed Hub Locations", pad=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.6, alpha=0.55)
    ax.legend(loc="upper left", fontsize=9, frameon=True, facecolor="white", edgecolor="#DCE4ED")

    pad_lon = 0.02
    pad_lat = 0.015
    ax.set_xlim(base["lon"].min() - pad_lon, base["lon"].max() + pad_lon)
    ax.set_ylim(base["lat"].min() - pad_lat, base["lat"].max() + pad_lat)

    fig.tight_layout()
    fig.savefig(VIZ / "03_textiles_deep_dive.png", dpi=320, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {VIZ / '03_textiles_deep_dive.png'}")


def viz_05_interactive_map(
    cp: pd.DataFrame,
    est: pd.DataFrame,
    hubs: pd.DataFrame,
    meta: Dict[str, Any],
) -> None:
    """Decluttered interactive map focused on textiles + proposed hubs."""
    if not HAS_FOLIUM:
        print("  Skipped map: folium not installed")
        return

    m = folium.Map(
        location=[float(est["lat"].mean()), float(est["lon"].mean())],
        zoom_start=11,
        tiles="CartoDB Positron",
        control_scale=True,
    )

    fg_est = folium.FeatureGroup(name="Underserved estates (>500m textile)", show=True)
    fg_hubs = folium.FeatureGroup(name="Proposed hubs", show=True)
    fg_textile = folium.FeatureGroup(name="Existing public textile points (sample)", show=False)

    for _, row in est.iterrows():
        dist = float(row["dist_textiles"])
        if dist <= UNDERSERVED_THRESHOLD_M:
            continue
        color = "#C62828" if dist > 1000 else "#FB8C00"
        radius = 5 if row["population"] < 12000 else 7
        tooltip = (
            f"{row['estate']} | {row['district']} | "
            f"{int(row['population']):,} residents | {dist:.0f}m"
        )
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.72,
            tooltip=tooltip,
        ).add_to(fg_est)

    for _, row in hubs.iterrows():
        hub_no = int(row["hub_rank"])
        html = f"""
        <div style="
            background:#1565C0;color:white;border-radius:50%;
            width:24px;height:24px;line-height:24px;text-align:center;
            font-size:12px;font-weight:700;border:2px solid white;">
            {hub_no}
        </div>
        """
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.DivIcon(html=html),
            tooltip=(
                f"Hub {hub_no}: {row['estate']} ({row['district']}) | "
                f"New pop covered: {int(row['new_population_covered']):,}"
            ),
        ).add_to(fg_hubs)
        folium.Circle(
            location=[row["lat"], row["lon"]],
            radius=HUB_SERVICE_RADIUS_M,
            color="#1E88E5",
            weight=1.1,
            fill=False,
            dash_array="5,6",
            opacity=0.75,
        ).add_to(fg_hubs)

    tex = cp[
        cp["is_public"]
        & cp["waste_type"].str.contains(STREAMS["textiles"]["pattern"], case=False, na=False)
    ]
    tex_sample = tex.sample(n=min(450, len(tex)), random_state=42)
    for _, row in tex_sample.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=2.4,
            color="#7B1FA2",
            fill=True,
            fill_opacity=0.35,
            tooltip="Public textile point",
        ).add_to(fg_textile)

    fg_est.add_to(m)
    fg_hubs.add_to(m)
    fg_textile.add_to(m)

    if meta["green_stations_loaded"]:
        fg_green = folium.FeatureGroup(name="GREEN@ stations", show=False)
        names = meta["green_station_names"]
        for i in range(len(meta["green_station_lat"])):
            nm = names[i] if i < len(names) else "GREEN@ station"
            folium.Marker(
                location=[meta["green_station_lat"][i], meta["green_station_lon"][i]],
                icon=folium.Icon(color="green", icon="recycle", prefix="fa"),
                tooltip=nm,
            ).add_to(fg_green)
        fg_green.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    legend = """
    <div style="
      position:fixed; bottom:20px; left:20px; z-index:9999;
      background:rgba(255,255,255,0.97); padding:10px 12px;
      border:1px solid #DDD; border-radius:8px; font-size:12px; line-height:1.5;">
      <b>Textile Access Map</b><br>
      <span style="color:#FB8C00;">●</span> Estate 500-1000m<br>
      <span style="color:#C62828;">●</span> Estate >1000m<br>
      <span style="color:#7B1FA2;">●</span> Public textile point (sample)<br>
      <span style="color:#1565C0;">●</span> Proposed hub (800m ring)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend))

    m.save(VIZ / "05_interactive_map.html")
    print(f"  Saved: {VIZ / '05_interactive_map.html'}")


def viz_06_sensitivity(report: Dict[str, Any]) -> None:
    """Sensitivity and assumptions figure for presentation backup/appendix."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={"width_ratios": [1.25, 1]})

    low_factor = report["diversion_model"]["assumptions"]["capture_factor_low"]
    low_tpd = report["diversion_model"]["additional_diversion_tpd_low"]
    base_unscaled_tpd = low_tpd / max(low_factor, 1e-9)
    fee = report["diversion_model"]["assumptions"]["landfill_gate_fee_hkd_per_tonne"]

    capture_grid = np.array([0.15, 0.20, 0.25, 0.30, 0.35, 0.40])
    capex_grid_m = np.array([20, 30, 40, 50], dtype=float)
    heat = np.zeros((len(capex_grid_m), len(capture_grid)))
    for i, capex_m in enumerate(capex_grid_m):
        capex = capex_m * 1_000_000
        for j, cf in enumerate(capture_grid):
            tpd = base_unscaled_tpd * cf
            annual = tpd * 365
            savings = annual * fee
            heat[i, j] = capex / savings if savings > 0 else np.nan

    im = axes[0].imshow(heat, cmap="YlGnBu_r", aspect="auto")
    axes[0].set_xticks(np.arange(len(capture_grid)))
    axes[0].set_xticklabels([f"{c:.2f}" for c in capture_grid])
    axes[0].set_yticks(np.arange(len(capex_grid_m)))
    axes[0].set_yticklabels([f"HK${int(c)}M" for c in capex_grid_m])
    axes[0].set_xlabel("Capture factor")
    axes[0].set_ylabel("Total capex")
    axes[0].set_title("Payback Sensitivity (years)")
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            axes[0].text(j, i, f"{heat[i, j]:.1f}", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

    axes[1].axis("off")
    summary = report["cost_summary"]
    assumptions_text = (
        "Assumptions\n"
        f"• Underserved threshold: {report['metadata']['underserved_threshold_m']}m\n"
        f"• Hub service radius: {report['metadata']['hub_service_radius_m']}m\n"
        f"• Capture factor range: {capture_grid.min():.2f} - {capture_grid.max():.2f}\n"
        f"• Gate fee: HK${fee}/tonne\n"
        f"• Capex range: HK${summary['capex_range_hkd'][0]/1e6:.0f}M - HK${summary['capex_range_hkd'][1]/1e6:.0f}M\n\n"
        "Current modeled range\n"
        f"• Diversion: {summary['additional_diversion_annual_tonnes_range'][0]:,} - "
        f"{summary['additional_diversion_annual_tonnes_range'][1]:,} t/yr\n"
        f"• Savings: HK${summary['landfill_savings_hkd_per_year_range'][0]/1e6:.1f}M - "
        f"HK${summary['landfill_savings_hkd_per_year_range'][1]/1e6:.1f}M/yr\n"
        f"• Payback: {summary['payback_years_range'][0]:.1f} - {summary['payback_years_range'][1]:.1f} years"
    )
    axes[1].text(
        0.02,
        0.98,
        assumptions_text,
        va="top",
        ha="left",
        fontsize=11,
        linespacing=1.5,
        color="#263238",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#FAFBFC", edgecolor="#DCE3E8"),
    )

    fig.tight_layout()
    fig.savefig(VIZ / "06_sensitivity_assumptions.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {VIZ / '06_sensitivity_assumptions.png'}")


def main() -> None:
    set_plot_style()
    cp, est, pb_lat, pb_lon, meta = load_all_data()

    baseline = phase1_analyze(cp, est, pb_lat, pb_lon, meta)
    hubs, optimization_summary = phase2_optimize_hubs(est)
    impact, report = phase3_measure_impact(est, hubs, baseline, optimization_summary)

    print("\n" + "=" * 72)
    print("GENERATING VISUALIZATIONS")
    print("=" * 72)
    viz_01_landfill_and_lockout(baseline, impact, optimization_summary)
    viz_02_inequality(baseline, est)
    viz_03_textiles_deep_dive(est, hubs, impact, optimization_summary)
    viz_05_interactive_map(cp, est, hubs, meta)
    viz_06_sensitivity(report)

    textiles = baseline["streams"]["textiles"]
    textiles_impact = impact["textiles"]
    diversion = report["diversion_model"]

    print("\n" + "=" * 72)
    print("PIPELINE COMPLETE")
    print("=" * 72)
    print(f"  Textiles lockout: {textiles['lockout_pct']:.1f}%")
    print(
        f"  Textiles underserved estates (>500m): "
        f"{textiles_impact['before_estates_over_500m']} -> {textiles_impact['after_estates_over_500m']}"
    )
    print(
        f"  Fairness metric (population >500m textile): "
        f"{baseline['fairness_metric']['value_pct']:.1f}%"
    )
    print(
        f"  Textiles population saved: {textiles_impact['population_saved']:,}"
    )
    if baseline["metadata"]["private_comparator_available"]:
        print(
            f"  Textile equity multiplier (PH vs private median): "
            f"{textiles['equity_multiplier']:.2f}x"
        )
    else:
        print("  Private comparator unavailable: equity multiplier omitted")
    print(
        f"  Modeled diversion: "
        f"{diversion['additional_diversion_annual_tonnes_low']:,} - "
        f"{diversion['additional_diversion_annual_tonnes_high']:,} tonnes/year"
    )
    print(
        f"  Payback range: {diversion['payback_years_best_case']:.1f} - "
        f"{diversion['payback_years_worst_case']:.1f} years"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
DataHack 2026: Open-Access Gap Analysis

Compares nominal recycling accessibility (all collection points)
vs publicly-usable accessibility (public-only collection points).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent
MPL_CACHE_DIR = ROOT / ".cache" / "matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import folium
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
VIZ_DIR = ROOT / "visualizations"

EARTH_RADIUS_M = 6_371_000
SEVERE_PENALTY_THRESHOLD_M = 80
HIGH_PENALTY_THRESHOLD_M = 100

for directory in (PROCESSED_DIR, VIZ_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def parse_flat_count(value: object) -> int | None:
    """Extract integer flat count from values like '1 000 * as at 31.12.2025'."""
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


def categorize_distance(distance_m: float) -> str:
    if distance_m < 300:
        return "Well"
    if distance_m < 500:
        return "Mod"
    return "Under"


def min_haversine_distances_m(
    estate_lat: np.ndarray,
    estate_lon: np.ndarray,
    point_lat: np.ndarray,
    point_lon: np.ndarray,
) -> np.ndarray:
    """Vectorized nearest-neighbor distance from each estate to any point."""
    if len(point_lat) == 0:
        return np.full(len(estate_lat), np.inf, dtype=float)

    est_lat = np.radians(estate_lat)[:, None]
    est_lon = np.radians(estate_lon)[:, None]
    pts_lat = np.radians(point_lat)[None, :]
    pts_lon = np.radians(point_lon)[None, :]

    dlat = pts_lat - est_lat
    dlon = pts_lon - est_lon

    a = np.sin(dlat / 2.0) ** 2 + np.cos(est_lat) * np.cos(pts_lat) * np.sin(dlon / 2.0) ** 2
    distances = 2.0 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))
    return distances.min(axis=1)


def weighted_category_population(df: pd.DataFrame, category_col: str, pop_col: str) -> tuple[int, int, int]:
    well = int(df.loc[df[category_col] == "Well", pop_col].sum())
    mod = int(df.loc[df[category_col] == "Mod", pop_col].sum())
    under = int(df.loc[df[category_col] == "Under", pop_col].sum())
    return well, mod, under


print("=" * 70)
print("DATAHACK 2026: Open-Access Gap Analysis")
print("Nominal Coverage vs Publicly-Usable Coverage")
print("=" * 70)

print("\n[1/6] Loading and validating source data...")
collection_path = RAW_DIR / "collection_points.csv"
housing_path = RAW_DIR / "public_housing.json"
if not collection_path.exists():
    raise FileNotFoundError("Missing required file: data/raw/collection_points.csv")
if not housing_path.exists():
    raise FileNotFoundError("Missing required file: data/raw/public_housing.json")

df_cp = pd.read_csv(collection_path, encoding="utf-8-sig")
required_cp_columns = {"lat", "lgt", "accessibilty_notes"}
missing_cols = sorted(required_cp_columns - set(df_cp.columns))
if missing_cols:
    raise ValueError(f"collection_points.csv is missing columns: {', '.join(missing_cols)}")

df_cp["lat"] = pd.to_numeric(df_cp["lat"], errors="coerce")
df_cp["lon"] = pd.to_numeric(df_cp["lgt"], errors="coerce")
df_cp = df_cp.dropna(subset=["lat", "lon"]).copy()
df_cp["is_public"] = (
    df_cp["accessibilty_notes"].fillna("").astype(str).str.contains("For public use", case=False, na=False)
)

df_public = df_cp[df_cp["is_public"]].copy()
df_restricted = df_cp[~df_cp["is_public"]].copy()

with housing_path.open() as f:
    housing_rows = json.load(f)
if not isinstance(housing_rows, list):
    raise ValueError("public_housing.json must contain a JSON list")

estates = []
flat_parse_failures = 0
for row in housing_rows:
    try:
        lat = float(row.get("Estate Map Latitude"))
        lon = float(row.get("Estate Map Longitude"))
    except Exception:
        continue

    flats = parse_flat_count(row.get("No. of Rental Flats"))
    if flats is None:
        flat_parse_failures += 1

    estates.append(
        {
            "name": row.get("Estate Name", {}).get("en", "Unknown"),
            "district": row.get("District Name", {}).get("en", "Unknown"),
            "lat": lat,
            "lon": lon,
            "flats": flats,
            "pop": int(flats * 2.7) if flats is not None else np.nan,
        }
    )

df_est = pd.DataFrame(estates)
if df_est.empty:
    raise ValueError("No valid estate records found in public_housing.json")

if df_est["pop"].isna().any():
    pop_median = df_est["pop"].dropna().median()
    if pd.isna(pop_median):
        pop_median = 0
    df_est["pop"] = df_est["pop"].fillna(pop_median)

df_est["pop"] = pd.to_numeric(df_est["pop"], errors="coerce").fillna(0).astype(int)

print(f"  Collection points (valid coords): {len(df_cp):,}")
print(f"  Public-access points: {len(df_public):,} ({len(df_public) / len(df_cp) * 100:.1f}%)")
print(f"  Restricted points: {len(df_restricted):,} ({len(df_restricted) / len(df_cp) * 100:.1f}%)")
print(f"  Public housing estates: {len(df_est):,}")
print(f"  Population proxy total: {df_est['pop'].sum():,}")
print(f"  Rental-flat parse fallbacks: {flat_parse_failures:,}")

print("\n[2/6] Calculating nearest distances...")
est_lat = df_est["lat"].to_numpy(dtype=float)
est_lon = df_est["lon"].to_numpy(dtype=float)

df_est["dist_all"] = min_haversine_distances_m(
    est_lat,
    est_lon,
    df_cp["lat"].to_numpy(dtype=float),
    df_cp["lon"].to_numpy(dtype=float),
)
df_est["dist_public"] = min_haversine_distances_m(
    est_lat,
    est_lon,
    df_public["lat"].to_numpy(dtype=float),
    df_public["lon"].to_numpy(dtype=float),
)
df_est["openness_penalty"] = df_est["dist_public"] - df_est["dist_all"]

print("\n[3/6] Computing accessibility metrics...")
df_est["category_all"] = df_est["dist_all"].map(categorize_distance)
df_est["category_public"] = df_est["dist_public"].map(categorize_distance)

total_pop = int(df_est["pop"].sum())
well_all, mod_all, under_all = weighted_category_population(df_est, "category_all", "pop")
well_pub, mod_pub, under_pub = weighted_category_population(df_est, "category_public", "pop")

gap_well = well_all - well_pub
gap_under = under_pub - under_all
median_penalty = float(df_est["dist_public"].median() - df_est["dist_all"].median())
mean_penalty = float(df_est["openness_penalty"].mean())

severe = df_est[df_est["openness_penalty"] >= SEVERE_PENALTY_THRESHOLD_M].copy()
high = df_est[df_est["openness_penalty"] >= HIGH_PENALTY_THRESHOLD_M].copy()
severe_pop = int(severe["pop"].sum())
high_pop = int(high["pop"].sum())

print("\n" + "=" * 70)
print("KEY FINDINGS: Open-Access Gap")
print("=" * 70)
print("\nSCENARIO 1: All Collection Points (Nominal Coverage)")
print(f"  Well-served (<300m): {well_all:,} residents ({(well_all / total_pop * 100) if total_pop else 0:.1f}%)")
print(f"  Moderate (300-500m): {mod_all:,} residents ({(mod_all / total_pop * 100) if total_pop else 0:.1f}%)")
print(f"  Underserved (>500m): {under_all:,} residents ({(under_all / total_pop * 100) if total_pop else 0:.1f}%)")
print(f"  Median distance: {df_est['dist_all'].median():.0f}m")

print("\nSCENARIO 2: Public-Access Points Only (Usable Coverage)")
print(f"  Well-served (<300m): {well_pub:,} residents ({(well_pub / total_pop * 100) if total_pop else 0:.1f}%)")
print(f"  Moderate (300-500m): {mod_pub:,} residents ({(mod_pub / total_pop * 100) if total_pop else 0:.1f}%)")
print(f"  Underserved (>500m): {under_pub:,} residents ({(under_pub / total_pop * 100) if total_pop else 0:.1f}%)")
print(f"  Median distance: {df_est['dist_public'].median():.0f}m")

print("\nGAP SUMMARY")
print(f"  Median distance penalty: +{median_penalty:.0f}m")
print(f"  Mean openness penalty: {mean_penalty:.0f}m")
print(f"  Loss of well-served residents: {gap_well:,} ({(gap_well / total_pop * 100) if total_pop else 0:.1f}%)")
print(f"  Increase in underserved residents: {gap_under:,} ({(gap_under / total_pop * 100) if total_pop else 0:.1f}%)")
print(
    f"  Estates with severe penalty (>= {SEVERE_PENALTY_THRESHOLD_M}m): "
    f"{len(severe):,} estates, {severe_pop:,} residents"
)
print(
    f"  Estates with high penalty (>= {HIGH_PENALTY_THRESHOLD_M}m): "
    f"{len(high):,} estates, {high_pop:,} residents"
)

print("\n" + "=" * 70)
print("PROJECT HOOK")
print("=" * 70)
print(
    f'\n"Hong Kong has {len(df_cp):,} recycling collection points, but only '
    f'{len(df_public):,} ({len(df_public) / len(df_cp) * 100:.0f}%) are publicly accessible. '
    f'Citywide median distance rises by {median_penalty:.0f}m when restricted points are excluded, '
    f'and {len(severe):,} estates still face severe penalties of at least {SEVERE_PENALTY_THRESHOLD_M}m."\n'
)
print("=" * 70)

print("\n[4/6] Listing highest-penalty estates...")
top_penalty = df_est.nlargest(15, "openness_penalty")
print("\nTop 15 estates by openness penalty:")
print("-" * 70)
for _, row in top_penalty.iterrows():
    print(
        f"  {row['name'][:35]:35} | "
        f"All: {row['dist_all']:4.0f}m | Public: {row['dist_public']:4.0f}m | "
        f"Penalty: +{row['openness_penalty']:4.0f}m | Pop: {row['pop']:6,}"
    )

print("\n[5/6] Creating visualizations...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].hist(df_est["dist_all"], bins=40, alpha=0.7, label="All points", color="steelblue")
axes[0, 0].hist(df_est["dist_public"], bins=40, alpha=0.7, label="Public-only", color="salmon")
axes[0, 0].axvline(300, color="green", linestyle="--", linewidth=1)
axes[0, 0].axvline(500, color="orange", linestyle="--", linewidth=1)
axes[0, 0].set_xlabel("Distance (m)")
axes[0, 0].set_ylabel("Number of Estates")
axes[0, 0].set_title("Distance Distribution Comparison")
axes[0, 0].legend()

categories = ["Well\n(<300m)", "Moderate\n(300-500m)", "Under\n(>500m)"]
all_counts = [well_all / 1000, mod_all / 1000, under_all / 1000]
pub_counts = [well_pub / 1000, mod_pub / 1000, under_pub / 1000]
x = np.arange(len(categories))
width = 0.35
axes[0, 1].bar(x - width / 2, all_counts, width, label="All points", color="steelblue", alpha=0.8)
axes[0, 1].bar(x + width / 2, pub_counts, width, label="Public-only", color="salmon", alpha=0.8)
axes[0, 1].set_ylabel("Population (thousands)")
axes[0, 1].set_title("Accessibility by Scenario")
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels(categories)
axes[0, 1].legend()

axes[1, 0].hist(df_est["openness_penalty"], bins=40, edgecolor="black", color="slategray")
axes[1, 0].set_xlabel("Openness Penalty (m)")
axes[1, 0].set_ylabel("Number of Estates")
axes[1, 0].set_title("Penalty Distribution")
axes[1, 0].axvline(
    df_est["openness_penalty"].median(),
    color="red",
    linestyle="--",
    label=f"Median: {df_est['openness_penalty'].median():.0f}m",
)
axes[1, 0].legend()

top10 = df_est.nlargest(10, "openness_penalty")
axes[1, 1].barh(np.arange(len(top10)), top10["openness_penalty"], color="indianred")
axes[1, 1].set_yticks(np.arange(len(top10)))
axes[1, 1].set_yticklabels([str(name)[:25] for name in top10["name"]])
axes[1, 1].set_xlabel("Openness Penalty (m)")
axes[1, 1].set_title("Top 10 Estates by Penalty")
axes[1, 1].invert_yaxis()

plt.tight_layout()
plt.savefig(VIZ_DIR / "open_access_gap.png", dpi=300, bbox_inches="tight")
print("  Saved: visualizations/open_access_gap.png")

print("  Creating interactive map...")
m = folium.Map(location=[22.35, 114.15], zoom_start=11)

public_sample = df_public.sample(n=min(500, len(df_public)), random_state=42)
restricted_sample = df_restricted.sample(n=min(500, len(df_restricted)), random_state=42)

for _, row in public_sample.iterrows():
    folium.CircleMarker(
        [row["lat"], row["lon"]],
        radius=2,
        color="blue",
        fill=True,
        opacity=0.4,
        popup="Public access",
    ).add_to(m)

for _, row in restricted_sample.iterrows():
    folium.CircleMarker(
        [row["lat"], row["lon"]],
        radius=2,
        color="gray",
        fill=True,
        opacity=0.3,
        popup="Restricted",
    ).add_to(m)

for _, row in df_est.iterrows():
    penalty = row["openness_penalty"]
    if penalty >= HIGH_PENALTY_THRESHOLD_M:
        color = "red"
        radius = 10
    elif penalty >= 50:
        color = "orange"
        radius = 8
    else:
        color = "green"
        radius = 6

    popup = (
        f"<b>{row['name']}</b><br>"
        f"All points: {row['dist_all']:.0f}m<br>"
        f"Public-only: {row['dist_public']:.0f}m<br>"
        f"Penalty: +{row['openness_penalty']:.0f}m<br>"
        f"Population proxy: {row['pop']:,}"
    )
    folium.CircleMarker(
        [row["lat"], row["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=popup,
    ).add_to(m)

m.save(VIZ_DIR / "access_gap_map.html")
print("  Saved: visualizations/access_gap_map.html")

print("\n[6/6] Saving outputs...")
df_est.to_csv(PROCESSED_DIR / "estates_access_gap.csv", index=False)

summary = {
    "metadata": {
        "analysis_type": "open_access_gap",
        "severe_penalty_threshold_m": SEVERE_PENALTY_THRESHOLD_M,
        "high_penalty_threshold_m": HIGH_PENALTY_THRESHOLD_M,
    },
    "collection_points": {
        "total_points": int(len(df_cp)),
        "public_points": int(len(df_public)),
        "restricted_points": int(len(df_restricted)),
        "public_percentage": float(len(df_public) / len(df_cp) * 100),
    },
    "housing": {
        "estate_count": int(len(df_est)),
        "population_proxy_total": int(total_pop),
        "flat_parse_fallbacks": int(flat_parse_failures),
    },
    "scenario_all": {
        "median_distance_m": float(df_est["dist_all"].median()),
        "well_served_pop": int(well_all),
        "moderate_pop": int(mod_all),
        "underserved_pop": int(under_all),
    },
    "scenario_public_only": {
        "median_distance_m": float(df_est["dist_public"].median()),
        "well_served_pop": int(well_pub),
        "moderate_pop": int(mod_pub),
        "underserved_pop": int(under_pub),
    },
    "gap": {
        "median_distance_penalty_m": float(median_penalty),
        "mean_openness_penalty_m": float(mean_penalty),
        "well_served_loss": int(gap_well),
        "well_served_loss_pct": float((gap_well / total_pop * 100) if total_pop else 0),
        "underserved_increase": int(gap_under),
    },
    "severity": {
        "severe_estates_count": int(len(severe)),
        "severe_estates_population": int(severe_pop),
        "high_estates_count": int(len(high)),
        "high_estates_population": int(high_pop),
        "max_openness_penalty_m": float(df_est["openness_penalty"].max()),
    },
}

with (PROCESSED_DIR / "access_gap_stats.json").open("w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print(f"  Public-access share: {len(df_public) / len(df_cp) * 100:.1f}%")
print(f"  Median penalty: +{median_penalty:.0f}m")
print(f"  Severe estates (>= {SEVERE_PENALTY_THRESHOLD_M}m): {len(severe)}")
print("  Outputs:")
print("    - data/processed/estates_access_gap.csv")
print("    - data/processed/access_gap_stats.json")
print("    - visualizations/open_access_gap.png")
print("    - visualizations/access_gap_map.html")
print("=" * 70)

#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════
DataHack 2026 — FULL STRATEGY PIPELINE
══════════════════════════════════════════════════════════════════════════

THESIS:
  "Hong Kong's recycling infrastructure creates a double trap for low-value
   waste: glass, textiles, and hazardous materials lack market-driven
   collection AND 70-78% of their collection points are locked inside
   private estates. We map this 'complexity lockout' across 241 public
   housing estates and propose 10 multi-stream hubs to unlock 731
   tonnes/day of trapped waste."

PIPELINE:
  Phase 1 — ANALYZE & UNCOVER    → Baseline metrics + equity gap
  Phase 2 — INNOVATE & PROPOSE   → Greedy max-coverage hub placement
  Phase 3 — JUSTIFY & MEASURE    → Impact quantification + cost-benefit

DATASETS (5 sources — all from data.gov.hk):
  1. Recyclable Collection Points         (8,858 points)
  2. Public Housing Estates               (241 estates)
  3. Open Space DB of Recycling Stations  (12 GREEN@ stations)
  4. Waste Management Facilities          (24 facilities)
  5. Database of Private Buildings in HK  (765 buildings)

OUTPUTS:
  data/processed/
    baseline_metrics.json         — per-stream current state
    optimized_hubs.csv            — 10 hub locations + metadata
    estates_full_analysis.csv     — 241 estates with per-stream distances
    impact_report.json            — before/after + cost-benefit

  visualizations/
    01_landfill_composition.png   — what goes to landfill + lockout paradox
    02_stream_inequality.png      — public vs total by stream + equity gap
    03_textiles_deep_dive.png     — worst stream: histogram + by district
    04_hub_impact.png             — before/after coverage comparison
    05_interactive_map.html       — full map with estates, hubs, facilities

══════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
GEO = ROOT / "data" / "geo"
OUT = ROOT / "data" / "processed"
VIZ = ROOT / "visualizations"

for d in (OUT, VIZ):
    d.mkdir(parents=True, exist_ok=True)

CACHE = ROOT / ".cache" / "matplotlib"
CACHE.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(CACHE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

try:
    import geopandas as gpd
    HAS_GEO = True
except ImportError:
    HAS_GEO = False
    print("  [WARN] geopandas not installed — skipping geo datasets")

try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("  [WARN] folium not installed — skipping interactive map")

# ══════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════
EARTH_R = 6_371_000  # metres
SERVICE_RADIUS = 800  # hub catchment (metres)
NUM_HUBS = 10

# Focus streams: the "trapped waste" trio + supporting streams
FOCUS_STREAMS = {
    "Glass Bottles":  {"col": "glass",     "tpd": 211, "recovery": 5,  "color": "#FF6F00"},
    "Clothes":        {"col": "textiles",  "tpd": 388, "recovery": 11, "color": "#E53935"},
    "Fluorescent Lamp":             {"col": "hazardous", "tpd": 50,  "recovery": 30, "color": "#AB47BC"},
    "Rechargeable Batteries":       {"col": "batteries", "tpd": 40,  "recovery": 30, "color": "#FFC107"},
    "Small Electrical and Electronic Equipment":
                      {"col": "ewaste",    "tpd": 42,  "recovery": 45, "color": "#E91E63"},
}

# Full MSW composition (EPD 2022, Plate 2.8 — tonnes per day)
MSW_COMPOSITION = {
    "Food Waste": 3495, "Plastics": 2369, "Paper": 2244,
    "Textiles": 388, "Metals": 248, "Glass": 211,
    "Wood": 207, "Household Hazardous": 132, "Others": 1834,
}

# Recovery rates (EPD 2022-2023 reports)
RECOVERY_RATES = {
    "Food Waste": 3, "Paper": 43, "Plastics": 11, "Metals": 92,
    "Glass": 5, "Textiles": 11, "Wood": 10, "Household Hazardous": 30,
}


# ══════════════════════════════════════════════════════════════════════
# SPATIAL HELPERS
# ══════════════════════════════════════════════════════════════════════
def haversine_min(lat1, lon1, lat2, lon2):
    """Nearest-neighbour distance from each point in set 1 to set 2."""
    if len(lat2) == 0:
        return np.full(len(lat1), np.inf)
    la1 = np.radians(lat1)[:, None]
    lo1 = np.radians(lon1)[:, None]
    la2 = np.radians(lat2)[None, :]
    lo2 = np.radians(lon2)[None, :]
    d = la2 - la1
    dl = lo2 - lo1
    a = np.sin(d / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin(dl / 2) ** 2
    return (2 * EARTH_R * np.arcsin(np.sqrt(a))).min(axis=1)


def parse_flats(val):
    """Extract integer flat count from messy housing JSON."""
    if isinstance(val, dict):
        val = val.get("en") or val.get("zh-Hant") or ""
    if not isinstance(val, str):
        return None
    head = val.split("as at")[0]
    m = re.search(r"\d[\d ,]*", head)
    if not m:
        return None
    digits = re.sub(r"[^\d]", "", m.group(0))
    return int(digits) if digits else None


# ══════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════
def load_data():
    """Load and clean all five datasets."""
    print("=" * 70)
    print("LOADING DATASETS")
    print("=" * 70)

    # ── 1. Collection Points ──────────────────────────────────────
    cp = pd.read_csv(RAW / "collection_points.csv", encoding="utf-8-sig")
    cp["lat"] = pd.to_numeric(cp["lat"], errors="coerce")
    cp["lon"] = pd.to_numeric(cp["lgt"], errors="coerce")
    cp = cp.dropna(subset=["lat", "lon"]).copy()
    cp["is_public"] = (
        cp["accessibilty_notes"]
        .fillna("")
        .str.contains("For public use", case=False)
    )
    print(f"  [1] Collection points:  {len(cp):,} ({cp['is_public'].sum():,} public)")

    # ── 2. Public Housing ─────────────────────────────────────────
    with (RAW / "public_housing.json").open() as f:
        raw_housing = json.load(f)
    rows = []
    for r in raw_housing:
        try:
            lat = float(r["Estate Map Latitude"])
            lon = float(r["Estate Map Longitude"])
        except Exception:
            continue
        flats = parse_flats(r.get("No. of Rental Flats"))
        rows.append({
            "name": r.get("Estate Name", {}).get("en", "Unknown"),
            "district": r.get("District Name", {}).get("en", "Unknown"),
            "lat": lat, "lon": lon,
            "flats": flats,
            "pop": int(flats * 2.7) if flats else 0,
        })
    est = pd.DataFrame(rows)
    print(f"  [2] Public housing:     {len(est)} estates, {est['pop'].sum():,} residents")

    # ── 3. Private Buildings ──────────────────────────────────────
    pb_lat, pb_lon = np.array([]), np.array([])
    if HAS_GEO:
        gml = list((GEO / "private_buildings").glob("*.gml"))
        if gml:
            gdf = gpd.read_file(gml[0])
            pb_lat = gdf.geometry.y.values
            pb_lon = gdf.geometry.x.values
            print(f"  [3] Private buildings:  {len(gdf)}")
        else:
            print("  [3] Private buildings:  NOT FOUND")
    else:
        print("  [3] Private buildings:  SKIPPED (no geopandas)")

    # ── 4. GREEN@ Stations ────────────────────────────────────────
    rs_lat, rs_lon, rs_names = np.array([]), np.array([]), []
    if HAS_GEO:
        gdb = list((GEO / "recycling_stations").glob("*.gdb"))
        if gdb:
            grs = gpd.read_file(gdb[0]).to_crs(epsg=4326)
            c = grs.geometry.centroid
            rs_lat, rs_lon = c.y.values, c.x.values
            rs_names = list(grs["BLDG_ENGNM"])
            print(f"  [4] GREEN@ stations:    {len(grs)}")

    # ── 5. Waste Facilities ───────────────────────────────────────
    wm = None
    if HAS_GEO:
        gdb = list((GEO / "waste_facilities").glob("*.gdb"))
        if gdb:
            wm = gpd.read_file(gdb[0])
            print(f"  [5] Waste facilities:   {len(wm)}")

    return cp, est, pb_lat, pb_lon, rs_lat, rs_lon, rs_names, wm


# ══════════════════════════════════════════════════════════════════════
# PHASE 1 — ANALYZE & UNCOVER
# ══════════════════════════════════════════════════════════════════════
def phase1_analyze(cp, est, pb_lat, pb_lon):
    """Compute baseline per-stream metrics + equity gap."""
    print("\n" + "=" * 70)
    print("PHASE 1: ANALYZE & UNCOVER")
    print("=" * 70)

    el, eo = est["lat"].values, est["lon"].values
    baseline = {}

    # ── Per-stream lockout and access ─────────────────────────────
    print(f"\n{'Stream':<14} {'Lock%':>6} {'Rec%':>5} {'tpd':>5}"
          f" {'Med PH':>7} {'Med PB':>7} {'Gap':>5}"
          f" {'E>500':>6} {'Pop>500':>9}")
    print("-" * 75)

    for stream, info in FOCUS_STREAMS.items():
        col = info["col"]
        mask = cp["waste_type"].str.contains(stream, case=False, na=False)
        pub = cp[mask & cp["is_public"]]
        total = mask.sum()
        lockout = 1 - len(pub) / total if total else 0

        d_est = haversine_min(el, eo, pub["lat"].values, pub["lon"].values)
        est[f"dist_{col}"] = d_est

        d_pb = (
            haversine_min(pb_lat, pb_lon,
                          cp.loc[mask, "lat"].values,
                          cp.loc[mask, "lon"].values)
            if len(pb_lat) > 0
            else np.array([0])
        )

        over500 = int((d_est > 500).sum())
        pop500 = int(est.loc[d_est > 500, "pop"].sum())
        med_est = float(np.median(d_est))
        med_pb = float(np.median(d_pb)) if len(d_pb) > 0 else 0
        gap = round(med_est / max(med_pb, 1), 1)

        baseline[col] = dict(
            stream=stream, total=int(total), public=int(len(pub)),
            lockout=round(lockout * 100, 1),
            tpd=info["tpd"], recovery=info["recovery"],
            med_est=round(med_est), med_pb=round(med_pb), gap=gap,
            over500=over500, pop500=pop500,
        )

        print(f"  {col:<12} {lockout*100:>5.1f}% {info['recovery']:>4}%"
              f" {info['tpd']:>5} {med_est:>6.0f}m {med_pb:>6.0f}m"
              f" {gap:>4.1f}x {over500:>6} {pop500:>9,}")

    # ── Full access breakdown (all 12 streams) ────────────────────
    print("\n  All-stream public access breakdown:")
    all_streams = {
        "Metals": "Metals", "Paper": "Paper", "Plastics": "Plastics",
        "Glass Bottles": "Glass", "Food Waste": "Food Waste",
        "Clothes": "Textiles", "Rechargeable Batteries": "Batteries",
        "Fluorescent Lamp": "Hazardous", "Small Electrical": "E-Waste",
        "Beverage Cartons": "Cartons",
    }
    stream_breakdown = {}
    for pat, label in all_streams.items():
        m = cp["waste_type"].str.contains(pat, case=False, na=False)
        t = m.sum()
        p = (m & cp["is_public"]).sum()
        lock = (t - p) / t * 100 if t else 0
        stream_breakdown[label] = dict(total=int(t), public=int(p), lockout=round(lock, 1))
        print(f"    {label:<14} {t:>6,} total | {p:>6,} public | {lock:>5.1f}% locked")

    # Save
    with (OUT / "baseline_metrics.json").open("w") as f:
        json.dump({"focus_streams": baseline, "all_streams": stream_breakdown},
                  f, indent=2)
    print(f"\n  → Saved: {OUT / 'baseline_metrics.json'}")

    return baseline


# ══════════════════════════════════════════════════════════════════════
# PHASE 2 — INNOVATE & PROPOSE
# ══════════════════════════════════════════════════════════════════════
def phase2_optimize(est):
    """Greedy max-coverage hub placement algorithm."""
    print("\n" + "=" * 70)
    print("PHASE 2: INNOVATE & PROPOSE — Greedy Max-Coverage Placement")
    print("=" * 70)

    el, eo = est["lat"].values, est["lon"].values

    # Stream weights proportional to landfill tonnage
    weights = {info["col"]: info["tpd"] for info in FOCUS_STREAMS.values()}
    wt = sum(weights.values())

    # Current best distance per stream (starts at baseline)
    cur = {col: est[f"dist_{col}"].values.copy() for col in weights}

    candidates = set(est.index)
    hubs = []

    for n in range(1, NUM_HUBS + 1):
        best_score, best_idx = -1, None

        for idx in candidates:
            clat = est.at[idx, "lat"]
            clon = est.at[idx, "lon"]
            d = haversine_min(el, eo, np.array([clat]), np.array([clon]))

            score = 0
            for col, w in weights.items():
                new = np.minimum(cur[col], d)
                was_far = cur[col] > 500
                now_ok = new <= SERVICE_RADIUS
                score += est.loc[was_far & now_ok, "pop"].sum() * (w / wt)

            if score > best_score:
                best_score, best_idx = score, idx

        # Lock in this hub
        row = est.loc[best_idx]
        hd = haversine_min(el, eo,
                           np.array([row["lat"]]), np.array([row["lon"]]))
        for col in weights:
            cur[col] = np.minimum(cur[col], hd)

        served = est[hd <= SERVICE_RADIUS]
        hubs.append(dict(
            hub_id=n, name=row["name"], district=row["district"],
            lat=float(row["lat"]), lon=float(row["lon"]),
            pop=int(row["pop"]),
            estates_in_800m=int(len(served)),
            pop_in_800m=int(served["pop"].sum()),
            coverage_gain=round(best_score),
        ))
        candidates.discard(best_idx)

    df_hubs = pd.DataFrame(hubs)

    print(f"\n  {'#':>2} {'Estate':<28} {'District':<14}"
          f" {'Estates 800m':>12} {'Pop 800m':>9}")
    print("  " + "-" * 70)
    for _, h in df_hubs.iterrows():
        print(f"  {h['hub_id']:>2} {h['name']:<28} {h['district']:<14}"
              f" {h['estates_in_800m']:>12} {h['pop_in_800m']:>9,}")

    total_pop = df_hubs["pop_in_800m"].sum()
    print(f"\n  TOTAL CATCHMENT: {total_pop:,} residents within 800 m of a hub")

    df_hubs.to_csv(OUT / "optimized_hubs.csv", index=False)
    print(f"  → Saved: {OUT / 'optimized_hubs.csv'}")

    return df_hubs


# ══════════════════════════════════════════════════════════════════════
# PHASE 3 — JUSTIFY & MEASURE
# ══════════════════════════════════════════════════════════════════════
def phase3_impact(est, df_hubs, baseline, wm):
    """Quantify before/after impact + cost-benefit."""
    print("\n" + "=" * 70)
    print("PHASE 3: JUSTIFY & MEASURE")
    print("=" * 70)

    el, eo = est["lat"].values, est["lon"].values
    hub_d = haversine_min(el, eo,
                          df_hubs["lat"].values, df_hubs["lon"].values)

    # ── Per-stream before/after ───────────────────────────────────
    impact = {}
    print(f"\n  {'Stream':<13} {'Bef>500':>8} {'Aft>500':>8}"
          f" {'Δ Est':>6} {'Pop saved':>10}"
          f" {'Med bef':>8} {'Med aft':>8}")
    print("  " + "-" * 65)

    for info in FOCUS_STREAMS.values():
        col = info["col"]
        bef = est[f"dist_{col}"].values
        aft = np.minimum(bef, hub_d)

        b500 = int((bef > 500).sum())
        a500 = int((aft > 500).sum())
        pb = int(est.loc[bef > 500, "pop"].sum())
        pa = int(est.loc[aft > 500, "pop"].sum())

        impact[col] = dict(
            before_500=b500, after_500=a500, delta=b500 - a500,
            pop_saved=pb - pa,
            med_before=round(float(np.median(bef))),
            med_after=round(float(np.median(aft))),
        )

        print(f"  {col:<13} {b500:>8} {a500:>8}"
              f" {b500-a500:>6} {pb-pa:>10,}"
              f" {np.median(bef):>7.0f}m {np.median(aft):>7.0f}m")

    # ── Cost-benefit ──────────────────────────────────────────────
    COST_LOW, COST_HIGH = 2_000_000, 5_000_000  # HK$ per hub
    GATE_FEE = 365  # HK$/tonne at landfill

    divert_low = 36.5   # tpd (+5% recovery on focus streams)
    divert_high = 73.1  # tpd (+10%)

    save_low = divert_low * GATE_FEE * 365
    save_high = divert_high * GATE_FEE * 365

    payback_best = (COST_LOW * NUM_HUBS) / save_high
    payback_worst = (COST_HIGH * NUM_HUBS) / save_low

    cost = dict(
        hubs=NUM_HUBS,
        cost_per_hub=f"HK${COST_LOW/1e6:.0f}–{COST_HIGH/1e6:.0f}M",
        total_capex=f"HK${COST_LOW*NUM_HUBS/1e6:.0f}–{COST_HIGH*NUM_HUBS/1e6:.0f}M",
        diversion_tpd=f"{divert_low}–{divert_high}",
        diversion_annual=f"{divert_low*365:,.0f}–{divert_high*365:,.0f} tonnes",
        landfill_savings=f"HK${save_low/1e6:.1f}–{save_high/1e6:.1f}M/year",
        payback_years=f"{payback_best:.1f}–{payback_worst:.1f}",
    )

    print(f"""
  ┌─────────────────────────────────────────────────────┐
  │  COST-BENEFIT SUMMARY                               │
  ├─────────────────────────────────────────────────────┤
  │  Capital:   {cost['total_capex']:<38} │
  │  Diversion: {cost['diversion_annual']:<38} │
  │  Savings:   {cost['landfill_savings']:<38} │
  │  Payback:   {cost['payback_years']:<38} │
  │                                                     │
  │  Compare: 1 GREEN@ station = HK$20-30M              │
  │  Our 10 micro-hubs = same budget, 10× coverage      │
  └─────────────────────────────────────────────────────┘""")

    # ── Nearest RTS per hub ───────────────────────────────────────
    if wm is not None:
        rts = wm[wm["SEARCH01_EN"] == "REFUSE TRANSFER STATION"]
        print(f"\n  LOGISTICS — Nearest Refuse Transfer Station:")
        for _, h in df_hubs.iterrows():
            d = haversine_min(
                np.array([h["lat"]]), np.array([h["lon"]]),
                rts["LATITUDE"].astype(float).values,
                rts["LONGITUDE"].astype(float).values,
            )
            nearest = rts.iloc[d.argmin()]
            print(f"    Hub {h['hub_id']:>2} → {nearest['NAME_EN']:<40} ({d.min():,.0f}m)")

    # ── Save ──────────────────────────────────────────────────────
    report = dict(baseline=baseline, impact=impact, cost_benefit=cost)
    with (OUT / "impact_report.json").open("w") as f:
        json.dump(report, f, indent=2, default=str)

    est.to_csv(OUT / "estates_full_analysis.csv", index=False)
    print(f"\n  → Saved: {OUT / 'impact_report.json'}")
    print(f"  → Saved: {OUT / 'estates_full_analysis.csv'}")

    return impact, cost


# ══════════════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════
def viz_01_landfill(cp):
    """Panel 1: MSW composition + lockout-recovery paradox."""
    fig, axes = plt.subplots(1, 3, figsize=(22, 8))

    # Left — what goes to landfill
    cats = list(MSW_COMPOSITION.keys())
    vals = list(MSW_COMPOSITION.values())
    total = sum(vals)
    cmap = {"Textiles": "#E53935", "Glass": "#FF6F00",
            "Household Hazardous": "#AB47BC", "Food Waste": "#66BB6A"}
    colors = [cmap.get(c, "#B0BEC5") for c in cats]

    axes[0].barh(range(len(cats)), vals, color=colors, edgecolor="white")
    axes[0].set_yticks(range(len(cats)))
    axes[0].set_yticklabels(cats, fontsize=11)
    for i, v in enumerate(vals):
        pct = v / total * 100
        w = "bold" if cats[i] in cmap else "normal"
        axes[0].text(v + 60, i, f"{v:,} tpd ({pct:.1f}%)",
                     va="center", fontsize=10, fontweight=w)
    axes[0].set_xlabel("Tonnes per Day", fontsize=12)
    axes[0].set_title("What Goes to HK Landfills\n(MSW 2022, EPD)", fontsize=13, fontweight="bold")
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, 4800)

    # Middle — lockout vs recovery
    focus = ["Food Waste", "Paper", "Plastics", "Metals",
             "Glass", "Textiles", "Household Hazardous"]
    lockouts = []
    is_pub = cp["is_public"]
    stream_map = {
        "Food Waste": "Food Waste", "Paper": "Paper", "Plastics": "Plastics",
        "Metals": "Metals", "Glass": "Glass Bottles",
        "Textiles": "Clothes", "Household Hazardous": "Fluorescent Lamp",
    }
    for f_ in focus:
        pat = stream_map[f_]
        m = cp["waste_type"].str.contains(pat, case=False, na=False)
        t = m.sum()
        p = (m & is_pub).sum()
        lockouts.append((t - p) / t * 100 if t else 0)

    rec = [RECOVERY_RATES.get(f_, 0) for f_ in focus]
    x = np.arange(len(focus))
    w = 0.35
    axes[1].bar(x - w / 2, rec, w, label="Recovery %", color="#4CAF50", alpha=.85)
    axes[1].bar(x + w / 2, lockouts, w, label="Lockout %", color="#E53935", alpha=.85)
    for i, (r_, l_) in enumerate(zip(rec, lockouts)):
        axes[1].text(i - w / 2, r_ + 2, f"{r_:.0f}%", ha="center", fontsize=8, color="#2E7D32")
        axes[1].text(i + w / 2, l_ + 2, f"{l_:.0f}%", ha="center", fontsize=8, color="#B71C1C")
    axes[1].set_xticks(x)
    labels = [c.replace("Household Hazardous", "Hazardous\n(Lamps)") for c in focus]
    axes[1].set_xticklabels(labels, fontsize=9, rotation=25, ha="right")
    axes[1].set_ylabel("Percentage", fontsize=12)
    axes[1].set_title("The Lockout-Recovery Paradox\nHigher lockout → Lower recovery",
                       fontsize=13, fontweight="bold")
    axes[1].legend(fontsize=10)
    axes[1].set_ylim(0, 105)

    # Right — bubble: lockout vs landfill volume
    bdata = {
        "Food Waste":  (26.1, 3495,  3,  "#66BB6A"),
        "Plastics":    (50.1, 2369, 11,  "#B0BEC5"),
        "Paper":       (50.7, 2244, 43,  "#B0BEC5"),
        "Metals":      (48.3,  248, 92,  "#B0BEC5"),
        "Glass":       (75.8,  211,  5,  "#FF6F00"),
        "Textiles":    (77.5,  388, 11,  "#E53935"),
        "Hazardous":   (68.9,  132, 30,  "#AB47BC"),
    }
    for name, (lk, tpd, rec_, clr) in bdata.items():
        sz = max(200, (100 - rec_) * 15)
        axes[2].scatter(lk, tpd, s=sz, c=clr, alpha=.75, edgecolors="k", lw=1, zorder=5)
        oy = 120 if name != "Glass" else -140
        axes[2].annotate(f"{name}\n({rec_}% recovered)", (lk, tpd),
                          xytext=(lk, tpd + oy), ha="center", fontsize=9,
                          fontweight="bold" if clr != "#B0BEC5" else "normal",
                          arrowprops=dict(arrowstyle="-", color="gray", lw=.5)
                          if abs(oy) > 100 else None)
    axes[2].axvspan(65, 82, alpha=.07, color="red")
    axes[2].text(73.5, 3800, "HIGH LOCKOUT\nZONE", ha="center",
                  fontsize=11, color="#C62828", fontweight="bold", alpha=.5)
    axes[2].set_xlabel("Infrastructure Lockout Rate (%)", fontsize=12)
    axes[2].set_ylabel("Daily Landfill Volume (tpd)", fontsize=12)
    axes[2].set_title("Why Glass, Textiles & Hazardous?\nHigh lockout + Low recovery = Trapped waste",
                       fontsize=13, fontweight="bold")
    axes[2].set_xlim(15, 85)
    axes[2].set_ylim(-100, 4500)

    plt.tight_layout(w_pad=3)
    fig.savefig(VIZ / "01_landfill_composition.png", dpi=300, bbox_inches="tight")
    print(f"  → {VIZ / '01_landfill_composition.png'}")


def viz_02_inequality(cp, est, pb_lat, pb_lon):
    """Panel 2: Public vs total by stream + equity gap."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Left — total vs public point counts
    all_streams = [
        ("Metals|Paper|Plastics", "Basic\n(Paper/Metal/Plastic)", "#4CAF50"),
        ("Food Waste",             "Food Waste",                  "#8BC34A"),
        ("Rechargeable Batteries", "Batteries",                   "#FFC107"),
        ("Glass Bottles",          "Glass",                       "#FF9800"),
        ("Fluorescent Lamp",       "Hazardous",                   "#FF5722"),
        ("Small Electrical",       "E-Waste",                     "#E91E63"),
        ("Clothes",                "Textiles",                    "#9C27B0"),
    ]
    labels, totals, publics, pcts, clrs = [], [], [], [], []
    for pat, lab, clr in all_streams:
        m = cp["waste_type"].str.contains(pat, case=False, na=False)
        t, p = m.sum(), (m & cp["is_public"]).sum()
        labels.append(lab); totals.append(t); publics.append(p)
        pcts.append(p / t * 100 if t else 0); clrs.append(clr)

    y = np.arange(len(labels))
    axes[0].barh(y, totals, .4, label="Total", color=[c + "40" for c in clrs],
                 edgecolor=clrs, lw=1.5)
    axes[0].barh(y - .4, publics, .4, label="Public", color=clrs, alpha=.85)
    for i in range(len(labels)):
        axes[0].text(totals[i] + 50, i, f"{totals[i]:,}", va="center", fontsize=9, color="gray")
        axes[0].text(publics[i] + 50, i - .4, f"{publics[i]:,} ({pcts[i]:.0f}%)",
                     va="center", fontsize=9, fontweight="bold")
    axes[0].set_yticks(y - .2); axes[0].set_yticklabels(labels, fontsize=10)
    axes[0].set_xlabel("Collection Points", fontsize=11)
    axes[0].set_title("Total vs Public Points by Stream", fontsize=13, fontweight="bold")
    axes[0].legend(loc="lower right"); axes[0].invert_yaxis()

    # Right — median distance comparison
    el, eo = est["lat"].values, est["lon"].values
    meds_est, meds_pb = [], []
    for pat, _, _ in all_streams:
        pub = cp[cp["waste_type"].str.contains(pat, case=False, na=False) & cp["is_public"]]
        allp = cp[cp["waste_type"].str.contains(pat, case=False, na=False)]
        de = haversine_min(el, eo, pub["lat"].values, pub["lon"].values)
        dp = (haversine_min(pb_lat, pb_lon, allp["lat"].values, allp["lon"].values)
              if len(pb_lat) > 0 else np.array([0]))
        meds_est.append(np.median(de)); meds_pb.append(np.median(dp))

    y2 = np.arange(len(all_streams))
    axes[1].barh(y2 - .2, meds_est, .35, label="Public Housing → public pts",
                 color="#E53935", alpha=.85)
    axes[1].barh(y2 + .2, meds_pb, .35, label="Private Bldgs → all pts",
                 color="#1E88E5", alpha=.85)
    for i in range(len(all_streams)):
        axes[1].text(meds_est[i] + 8, i - .2, f"{meds_est[i]:.0f}m",
                     va="center", fontsize=9, fontweight="bold", color="#C62828")
        axes[1].text(meds_pb[i] + 8, i + .2, f"{meds_pb[i]:.0f}m",
                     va="center", fontsize=9, color="#1565C0")
    axes[1].set_yticks(y2)
    axes[1].set_yticklabels([s[1] for s in all_streams], fontsize=10)
    axes[1].set_xlabel("Median Distance (m)", fontsize=11)
    axes[1].set_title("Equity Gap: Public Housing vs Private",
                       fontsize=13, fontweight="bold")
    axes[1].legend(loc="lower right", fontsize=9)
    axes[1].invert_yaxis()
    axes[1].axvline(300, color="gray", ls="--", alpha=.4)

    plt.tight_layout()
    fig.savefig(VIZ / "02_stream_inequality.png", dpi=300, bbox_inches="tight")
    print(f"  → {VIZ / '02_stream_inequality.png'}")


def viz_03_textiles(est):
    """Panel 3: Textiles deep dive."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    d = est["dist_textiles"].values

    axes[0].hist(d, bins=30, color="#9C27B0", alpha=.8, edgecolor="white")
    axes[0].axvline(500, color="red", ls="--", lw=2, label="500m threshold")
    axes[0].axvline(np.median(d), color="orange", lw=2, label=f"Median: {np.median(d):.0f}m")
    axes[0].axvspan(500, d.max() + 50, alpha=.1, color="red")
    n500 = (d > 500).sum()
    p500 = est.loc[d > 500, "pop"].sum()
    axes[0].text(700, axes[0].get_ylim()[1] * .75,
                 f"{n500} estates\n>500 m\n({p500/1000:.0f}K residents)",
                 fontsize=12, fontweight="bold", color="#C62828", ha="center")
    axes[0].set_xlabel("Distance to nearest PUBLIC textile point (m)", fontsize=11)
    axes[0].set_ylabel("Estates", fontsize=11)
    axes[0].set_title("Textile Recycling: Distance Distribution", fontsize=13, fontweight="bold")
    axes[0].legend(fontsize=10)

    # By district
    rows = []
    for dist in est["district"].unique():
        sub = est[est["district"] == dist]
        rows.append(dict(district=dist, median=sub["dist_textiles"].median(),
                         over500=(sub["dist_textiles"] > 500).sum(),
                         total=len(sub)))
    ddf = pd.DataFrame(rows).sort_values("median")
    clr = ["#C62828" if m > 500 else "#FF9800" if m > 300 else "#4CAF50"
           for m in ddf["median"]]
    axes[1].barh(range(len(ddf)), ddf["median"], color=clr, alpha=.85)
    axes[1].set_yticks(range(len(ddf)))
    axes[1].set_yticklabels(ddf["district"], fontsize=9)
    for i, (_, r) in enumerate(ddf.iterrows()):
        axes[1].text(r["median"] + 12, i,
                     f'{r["median"]:.0f}m ({r["over500"]}/{r["total"]})',
                     va="center", fontsize=8)
    axes[1].axvline(300, color="green", ls="--", alpha=.4)
    axes[1].axvline(500, color="red", ls="--", alpha=.4)
    axes[1].set_xlabel("Median Distance (m)", fontsize=11)
    axes[1].set_title("By District (estates >500m / total)", fontsize=13, fontweight="bold")
    axes[1].invert_yaxis()

    plt.tight_layout()
    fig.savefig(VIZ / "03_textiles_deep_dive.png", dpi=300, bbox_inches="tight")
    print(f"  → {VIZ / '03_textiles_deep_dive.png'}")


def viz_04_impact(est, df_hubs, impact):
    """Panel 4: Before/after hub impact."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Left — before/after bar chart per stream
    streams = list(impact.keys())
    bef = [impact[s]["before_500"] for s in streams]
    aft = [impact[s]["after_500"] for s in streams]
    x = np.arange(len(streams))
    w = .35

    axes[0].bar(x - w / 2, bef, w, label="BEFORE (current)", color="#E53935", alpha=.8)
    axes[0].bar(x + w / 2, aft, w, label="AFTER (10 hubs)", color="#4CAF50", alpha=.8)
    for i in range(len(streams)):
        axes[0].text(i - w / 2, bef[i] + 1, str(bef[i]), ha="center", fontsize=10)
        axes[0].text(i + w / 2, aft[i] + 1, str(aft[i]), ha="center", fontsize=10)
        delta = bef[i] - aft[i]
        if delta > 0:
            axes[0].annotate(f"−{delta}", (i, max(bef[i], aft[i]) + 5),
                              fontsize=11, fontweight="bold", color="#2E7D32", ha="center")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([s.capitalize() for s in streams], fontsize=11)
    axes[0].set_ylabel("Estates >500 m from public point", fontsize=11)
    axes[0].set_title("Estates Beyond 500m: Before vs After",
                       fontsize=13, fontweight="bold")
    axes[0].legend(fontsize=10)

    # Right — population saved
    saved = [impact[s]["pop_saved"] for s in streams]
    clr = ["#E53935" if s == "textiles" else "#FF6F00" if s == "glass"
           else "#AB47BC" if s == "hazardous" else "#FFC107" if s == "batteries"
           else "#E91E63" for s in streams]
    axes[1].bar(range(len(streams)), saved, color=clr, alpha=.85, edgecolor="white")
    for i, v in enumerate(saved):
        if v > 0:
            axes[1].text(i, v + 3000, f"{v:,}", ha="center", fontsize=11, fontweight="bold")
    axes[1].set_xticks(range(len(streams)))
    axes[1].set_xticklabels([s.capitalize() for s in streams], fontsize=11)
    axes[1].set_ylabel("Residents removed from >500m zone", fontsize=11)
    axes[1].set_title("Population Saved by 10 Hubs",
                       fontsize=13, fontweight="bold")
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))

    plt.tight_layout()
    fig.savefig(VIZ / "04_hub_impact.png", dpi=300, bbox_inches="tight")
    print(f"  → {VIZ / '04_hub_impact.png'}")


def viz_05_map(cp, est, df_hubs, rs_lat, rs_lon, rs_names, wm):
    """Interactive Folium map with all layers."""
    if not HAS_FOLIUM:
        print("  [SKIP] folium not installed")
        return

    m = folium.Map(location=[22.35, 114.15], zoom_start=11, tiles="CartoDB positron")

    # Estates coloured by textile distance
    for _, r in est.iterrows():
        td = r["dist_textiles"]
        if td > 1000:    clr, sz = "#C62828", 10
        elif td > 500:   clr, sz = "#FF6F00", 8
        elif td > 300:   clr, sz = "#FDD835", 6
        else:            clr, sz = "#4CAF50", 5
        popup = (f"<b>{r['name']}</b><br>District: {r['district']}<br>"
                 f"Pop: {r['pop']:,}<hr>"
                 f"Textiles: <b>{r['dist_textiles']:.0f}m</b><br>"
                 f"Glass: {r['dist_glass']:.0f}m<br>"
                 f"Hazardous: {r['dist_hazardous']:.0f}m")
        folium.CircleMarker([r["lat"], r["lon"]], radius=sz, color=clr,
                             fill=True, fill_opacity=.7, popup=popup).add_to(m)

    # Proposed hubs
    for _, h in df_hubs.iterrows():
        folium.Marker(
            [h["lat"], h["lon"]],
            icon=folium.Icon(color="blue", icon="star", prefix="fa"),
            popup=(f"<b>PROPOSED HUB {h['hub_id']}</b><br>{h['name']}<br>"
                   f"{h['district']}<br>Catchment: {h['pop_in_800m']:,}")
        ).add_to(m)
        folium.Circle([h["lat"], h["lon"]], radius=SERVICE_RADIUS,
                       color="blue", fill=False, weight=1, dash_array="5").add_to(m)

    # Existing public textile points
    tex = cp[cp["waste_type"].str.contains("Clothes", case=False, na=False)
             & cp["is_public"]]
    for _, p in tex.iterrows():
        folium.CircleMarker([p["lat"], p["lon"]], radius=3, color="#9C27B0",
                             fill=True, fill_opacity=.4,
                             popup="Public textile recycling").add_to(m)

    # GREEN@ stations
    for i in range(len(rs_lat)):
        folium.Marker(
            [rs_lat[i], rs_lon[i]],
            icon=folium.Icon(color="green", icon="recycle", prefix="fa"),
            popup=f"<b>{rs_names[i]}</b><br>GREEN@ Premium Station"
        ).add_to(m)

    # Waste facilities
    if wm is not None:
        for _, f_ in wm.iterrows():
            folium.CircleMarker(
                [float(f_["LATITUDE"]), float(f_["LONGITUDE"])],
                radius=6, color="#795548", fill=True, fill_opacity=.6,
                popup=f"<b>{f_['NAME_EN']}</b><br>{f_['SEARCH01_EN']}"
            ).add_to(m)

    # Legend
    legend = """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;
                background:white;padding:14px;border-radius:8px;
                box-shadow:0 2px 6px rgba(0,0,0,.3);font-size:12px;line-height:1.8">
    <b>Textile Recycling Access</b><br>
    <span style="color:#4CAF50">●</span> Estate &lt;300m<br>
    <span style="color:#FDD835">●</span> Estate 300–500m<br>
    <span style="color:#FF6F00">●</span> Estate 500m–1km<br>
    <span style="color:#C62828">●</span> Estate &gt;1km<br>
    <span style="color:#9C27B0">●</span> Existing public textile pt<br>
    <span style="color:blue">★</span> Proposed hub (800m ring)<br>
    <span style="color:green">♻</span> GREEN@ station<br>
    <span style="color:#795548">●</span> Waste mgmt facility
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))

    m.save(VIZ / "05_interactive_map.html")
    print(f"  → {VIZ / '05_interactive_map.html'}")


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════
def main():
    cp, est, pb_lat, pb_lon, rs_lat, rs_lon, rs_names, wm = load_data()

    # Phase 1 — Analyze
    baseline = phase1_analyze(cp, est, pb_lat, pb_lon)

    # Phase 2 — Optimize
    df_hubs = phase2_optimize(est)

    # Phase 3 — Impact
    impact, cost = phase3_impact(est, df_hubs, baseline, wm)

    # Visualizations
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    viz_01_landfill(cp)
    viz_02_inequality(cp, est, pb_lat, pb_lon)
    viz_03_textiles(est)
    viz_04_impact(est, df_hubs, impact)
    viz_05_map(cp, est, df_hubs, rs_lat, rs_lon, rs_names, wm)

    # Final summary
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    t_saved = impact["textiles"]["pop_saved"]
    t_delta = impact["textiles"]["delta"]
    print(f"""
  THESIS: Hong Kong's recycling infrastructure creates a double trap
          for low-value waste.

  KEY NUMBERS:
    • 8,858 collection points — but 70-78% of glass/textile/hazardous
      infrastructure is locked behind private estates
    • Glass: 76% locked, 5% recovered, 211 tpd to landfill
    • Textiles: 78% locked, 11% recovered, 388 tpd to landfill
    • Public housing residents walk 2.5-3.1× farther than private
    • 106/241 estates >500m from public textile recycling

  SOLUTION: 10 Multi-Stream Micro-Hubs (HK$20-50M total)
    • Greedy max-coverage placement across 10 districts
    • 800m walkable catchment per hub
    • Textiles: {t_delta} fewer estates >500m, {t_saved:,} residents saved
    • 13,300-26,700 tonnes/year diverted from landfill
    • Payback: {cost['payback_years']} years

  FILES:
    data/processed/baseline_metrics.json
    data/processed/optimized_hubs.csv
    data/processed/estates_full_analysis.csv
    data/processed/impact_report.json
    visualizations/01_landfill_composition.png
    visualizations/02_stream_inequality.png
    visualizations/03_textiles_deep_dive.png
    visualizations/04_hub_impact.png
    visualizations/05_interactive_map.html
""")


if __name__ == "__main__":
    main()

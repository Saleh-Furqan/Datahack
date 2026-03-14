#!/usr/bin/env python3
"""
Precompute scenario outputs for the Green Loop Control Tower.

This script intentionally separates:
- Measured outputs (from run_analysis.py artifacts)
- Modeled scenario estimates (explicitly assumption-driven)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd


ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "processed"
CONTROL_TOWER = ROOT / "control_tower"
CONTROL_TOWER_DATA = CONTROL_TOWER / "data"
CONFIG_PATH = CONTROL_TOWER_DATA / "scenarios.json"
OUTPUT_PATH = CONTROL_TOWER_DATA / "scenario_outputs.json"

CONTROL_TOWER_DATA.mkdir(exist_ok=True)


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def _compute_gini(values: np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0
    if np.min(arr) < 0:
        arr = arr - np.min(arr)
    total = np.sum(arr)
    if np.isclose(total, 0):
        return 0.0
    arr = np.sort(arr)
    n = arr.size
    idx = np.arange(1, n + 1)
    gini = (2.0 * np.sum(idx * arr)) / (n * total) - (n + 1) / n
    return float(gini)


def _district_median_gini(estates: pd.DataFrame, distances: np.ndarray) -> float:
    tmp = estates[["district"]].copy()
    tmp["dist"] = distances
    med = tmp.groupby("district", as_index=False).agg(median_dist=("dist", "median"))
    return _compute_gini(med["median_dist"].to_numpy(dtype=float))


def _summarize_access(
    distances: np.ndarray,
    populations: np.ndarray,
    threshold_m: int,
    total_population: int,
) -> Dict[str, Any]:
    over = distances > threshold_m
    estates_over = int(np.sum(over))
    pop_over = int(np.sum(populations[over]))
    burden_pct = (pop_over / max(total_population, 1)) * 100.0
    return {
        "estates_over_500m": estates_over,
        "population_over_500m": pop_over,
        "textile_burden_pct": round(float(burden_pct), 2),
        "median_distance_m": round(float(np.median(distances)), 1),
    }


def _top_beneficiaries(
    estates: pd.DataFrame,
    baseline_dist: np.ndarray,
    scenario_dist: np.ndarray,
    n: int = 12,
) -> list[Dict[str, Any]]:
    tmp = estates[["estate", "district", "population"]].copy()
    tmp["before_m"] = baseline_dist
    tmp["after_m"] = scenario_dist
    tmp["reduction_m"] = np.maximum(tmp["before_m"] - tmp["after_m"], 0.0)
    tmp["newly_served"] = (tmp["before_m"] > 500) & (tmp["after_m"] <= 500)
    top = tmp.sort_values("reduction_m", ascending=False).head(n)
    records = []
    for _, row in top.iterrows():
        records.append(
            {
                "estate": str(row["estate"]),
                "district": str(row["district"]),
                "population": int(row["population"]),
                "before_m": round(float(row["before_m"]), 1),
                "after_m": round(float(row["after_m"]), 1),
                "reduction_m": round(float(row["reduction_m"]), 1),
                "newly_served": bool(row["newly_served"]),
            }
        )
    return records


def _normalize(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=float)
    if arr.size == 0:
        return arr
    vmin = np.min(arr)
    vmax = np.max(arr)
    if np.isclose(vmin, vmax):
        return np.zeros_like(arr)
    return (arr - vmin) / (vmax - vmin)


def _modeled_distances(
    estates: pd.DataFrame,
    baseline_dist: np.ndarray,
    static_dist: np.ndarray,
    model_cfg: Dict[str, Any],
) -> np.ndarray:
    static_gain = np.maximum(baseline_dist - static_dist, 0.0)
    vulnerability = estates.get("district_vulnerability", pd.Series(np.zeros(len(estates)))).to_numpy(dtype=float)
    population = estates["population"].to_numpy(dtype=float)

    vuln_norm = _normalize(vulnerability)
    pop_norm = _normalize(population)

    gain_factor = float(model_cfg.get("distance_gain_factor", 0.4))
    vulnerability_weight = float(model_cfg.get("vulnerability_weight", 0.25))
    focus_population_weight = float(model_cfg.get("focus_population_weight", 0.35))
    targeted_estates = int(model_cfg.get("targeted_estates", 30))
    targeted_boost_m = float(model_cfg.get("targeted_boost_m", 50))

    gain = static_gain * gain_factor * (0.95 + vulnerability_weight * vuln_norm)

    underserved_idx = np.where(baseline_dist > 500)[0]
    if targeted_estates > 0 and underserved_idx.size > 0:
        focus = focus_population_weight * pop_norm + (1.0 - focus_population_weight) * vuln_norm
        ranked = underserved_idx[np.argsort(focus[underserved_idx])[::-1]]
        chosen = ranked[: min(targeted_estates, ranked.size)]
        gain[chosen] += targeted_boost_m

    modeled = np.maximum(baseline_dist - gain, 0.0)
    return modeled


def _costs_and_payback(
    capex_hkd: float,
    annual_opex_hkd: float,
    annual_diversion_low: int,
    annual_diversion_high: int,
    gate_fee_hkd_per_tonne: float,
) -> Tuple[float, Tuple[float, float], Tuple[int, int]]:
    total_cost = float(capex_hkd + annual_opex_hkd * 5.0)
    savings_low = float(annual_diversion_low * gate_fee_hkd_per_tonne)
    savings_high = float(annual_diversion_high * gate_fee_hkd_per_tonne)

    if savings_low <= 0 or savings_high <= 0:
        return total_cost, (0.0, 0.0), (0, 0)

    payback_best = capex_hkd / savings_high
    payback_worst = total_cost / savings_low
    return total_cost, (round(payback_best, 2), round(payback_worst, 2)), (int(savings_low), int(savings_high))


def main() -> None:
    print("=" * 72)
    print("GREEN LOOP CONTROL TOWER - Scenario Precomputation")
    print("=" * 72)

    baseline = _read_json(DATA / "baseline_metrics.json")
    report = _read_json(DATA / "impact_report.json")
    config = _read_json(CONFIG_PATH)
    estates = pd.read_csv(DATA / "estates_full_analysis.csv")
    hubs = pd.read_csv(DATA / "optimized_hubs.csv")

    textiles_baseline = baseline["streams"]["textiles"]
    textiles_impact = report["impact"]["textiles"]
    threshold = int(report["metadata"]["underserved_threshold_m"])
    gate_fee = float(report["diversion_model"]["assumptions"]["landfill_gate_fee_hkd_per_tonne"])
    total_population = int(baseline["fairness_metric"]["denominator_population"])

    baseline_dist = estates["dist_textiles"].to_numpy(dtype=float)
    static_dist = estates["dist_textiles_after"].to_numpy(dtype=float)
    populations = estates["population"].to_numpy(dtype=float)

    baseline_gini = _district_median_gini(estates, baseline_dist)
    static_gini = _district_median_gini(estates, static_dist)

    static_low, static_high = report["cost_summary"]["additional_diversion_annual_tonnes_range"]

    scenarios_out: Dict[str, Dict[str, Any]] = {}

    for key, cfg in config["scenarios"].items():
        costs = cfg.get("costs", {})
        interventions = cfg.get("interventions", {})
        capex = float(costs.get("capex_hkd", 0))
        annual_opex = float(costs.get("annual_opex_hkd", 0))
        model_cfg = cfg.get("modeling", {})

        if key == "baseline":
            access = _summarize_access(baseline_dist, populations, threshold, total_population)
            annual_low = 0
            annual_high = 0
            annual_mid = 0
            gini = baseline_gini
            distances = baseline_dist
            top_bens = []
        elif key == "static_hubs":
            # Measured from main optimization run.
            access = {
                "estates_over_500m": int(textiles_impact["after_estates_over_500m"]),
                "population_over_500m": int(textiles_impact["after_population_over_500m"]),
                "textile_burden_pct": round(float(textiles_impact["after_population_over_500m"] / total_population * 100), 2),
                "median_distance_m": round(float(textiles_impact["median_distance_after_m"]), 1),
            }
            annual_low = int(static_low)
            annual_high = int(static_high)
            annual_mid = int(round((annual_low + annual_high) / 2))
            gini = static_gini
            distances = static_dist
            top_bens = _top_beneficiaries(estates, baseline_dist, static_dist)
        else:
            # Explicitly modeled scenario.
            distances = _modeled_distances(estates, baseline_dist, static_dist, model_cfg)
            access = _summarize_access(distances, populations, threshold, total_population)

            rel_low = float(model_cfg.get("diversion_relative_low", 0.7))
            rel_high = float(model_cfg.get("diversion_relative_high", 0.95))
            annual_low = int(round(static_low * rel_low))
            annual_high = int(round(static_high * rel_high))
            if annual_high < annual_low:
                annual_low, annual_high = annual_high, annual_low
            annual_mid = int(round((annual_low + annual_high) / 2))

            gini = _district_median_gini(estates, distances)
            top_bens = _top_beneficiaries(estates, baseline_dist, distances)

        total_cost, payback_range, savings_range = _costs_and_payback(
            capex_hkd=capex,
            annual_opex_hkd=annual_opex,
            annual_diversion_low=annual_low,
            annual_diversion_high=annual_high,
            gate_fee_hkd_per_tonne=gate_fee,
        )

        newly_served_mask = (baseline_dist > threshold) & (distances <= threshold)
        worst_quartile_threshold = estates.get("district_vulnerability", pd.Series(np.zeros(len(estates)))).quantile(0.75)
        worst_quartile_mask = estates.get("district_vulnerability", pd.Series(np.zeros(len(estates)))) >= worst_quartile_threshold

        scenario_record = {
            "name": cfg.get("name", key),
            "description": cfg.get("description", ""),
            "interventions": interventions,
            "notes": cfg.get("assumptions", {}).get("note", ""),
            "estates_over_500m": access["estates_over_500m"],
            "population_over_500m": access["population_over_500m"],
            "textile_burden_pct": access["textile_burden_pct"],
            "median_distance_m": access["median_distance_m"],
            "district_gini": round(float(gini), 3),
            "beneficiary_estates": int(np.sum(newly_served_mask)),
            "worst_quartile_improvement": int(np.sum(newly_served_mask & worst_quartile_mask.to_numpy())),
            "annual_diversion_tonnes": annual_mid,
            "annual_diversion_tonnes_range": [annual_low, annual_high],
            "landfill_savings_hkd_per_year_range": [savings_range[0], savings_range[1]],
            "capex_hkd": int(capex),
            "annual_opex_hkd": int(annual_opex),
            "total_cost_hkd": int(total_cost),
            "payback_years": round(float(np.mean(payback_range)), 2) if annual_mid > 0 else None,
            "payback_years_range": [payback_range[0], payback_range[1]] if annual_mid > 0 else [None, None],
            "estate_distances_m": [round(float(x), 2) for x in distances.tolist()],
            "top_beneficiaries": top_bens,
        }
        scenarios_out[key] = scenario_record

    # Keep top hubs for map overlays.
    map_hubs = []
    for _, row in hubs.iterrows():
        map_hubs.append(
            {
                "hub_rank": int(row["hub_rank"]),
                "estate": str(row["estate"]),
                "district": str(row["district"]),
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "new_population_covered": int(row["new_population_covered"]),
            }
        )

    output = {
        "metadata": {
            "generated_on": pd.Timestamp.utcnow().isoformat(),
            "source_files": [
                "data/processed/baseline_metrics.json",
                "data/processed/impact_report.json",
                "data/processed/optimized_hubs.csv",
                "data/processed/estates_full_analysis.csv",
                "control_tower/data/scenarios.json",
            ],
            "primary_metric": "Textile Population Burden (>500m)",
            "secondary_metric": "District median distance inequality (Gini)",
            "units": {
                "annual_diversion": "tonnes/year",
                "diversion_range": "tonnes/year",
                "distance": "meters",
                "cost": "HKD",
                "payback": "years",
            },
            "assumptions": "Baseline/static are measured from pipeline; other scenarios are modeled estimates.",
            "uncertainty": "±40% modeled range; validate through pilot.",
        },
        "scenarios": scenarios_out,
        "hubs": map_hubs,
    }

    with OUTPUT_PATH.open("w") as f:
        json.dump(output, f, indent=2)

    print("\n✓ Saved scenario outputs to:", OUTPUT_PATH)
    print("\n" + "=" * 72)
    print("SCENARIO SUMMARY")
    print("=" * 72)
    for key, s in scenarios_out.items():
        print(f"\n{key.upper()}:")
        print(f"  Estates >500m: {s['estates_over_500m']}")
        print(f"  Textile burden: {s['textile_burden_pct']:.1f}%")
        print(
            f"  Diversion: {s['annual_diversion_tonnes_range'][0]:,} - "
            f"{s['annual_diversion_tonnes_range'][1]:,} tonnes/year"
        )
        print(f"  Cost (5y): HK${s['total_cost_hkd'] / 1e6:.1f}M")
        if s["payback_years"] is not None:
            print(
                f"  Payback: {s['payback_years_range'][0]} - "
                f"{s['payback_years_range'][1]} years"
            )
        print(f"  District inequality (Gini): {s['district_gini']:.3f}")

    print("\n✓ Precomputation complete.")


if __name__ == "__main__":
    main()

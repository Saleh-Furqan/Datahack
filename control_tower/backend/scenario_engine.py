"""Scenario engine utilities used by the Streamlit frontend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CONTROL_TOWER = ROOT / "control_tower"
OUTPUT_PATH = CONTROL_TOWER / "data" / "scenario_outputs.json"


def load_outputs(path: Path | None = None) -> Dict[str, Any]:
    """Load precomputed scenario outputs."""
    target = path or OUTPUT_PATH
    with target.open() as f:
        return json.load(f)


def _minmax_norm(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return arr
    vmin = np.nanmin(arr)
    vmax = np.nanmax(arr)
    if not np.isfinite(vmin) or not np.isfinite(vmax) or np.isclose(vmin, vmax):
        return np.zeros_like(arr)
    return (arr - vmin) / (vmax - vmin)


def recommend_scenario(outputs: Dict[str, Any], budget_millions: int, equity_weight: int) -> str:
    """
    Recommend a scenario from precomputed options based on budget + policy preference.

    The scoring blends impact and equity:
    - Impact: burden reduction + diversion
    - Equity: district inequality reduction + burden reduction
    """
    scenarios = outputs["scenarios"]
    baseline = scenarios["baseline"]

    eligible_keys = [
        k for k, v in scenarios.items() if int(round(v["capex_hkd"] / 1_000_000)) <= budget_millions
    ]
    if not eligible_keys:
        return "baseline"
    if len(eligible_keys) == 1:
        return eligible_keys[0]

    rows: List[Dict[str, Any]] = []
    for k in eligible_keys:
        s = scenarios[k]
        rows.append(
            {
                "key": k,
                "estate_reduction": baseline["estates_over_500m"] - s["estates_over_500m"],
                "burden_reduction": baseline["textile_burden_pct"] - s["textile_burden_pct"],
                "diversion": s["annual_diversion_tonnes"],
                "gini_reduction": baseline["district_gini"] - s["district_gini"],
                "cost_m": s["total_cost_hkd"] / 1_000_000,
            }
        )

    df = pd.DataFrame(rows)
    df["impact_norm"] = (
        0.45 * _minmax_norm(df["burden_reduction"].to_numpy())
        + 0.35 * _minmax_norm(df["diversion"].to_numpy())
        + 0.20 * _minmax_norm(df["estate_reduction"].to_numpy())
    )
    df["equity_norm"] = (
        0.7 * _minmax_norm(df["gini_reduction"].to_numpy())
        + 0.3 * _minmax_norm(df["burden_reduction"].to_numpy())
    )

    ew = float(equity_weight) / 100.0
    # Penalize cost more when user is in impact-first mode.
    cost_penalty_weight = 0.18 - (0.12 * ew)
    df["cost_penalty"] = _minmax_norm(df["cost_m"].to_numpy()) * cost_penalty_weight
    df["score"] = (1.0 - ew) * df["impact_norm"] + ew * df["equity_norm"] - df["cost_penalty"]

    # Explicit preference modes for clearer behavior in demo.
    if equity_weight <= 30:
        df["score"] = df["impact_norm"] - (_minmax_norm(df["cost_m"].to_numpy()) * 0.22)
    elif equity_weight >= 70:
        df["score"] = 0.75 * df["equity_norm"] + 0.25 * df["impact_norm"] - (_minmax_norm(df["cost_m"].to_numpy()) * 0.06)

    best_row = df.sort_values("score", ascending=False).iloc[0]
    return str(best_row["key"])


def scenario_comparison_table(outputs: Dict[str, Any]) -> pd.DataFrame:
    """Build tidy comparison table for charts."""
    rows: List[Dict[str, Any]] = []
    for key, s in outputs["scenarios"].items():
        rows.append(
            {
                "key": key,
                "scenario": s["name"],
                "estates_over_500m": s["estates_over_500m"],
                "textile_burden_pct": s["textile_burden_pct"],
                "annual_diversion_tonnes": s["annual_diversion_tonnes"],
                "total_cost_hkd_m": s["total_cost_hkd"] / 1_000_000,
                "district_gini": s["district_gini"],
            }
        )
    return pd.DataFrame(rows)


def build_estate_view(estates: pd.DataFrame, scenario: Dict[str, Any]) -> pd.DataFrame:
    """Build scenario-specific estate dataframe for map and beneficiary views."""
    out = estates[["estate", "district", "lat", "lon", "population", "dist_textiles"]].copy()
    modeled = scenario.get("estate_distances_m")
    if modeled is None:
        out["distance_m"] = out["dist_textiles"]
    else:
        out["distance_m"] = np.asarray(modeled, dtype=float)
    out["distance_reduction_m"] = np.maximum(out["dist_textiles"] - out["distance_m"], 0.0)
    out["still_underserved"] = out["distance_m"] > 500
    out["newly_served"] = (out["dist_textiles"] > 500) & (out["distance_m"] <= 500)

    def severity_label(d: float) -> str:
        if d > 800:
            return "Critical (>800m)"
        if d > 500:
            return "Underserved (500-800m)"
        if d > 300:
            return "Moderate (300-500m)"
        return "Well-served (<300m)"

    out["severity"] = out["distance_m"].apply(severity_label)
    return out


def top_beneficiary_estates(estates_view: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return estates with largest modeled improvement."""
    cols = ["estate", "district", "population", "dist_textiles", "distance_m", "distance_reduction_m", "newly_served"]
    top = estates_view.sort_values("distance_reduction_m", ascending=False).head(n)[cols].copy()
    top.rename(
        columns={
            "dist_textiles": "before_m",
            "distance_m": "after_m",
            "distance_reduction_m": "reduction_m",
        },
        inplace=True,
    )
    return top

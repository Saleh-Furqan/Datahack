#!/usr/bin/env python3
"""Green Loop Control Tower - polished interactive policy demo."""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure imports work both from repo root and from control_tower/ cwd.
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from control_tower.backend import (  # noqa: E402
    build_estate_view,
    load_outputs,
    recommend_scenario,
    scenario_comparison_table,
    top_beneficiary_estates,
)


DATA = ROOT / "data" / "processed"
ASSETS = ROOT / "control_tower" / "assets"
HK_DISTRICTS_GEOJSON = ASSETS / "hk_districts.geojson"

SCENARIO_ORDER = ["baseline", "mobile_first", "hybrid_equity", "static_hubs"]
SCENARIO_LABELS = {
    "baseline": "Baseline",
    "mobile_first": "Mobile-First",
    "hybrid_equity": "Hybrid Equity",
    "static_hubs": "Static Hubs",
}
SEVERITY_COLORS = {
    "Well-served (<300m)": "#2E7D32",
    "Moderate (300-500m)": "#F59E0B",
    "Underserved (500-800m)": "#EF4444",
    "Critical (>800m)": "#991B1B",
}


def _inject_css() -> None:
    st.markdown(
        """
        <style>
          .block-container {padding-top: 1.2rem; padding-bottom: 1.2rem; max-width: 1280px;}
          .app-title {font-size: 2.1rem; font-weight: 800; color: #0F172A; margin-bottom: 0.15rem;}
          .app-subtitle {font-size: 1.0rem; color: #475569; margin-bottom: 1rem;}
          .panel {background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 0.9rem 1rem;}
          .small-muted {font-size: 0.86rem; color: #64748B;}
          .badge {display: inline-block; padding: 0.2rem 0.5rem; border-radius: 999px; background: #E2E8F0; color: #0F172A; font-size: 0.78rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _load_outputs() -> Dict:
    return load_outputs()


@st.cache_data(show_spinner=False)
def _load_estates() -> pd.DataFrame:
    df = pd.read_csv(DATA / "estates_full_analysis.csv")
    expected = {"estate", "district", "lat", "lon", "population", "dist_textiles"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns in estates_full_analysis.csv: {sorted(missing)}")
    return df


@st.cache_data(show_spinner=False)
def _load_optional_district_geojson() -> bool:
    return HK_DISTRICTS_GEOJSON.exists()


@st.cache_data(show_spinner=False)
def _read_district_geojson() -> tuple[dict | None, str | None]:
    if not HK_DISTRICTS_GEOJSON.exists():
        return None, None
    try:
        data = json.loads(HK_DISTRICTS_GEOJSON.read_text())
    except Exception:
        return None, None

    features = data.get("features", [])
    if not features:
        return None, None
    props = features[0].get("properties", {})
    if not props:
        return None, None

    candidates = ["district", "DISTRICT", "District", "name", "NAME_ENG", "ENAME"]
    for c in candidates:
        if c in props:
            return data, c
    # fallback: first property key
    first = next(iter(props.keys()), None)
    return data, first


def _scenario_selector(outputs: Dict) -> str:
    st.sidebar.markdown("## Policy Controls")

    budget_m = st.sidebar.slider("Budget (HK$M)", 0, 80, 55, 5)
    equity = st.sidebar.slider("Equity Priority (%)", 0, 100, 50, 5)
    mode = st.sidebar.radio("Selection Mode", ["Auto", "Manual"], horizontal=True)

    recommended = recommend_scenario(outputs, budget_millions=budget_m, equity_weight=equity)
    if mode == "Auto":
        selected = recommended
    else:
        selected = st.sidebar.selectbox(
            "Scenario",
            options=SCENARIO_ORDER,
            format_func=lambda k: outputs["scenarios"][k]["name"],
            index=SCENARIO_ORDER.index(recommended),
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Recommended by controls:** `{outputs['scenarios'][recommended]['name']}`")
    st.sidebar.markdown(
        '<div class="small-muted">Controls drive scenario recommendation through an impact/equity scoring rule under budget constraints.</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Data")
    st.sidebar.markdown("- Measured baseline + measured static-hub impacts")
    st.sidebar.markdown("- Modeled scenario estimates (explicitly labeled)")

    return selected


def _summary_metrics(current: Dict, baseline: Dict) -> None:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Estates >500m",
            int(current["estates_over_500m"]),
            delta=int(current["estates_over_500m"] - baseline["estates_over_500m"]),
            delta_color="inverse",
        )
    with c2:
        st.metric(
            "Textile Burden",
            f"{current['textile_burden_pct']:.1f}%",
            delta=f"{current['textile_burden_pct'] - baseline['textile_burden_pct']:.1f}%",
            delta_color="inverse",
        )
    with c3:
        low, high = current["annual_diversion_tonnes_range"]
        st.metric(
            "Diversion (annual)",
            f"{int(current['annual_diversion_tonnes']):,} t/y",
            delta=f"{low:,} - {high:,} t/y",
        )
    with c4:
        st.metric(
            "District Inequality (Gini)",
            f"{current['district_gini']:.3f}",
            delta=f"{current['district_gini'] - baseline['district_gini']:.3f}",
            delta_color="inverse",
        )


def _overview_tab(outputs: Dict, selected_key: str) -> None:
    st.subheader("Strategy Tradeoff Overview")
    table = scenario_comparison_table(outputs)
    baseline = outputs["scenarios"]["baseline"]

    # Tradeoff frontier
    fig = px.scatter(
        table,
        x="textile_burden_pct",
        y="annual_diversion_tonnes",
        size="total_cost_hkd_m",
        color="district_gini",
        text="scenario",
        color_continuous_scale="RdYlGn_r",
        labels={
            "textile_burden_pct": "Textile burden >500m (%)",
            "annual_diversion_tonnes": "Diversion (tonnes/year)",
            "district_gini": "District inequality (Gini)",
            "total_cost_hkd_m": "5-year cost (HK$M)",
        },
        title="Policy Frontier: Impact vs Equity vs Cost",
        height=420,
    )
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="white")))
    for _, row in table.iterrows():
        if row["key"] == selected_key:
            fig.add_annotation(
                x=row["textile_burden_pct"],
                y=row["annual_diversion_tonnes"],
                text="Selected",
                showarrow=True,
                arrowhead=2,
                ay=-34,
                bgcolor="#111827",
                font=dict(color="white", size=11),
            )
    st.plotly_chart(fig, width="stretch")

    left, right = st.columns([1.5, 1.0])
    current = outputs["scenarios"][selected_key]
    with left:
        comp = table[["scenario", "estates_over_500m", "textile_burden_pct", "annual_diversion_tonnes", "total_cost_hkd_m", "district_gini"]].copy()
        comp.rename(
            columns={
                "scenario": "Scenario",
                "estates_over_500m": "Estates >500m",
                "textile_burden_pct": "Burden %",
                "annual_diversion_tonnes": "Diversion (t/y)",
                "total_cost_hkd_m": "Cost 5y (HK$M)",
                "district_gini": "Gini",
            },
            inplace=True,
        )
        st.dataframe(comp.round(2), width="stretch", hide_index=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(f"### {current['name']}")
        st.markdown(current["description"])
        st.markdown("**Interventions**")
        interventions = current.get("interventions", {})
        for k, v in interventions.items():
            label = k.replace("_", " ").title()
            st.markdown(f"- {label}: {v}")
        st.markdown("**Economics**")
        low_pay, high_pay = current["payback_years_range"]
        if low_pay is not None:
            st.markdown(f"- Payback: {low_pay} - {high_pay} years")
        st.markdown(f"- Capex: HK${current['capex_hkd']/1e6:.1f}M")
        st.markdown(f"- 5-year total: HK${current['total_cost_hkd']/1e6:.1f}M")
        st.markdown(
            f'<div class="small-muted">Delta vs baseline burden: {baseline["textile_burden_pct"] - current["textile_burden_pct"]:.1f}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def _map_tab(outputs: Dict, estates: pd.DataFrame, selected_key: str) -> None:
    st.subheader("Hong Kong Estate-Level Map")
    current = outputs["scenarios"][selected_key]
    est_view = build_estate_view(estates, current)

    estate_options = ["(none)"] + sorted(est_view["estate"].tolist())
    spotlight = st.selectbox("Estate Spotlight", options=estate_options, index=0)

    fig = go.Figure()

    geojson_data, feature_key = _read_district_geojson()
    if geojson_data is not None and feature_key is not None:
        district = (
            est_view.groupby("district", as_index=False)
            .agg(
                district_pop=("population", "sum"),
                pop_over_500=("population", lambda s: int(s[est_view.loc[s.index, "distance_m"] > 500].sum())),
            )
            .copy()
        )
        district["burden_pct"] = (
            district["pop_over_500"] / district["district_pop"].replace(0, np.nan) * 100
        ).fillna(0.0)
        fig.add_trace(
            go.Choroplethmap(
                geojson=geojson_data,
                featureidkey=f"properties.{feature_key}",
                locations=district["district"],
                z=district["burden_pct"],
                colorscale="OrRd",
                zmin=0,
                zmax=max(40, float(district["burden_pct"].max())),
                marker_opacity=0.23,
                marker_line_width=0.4,
                marker_line_color="#94A3B8",
                colorbar_title="District burden %",
                name="District burden",
                hovertemplate="<b>%{location}</b><br>Burden: %{z:.1f}%<extra></extra>",
            )
        )
    for severity, color in SEVERITY_COLORS.items():
        sub = est_view[est_view["severity"] == severity]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scattermap(
                lat=sub["lat"],
                lon=sub["lon"],
                mode="markers",
                name=severity,
                marker=dict(
                    size=np.clip(np.sqrt(sub["population"]) / 6.2, 7, 18),
                    color=color,
                    opacity=0.78,
                ),
                text=sub.apply(
                    lambda r: (
                        f"{r['estate']} ({r['district']})<br>"
                        f"Population: {int(r['population']):,}<br>"
                        f"Distance: {r['distance_m']:.0f}m<br>"
                        f"Reduction: {r['distance_reduction_m']:.0f}m"
                    ),
                    axis=1,
                ),
                hoverinfo="text",
            )
        )

    hubs = pd.DataFrame(outputs.get("hubs", []))
    hub_count = int(current.get("interventions", {}).get("new_hubs", 0))
    if hub_count > 0 and not hubs.empty:
        hubs_to_show = hubs.head(hub_count)
        fig.add_trace(
            go.Scattermap(
                lat=hubs_to_show["lat"],
                lon=hubs_to_show["lon"],
                mode="markers+text",
                text=[f"H{int(x)}" for x in hubs_to_show["hub_rank"]],
                textposition="top center",
                name="Proposed Hubs",
                marker=dict(size=14, color="#1D4ED8", symbol="star"),
                hovertext=hubs_to_show.apply(
                    lambda r: (
                        f"Hub {int(r['hub_rank'])}: {r['estate']}<br>"
                        f"District: {r['district']}<br>"
                        f"New coverage: {int(r['new_population_covered']):,}"
                    ),
                    axis=1,
                ),
                hoverinfo="text",
            )
        )

    if spotlight != "(none)":
        row = est_view[est_view["estate"] == spotlight].iloc[0]
        fig.add_trace(
            go.Scattermap(
                lat=[row["lat"]],
                lon=[row["lon"]],
                mode="markers",
                name="Spotlight",
                marker=dict(size=22, color="#111827", symbol="circle"),
                hovertext=f"{row['estate']}<br>After: {row['distance_m']:.0f}m",
                hoverinfo="text",
            )
        )

    fig.update_layout(
        map=dict(
            style="carto-positron",
            center={"lat": 22.35, "lon": 114.16},
            zoom=10.2,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=640,
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01),
    )
    st.plotly_chart(fig, width="stretch")

    if not _load_optional_district_geojson():
        st.caption("Optional upgrade: add `control_tower/assets/hk_districts.geojson` for district boundary overlay.")
    elif geojson_data is None or feature_key is None:
        st.caption(
            "District overlay file detected but property matching failed. "
            "Expected a district-name property like `district` or `DISTRICT`."
        )
    else:
        st.caption(f"District overlay active (feature key: `{feature_key}`).")

    st.markdown("### Top Beneficiary Estates")
    top = top_beneficiary_estates(est_view, n=12)
    st.dataframe(top, width="stretch", hide_index=True)


def _equity_tab(outputs: Dict, estates: pd.DataFrame, selected_key: str) -> None:
    st.subheader("Equity Dashboard")
    current = outputs["scenarios"][selected_key]
    baseline = outputs["scenarios"]["baseline"]
    est_view = build_estate_view(estates, current)

    c1, c2 = st.columns(2)
    with c1:
        target = 30.0
        current_b = current["textile_burden_pct"]
        baseline_b = baseline["textile_burden_pct"]
        denom = max(baseline_b - target, 1e-9)
        progress = max(0.0, min(1.0, (baseline_b - current_b) / denom))
        st.markdown("**Primary fairness metric: Textile burden >500m**")
        st.progress(progress)
        st.markdown(f"- Baseline: **{baseline_b:.1f}%**")
        st.markdown(f"- Current: **{current_b:.1f}%**")
        st.markdown(f"- Target: **{target:.1f}%**")
    with c2:
        st.markdown("**Secondary fairness metric: District inequality (Gini)**")
        st.markdown(f"- Baseline: **{baseline['district_gini']:.3f}**")
        st.markdown(f"- Current: **{current['district_gini']:.3f}**")
        st.markdown(f"- Improvement: **{baseline['district_gini'] - current['district_gini']:.3f}**")

    st.markdown("### Tradeoff Space (Burden vs Inequality)")
    table = scenario_comparison_table(outputs)
    fig = px.scatter(
        table,
        x="district_gini",
        y="textile_burden_pct",
        size="total_cost_hkd_m",
        color="annual_diversion_tonnes",
        text="scenario",
        color_continuous_scale="Viridis",
        labels={"district_gini": "Gini (lower better)", "textile_burden_pct": "Burden % (lower better)"},
        height=390,
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, width="stretch")

    newly_served = int(est_view["newly_served"].sum())
    still_underserved = int(est_view["still_underserved"].sum())
    pop_saved = int(baseline["population_over_500m"] - current["population_over_500m"])
    m1, m2, m3 = st.columns(3)
    m1.metric("Newly Served Estates", newly_served)
    m2.metric("Still Underserved Estates", still_underserved)
    m3.metric("Residents Moved Out of >500m", f"{pop_saved:,}")


def _assumptions_tab(outputs: Dict, selected_key: str) -> None:
    st.subheader("Assumptions, Sensitivity, and Validation")
    current = outputs["scenarios"][selected_key]
    st.warning(
        "Measured baseline/static outputs are data-driven. Mobile-first and hybrid are modeled estimates requiring pilot validation."
    )

    assumptions_rows = [
        ["Underserved threshold", "500m", "From baseline analysis design"],
        ["Service radius (fixed hubs)", "800m", "From optimization setup"],
        ["Population proxy", "rental_flats x 2.7", "Housing-estate proxy used in pipeline"],
        ["Diversion metric", "tonnes/year", "Annualized from tpd assumptions"],
        ["Gate fee", "HK$365/tonne", "Impact report assumption"],
        ["Modeled uncertainty", "+/-40%", "Displayed as low/high ranges"],
    ]
    st.table(pd.DataFrame(assumptions_rows, columns=["Parameter", "Value", "Reference"]))

    st.markdown("### Scenario Sensitivity Snapshot")
    rows: List[Dict[str, float | str]] = []
    for key in SCENARIO_ORDER:
        sc = outputs["scenarios"][key]
        low_div, high_div = sc["annual_diversion_tonnes_range"]
        low_pay, high_pay = sc["payback_years_range"]
        rows.append(
            {
                "Scenario": sc["name"],
                "Diversion Low": low_div,
                "Diversion High": high_div,
                "Payback Best": low_pay if low_pay is not None else np.nan,
                "Payback Worst": high_pay if high_pay is not None else np.nan,
            }
        )
    sens = pd.DataFrame(rows)
    st.dataframe(sens, width="stretch", hide_index=True)

    st.markdown("### 90-Day Pilot Validation Plan")
    st.markdown(
        """
        1. Weeks 1-2: Baseline measurement at 5 high-burden estates.
        2. Weeks 3-8: Deploy selected intervention package and log weekly tonnage.
        3. Weeks 9-10: Compare observed uplift vs modeled ranges.
        4. Weeks 11-12: Scale, retune, or pivot based on evidence.
        """
    )


def main() -> None:
    st.set_page_config(page_title="Green Loop Control Tower", page_icon="recycle", layout="wide")
    _inject_css()

    outputs = _load_outputs()
    estates = _load_estates()

    selected_key = _scenario_selector(outputs)
    current = outputs["scenarios"][selected_key]
    baseline = outputs["scenarios"]["baseline"]

    st.markdown('<div class="app-title">Green Loop Control Tower</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Interactive policy simulator for Hong Kong recycling access, equity, and cost tradeoffs.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="badge">Active Scenario: {current["name"]}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    _summary_metrics(current, baseline)
    st.markdown("---")

    tab_overview, tab_map, tab_equity, tab_assumptions = st.tabs(
        ["Overview", "Hong Kong Map", "Equity", "Assumptions & Validation"]
    )
    with tab_overview:
        _overview_tab(outputs, selected_key)
    with tab_map:
        _map_tab(outputs, estates, selected_key)
    with tab_equity:
        _equity_tab(outputs, estates, selected_key)
    with tab_assumptions:
        _assumptions_tab(outputs, selected_key)

    st.markdown("---")
    st.caption(
        "Data sources: data.gov.hk datasets + generated processed outputs in this repo. "
        "All modeled values are explicitly labeled and should be validated with pilot data."
    )


if __name__ == "__main__":
    main()

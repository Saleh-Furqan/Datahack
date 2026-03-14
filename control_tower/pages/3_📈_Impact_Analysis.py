#!/usr/bin/env python3
"""
Impact Analysis - Detailed metrics and beneficiary analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path

try:
    from control_tower.backend.theme import apply_theme
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from backend.theme import apply_theme

# Page config
st.set_page_config(
    page_title="Impact Analysis - Green Loop",
    page_icon="📈",
    layout="wide"
)
apply_theme()

# Paths
ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data" / "processed"
CT_DATA = Path(__file__).parent.parent / "data"

# Load data
@st.cache_data
def load_scenario_data():
    with open(CT_DATA / "scenario_outputs.json") as f:
        return json.load(f)

@st.cache_data
def load_estates():
    return pd.read_csv(DATA_DIR / "estates_full_analysis.csv")

data = load_scenario_data()
scenarios = data["scenarios"]
estates = load_estates()

# Header
st.title("📈 Impact Analysis")
st.markdown("**Detailed metrics and beneficiary analysis**")

# Scenario selector
scenario_options = {
    "static_hubs": "Static Hubs (Optimized)",
    "mobile_first": "Mobile-First Scenario",
    "hybrid_equity": "Hybrid Equity Scenario"
}

selected_scenario = st.selectbox(
    "Select Scenario to Analyze",
    options=list(scenario_options.keys()),
    format_func=lambda x: scenario_options[x]
)

s = scenarios[selected_scenario]
baseline = scenarios["baseline"]

st.markdown("---")

# Key Impact Metrics
st.subheader("📊 Key Impact Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta = s["estates_over_500m"] - baseline["estates_over_500m"]
    st.metric(
        "Estates >500m",
        s["estates_over_500m"],
        delta=f"{delta}",
        delta_color="inverse"
    )

with col2:
    delta = s["textile_burden_pct"] - baseline["textile_burden_pct"]
    st.metric(
        "Burden %",
        f"{s['textile_burden_pct']:.1f}%",
        delta=f"{delta:.1f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "Diversion (t/y)",
        f"{s['annual_diversion_tonnes']:,}",
        delta=f"+{s['annual_diversion_tonnes']:,}"
    )

with col4:
    delta = s["district_gini"] - baseline["district_gini"]
    st.metric(
        "District Gini",
        f"{s['district_gini']:.3f}",
        delta=f"{delta:.3f}",
        delta_color="inverse"
    )

with col5:
    st.metric(
        "Beneficiaries",
        s["beneficiary_estates"],
        delta=f"+{s['beneficiary_estates']}"
    )

st.markdown("---")

# Distribution Analysis
st.subheader("📊 Coverage Distribution Analysis")

col1, col2 = st.columns(2)

with col1:
    # Distance distribution histogram
    st.markdown("### Distance Distribution")

    # Create bins
    bins = [0, 300, 500, 800, 1000, 5000]
    labels = ["<300m", "300-500m", "500-800m", "800-1000m", ">1000m"]

    baseline_distances = estates["dist_textiles"].values
    candidate_distances = s.get("estate_distances_m", [])
    if len(candidate_distances) == len(estates):
        scenario_distances = np.asarray(candidate_distances, dtype=float)
    else:
        scenario_distances = baseline_distances.copy()

    baseline_binned = pd.cut(baseline_distances, bins=bins, labels=labels)
    scenario_binned = pd.cut(scenario_distances, bins=bins, labels=labels)

    baseline_counts = baseline_binned.value_counts().sort_index()
    scenario_counts = scenario_binned.value_counts().sort_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=baseline_counts.values,
        name="Baseline",
        marker_color="#94A3B8"
    ))

    fig.add_trace(go.Bar(
        x=labels,
        y=scenario_counts.values,
        name=scenario_options[selected_scenario],
        marker_color="#0EA5E9"
    ))

    fig.update_layout(
        xaxis_title="Distance Category",
        yaxis_title="Number of Estates",
        barmode="group",
        height=400
    )

    st.plotly_chart(fig, width="stretch")

with col2:
    # Population coverage
    st.markdown("### Population Coverage")

    # Calculate population in each category
    estates_temp = estates.copy()
    estates_temp["baseline_dist"] = baseline_distances
    estates_temp["scenario_dist"] = scenario_distances

    baseline_pop = estates_temp.groupby(
        pd.cut(estates_temp["baseline_dist"], bins=bins, labels=labels),
        observed=False,
    )["population"].sum()
    scenario_pop = estates_temp.groupby(
        pd.cut(estates_temp["scenario_dist"], bins=bins, labels=labels),
        observed=False,
    )["population"].sum()

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=labels,
        y=baseline_pop.values,
        name="Baseline",
        marker_color="#94A3B8"
    ))

    fig2.add_trace(go.Bar(
        x=labels,
        y=scenario_pop.values,
        name=scenario_options[selected_scenario],
        marker_color="#10B981"
    ))

    fig2.update_layout(
        xaxis_title="Distance Category",
        yaxis_title="Population",
        barmode="group",
        height=400
    )

    st.plotly_chart(fig2, width="stretch")

st.markdown("---")

# District-level Analysis
st.subheader("🗺️ District-Level Impact")

# Calculate district-level metrics
estates_temp["improvement"] = estates_temp["baseline_dist"] - estates_temp["scenario_dist"]

district_stats = estates_temp.groupby("district").agg({
    "improvement": "mean",
    "population": "sum",
    "estate": "count",
    "scenario_dist": "median"
}).reset_index()

district_stats.columns = ["District", "Avg Improvement (m)", "Population", "Estates", "Median Distance (m)"]
district_stats = district_stats.sort_values("Avg Improvement (m)", ascending=False)

# District improvement chart
fig3 = px.bar(
    district_stats.head(15),
    x="District",
    y="Avg Improvement (m)",
    color="Avg Improvement (m)",
    color_continuous_scale="RdYlGn",
    title="Top 15 Districts by Average Distance Improvement"
)

fig3.update_layout(height=400)
st.plotly_chart(fig3, width="stretch")

# District table
st.markdown("### District Summary")
st.dataframe(
    district_stats.head(20),
    width="stretch",
    hide_index=True,
    column_config={
        "Avg Improvement (m)": st.column_config.NumberColumn(
            "Avg Improvement (m)",
            format="%.1f"
        ),
        "Median Distance (m)": st.column_config.NumberColumn(
            "Median Distance (m)",
            format="%.1f"
        ),
        "Population": st.column_config.NumberColumn(
            "Population",
            format="%d"
        )
    }
)

st.markdown("---")

# Top Beneficiaries
if s.get("top_beneficiaries"):
    st.subheader("🏆 Top Beneficiary Estates")
    st.markdown(f"**Estates that benefit most from {scenario_options[selected_scenario]}**")

    beneficiaries_df = pd.DataFrame(s["top_beneficiaries"])

    # Display as formatted table
    st.dataframe(
        beneficiaries_df,
        width="stretch",
        hide_index=True,
        column_config={
            "estate": st.column_config.TextColumn("Estate", width="large"),
            "district": st.column_config.TextColumn("District"),
            "population": st.column_config.NumberColumn("Population", format="%d"),
            "before_m": st.column_config.NumberColumn("Before (m)", format="%.1f"),
            "after_m": st.column_config.NumberColumn("After (m)", format="%.1f"),
            "reduction_m": st.column_config.NumberColumn("Reduction (m)", format="%.1f"),
            "newly_served": st.column_config.CheckboxColumn("Newly Served?")
        }
    )

    # Beneficiary breakdown
    col1, col2 = st.columns(2)

    with col1:
        newly_served = sum(1 for b in s["top_beneficiaries"] if b["newly_served"])
        st.info(f"**{newly_served} / {len(s['top_beneficiaries'])}** estates newly brought within 500m threshold")

    with col2:
        total_pop = sum(b["population"] for b in s["top_beneficiaries"])
        st.success(f"**{total_pop:,}** residents in top beneficiary estates")

st.markdown("---")

# Economic Analysis
st.subheader("💰 Economic Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Cost Breakdown")

    cost_data = {
        "Component": ["CAPEX", "5-Year OPEX"],
        "Amount (HK$M)": [
            s["capex_hkd"] / 1e6,
            s["annual_opex_hkd"] * 5 / 1e6
        ]
    }

    cost_df = pd.DataFrame(cost_data)

    fig4 = px.pie(
        cost_df,
        values="Amount (HK$M)",
        names="Component",
        title=f"Total Cost: HK${s['total_cost_hkd'] / 1e6:.1f}M"
    )

    st.plotly_chart(fig4, width="stretch")

with col2:
    st.markdown("### Savings & Payback")

    if s["payback_years"]:
        savings_range = s["landfill_savings_hkd_per_year_range"]

        st.metric(
            "Annual Landfill Savings",
            f"HK${savings_range[0]:,} - ${savings_range[1]:,}",
            help="Avoided landfill gate fees from diverted textiles"
        )

        st.metric(
            "Payback Period",
            f"{s['payback_years']:.1f} years",
            help="Time to recover CAPEX from landfill savings"
        )

        payback_best, payback_worst = s["payback_years_range"]
        st.markdown(f"""
        **Payback Range:** {payback_best:.1f} - {payback_worst:.1f} years

        - Best case: CAPEX / High savings
        - Worst case: Total 5Y cost / Low savings
        """)

    else:
        st.warning("No diversion in baseline scenario")

st.markdown("---")

# Uncertainty & Assumptions
st.subheader("⚠️ Uncertainty & Assumptions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Diversion Estimate Range")

    div_low, div_high = s["annual_diversion_tonnes_range"]
    div_mid = s["annual_diversion_tonnes"]

    fig5 = go.Figure()

    fig5.add_trace(go.Bar(
        x=["Low", "Mid", "High"],
        y=[div_low, div_mid, div_high],
        marker_color=["#EF4444", "#F59E0B", "#10B981"],
        text=[f"{div_low:,}", f"{div_mid:,}", f"{div_high:,}"],
        textposition="auto"
    ))

    fig5.update_layout(
        yaxis_title="Annual Diversion (tonnes/year)",
        showlegend=False,
        height=300
    )

    st.plotly_chart(fig5, width="stretch")

    st.caption(f"**Uncertainty range:** ±{((div_high - div_low) / div_mid * 100):.0f}% around midpoint")

with col2:
    st.markdown("### Key Assumptions")

    st.markdown(f"""
    **Scenario:** {s["name"]}

    {s.get("notes", "")}

    **Modeling Notes:**
    - Baseline and static scenarios use measured pipeline outputs
    - Mobile and hybrid scenarios use modeled estimates
    - All ranges reflect ±40% uncertainty
    - Validate through 90-day pilot before scaling
    """)

st.markdown("---")

# Summary
st.info(f"""
**Summary for {scenario_options[selected_scenario]}:**

This scenario reduces the textile burden from {baseline['textile_burden_pct']:.1f}% to {s['textile_burden_pct']:.1f}%,
serving an additional {s['beneficiary_estates']} estates and diverting an estimated {s['annual_diversion_tonnes']:,} tonnes/year
from landfills at a total 5-year cost of HK${s['total_cost_hkd'] / 1e6:.1f}M.

District inequality (Gini) improves from {baseline['district_gini']:.3f} to {s['district_gini']:.3f},
with {s['worst_quartile_improvement']} estates in the most vulnerable districts gaining access.
""")

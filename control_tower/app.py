#!/usr/bin/env python3
"""
Green Loop Control Tower - Interactive Policy Dashboard
DataHack 2026 Submission
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Green Loop Control Tower",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "processed"
CONTROL_TOWER = ROOT / "control_tower"

# Load precomputed scenarios
@st.cache_data
def load_scenarios():
    with open(CONTROL_TOWER / "scenario_outputs.json") as f:
        return json.load(f)

@st.cache_data
def load_estates():
    return pd.read_csv(DATA / "estates_full_analysis.csv")

@st.cache_data
def load_hubs():
    return pd.read_csv(DATA / "optimized_hubs.csv")

# Load data
scenarios_data = load_scenarios()
estates = load_estates()
hubs = load_hubs()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .scenario-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0f172a;
    }
    .assumption-box {
        background: #fef3c7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<div class="main-header">♻️ Green Loop Control Tower</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Data-Driven Recycling Policy Simulator | DataHack 2026</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

st.sidebar.title("⚙️ Policy Controls")

# Scenario selector
scenario_options = {
    "baseline": "🔴 Baseline (Current State)",
    "static_hubs": "🏢 Static Hubs (Infrastructure-First)",
    "mobile_first": "🚛 Mobile-First (Flexible Operations)",
    "hybrid_equity": "⚖️ Hybrid Equity (Balanced Approach)"
}

selected_scenario = st.sidebar.selectbox(
    "Select Strategy:",
    options=list(scenario_options.keys()),
    format_func=lambda x: scenario_options[x],
    index=3  # Default to hybrid_equity
)

current = scenarios_data["scenarios"][selected_scenario]
baseline_metrics = scenarios_data["scenarios"]["baseline"]

st.sidebar.markdown("---")

# Budget slider
budget_millions = st.sidebar.slider(
    "Budget (HK$ Million)",
    min_value=0,
    max_value=80,
    value=int(current["capex_hkd"] / 1e6),
    step=5,
    help="Adjust total budget - scenario will auto-select based on available funding"
)

# Auto-select scenario based on budget
if budget_millions < 20 and selected_scenario != "baseline":
    st.sidebar.warning("⚠️ Budget too low for this scenario. Consider Baseline or Mobile-First.")
elif budget_millions >= 20 and budget_millions < 30:
    if selected_scenario not in ["baseline", "mobile_first"]:
        st.sidebar.info("💡 Budget suits Mobile-First strategy")
elif budget_millions >= 30 and budget_millions < 45:
    if selected_scenario != "hybrid_equity":
        st.sidebar.info("💡 Budget suits Hybrid Equity strategy")
elif budget_millions >= 45:
    if selected_scenario != "static_hubs":
        st.sidebar.info("💡 Budget suits Static Hubs strategy")

st.sidebar.markdown("---")

# Equity priority slider
equity_weight = st.sidebar.slider(
    "Equity Priority (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=10,
    help="Higher values prioritize equal distribution over total tonnage"
)

if equity_weight > 70:
    st.sidebar.success("✓ High equity mode - prioritizes worst-served districts")
elif equity_weight < 30:
    st.sidebar.info("ℹ️ Impact-first mode - maximizes total diversion")

st.sidebar.markdown("---")

# View mode
view_mode = st.sidebar.radio(
    "Display Mode:",
    ["📊 Overview", "🗺️ Map Details", "📈 Equity Analysis", "⚙️ Assumptions"]
)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Overview metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_estates = current["estates_over_500m"] - baseline_metrics["estates_over_500m"]
    st.metric(
        "Estates >500m",
        f"{current['estates_over_500m']}",
        delta=f"{delta_estates} estates",
        delta_color="inverse"
    )

with col2:
    delta_burden = current["textile_burden_pct"] - baseline_metrics["textile_burden_pct"]
    st.metric(
        "Textile Burden",
        f"{current['textile_burden_pct']:.1f}%",
        delta=f"{delta_burden:.1f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "Annual Diversion",
        f"{current['annual_diversion_tonnes']:,} tonnes",
        delta=f"+{current['annual_diversion_tonnes']:,} vs baseline"
    )

with col4:
    gini_delta = current["district_gini"] - baseline_metrics["district_gini"]
    st.metric(
        "District Inequality (Gini)",
        f"{current['district_gini']:.2f}",
        delta=f"{gini_delta:.2f}",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================================================
# VIEW MODES
# ============================================================================

if view_mode == "📊 Overview":
    st.subheader(f"Strategy: {scenario_options[selected_scenario]}")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Comparison chart
        st.markdown("### Scenario Comparison")

        comparison_data = []
        for scenario_key, scenario_name in scenario_options.items():
            metrics = scenarios_data["scenarios"][scenario_key]
            comparison_data.append({
                "Scenario": scenario_name.split(" (")[0],  # Remove description
                "Estates >500m": metrics["estates_over_500m"],
                "Burden %": metrics["textile_burden_pct"],
                "Diversion (tonnes/yr)": metrics["annual_diversion_tonnes"],
                "Cost (HK$M)": metrics["total_cost_hkd"] / 1e6,
                "Gini": metrics["district_gini"]
            })

        comparison_df = pd.DataFrame(comparison_data)

        # Create multi-metric comparison
        fig = go.Figure()

        # Estates >500m (lower is better)
        fig.add_trace(go.Bar(
            name="Estates >500m",
            x=comparison_df["Scenario"],
            y=comparison_df["Estates >500m"],
            marker_color="#ef4444"
        ))

        fig.update_layout(
            title="Key Metrics Across Scenarios",
            xaxis_title="",
            yaxis_title="Estates >500m from Textile Recycling",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Strategy Details")

        st.markdown(f"""
        **Current Selection:** {scenario_options[selected_scenario]}

        **Interventions:**
        """)

        # Show interventions based on scenario
        if selected_scenario == "baseline":
            st.info("No interventions - current state")
        elif selected_scenario == "static_hubs":
            st.success("✓ 10 fixed multi-stream hubs")
            st.info("📍 Locations from greedy max-coverage optimization")
        elif selected_scenario == "mobile_first":
            st.success("✓ 3 mobile collection trucks")
            st.success("✓ 15 retrofitted existing points")
            st.info("🚛 2-week rotation through 20 high-lockout estates")
        elif selected_scenario == "hybrid_equity":
            st.success("✓ 5 fixed hubs")
            st.success("✓ 2 mobile trucks")
            st.success("✓ 15 retrofitted points")
            st.success("✓ Incentive pilots in 3 districts")
            st.info("⚖️ Equity-weighted allocation")

        st.markdown("---")

        st.markdown(f"""
        **Financial Summary:**
        - Capex: HK${current['capex_hkd'] / 1e6:.1f}M
        - Annual Opex: HK${current['annual_opex_hkd'] / 1e6:.1f}M
        - 5-Year Total: HK${current['total_cost_hkd'] / 1e6:.1f}M
        """)

        if current.get('payback_years'):
            range_str = f"{current.get('payback_years_range', [current['payback_years'], current['payback_years']])[0]}-{current.get('payback_years_range', [current['payback_years'], current['payback_years']])[1]}"
            st.markdown(f"**Payback Period:** {range_str} years")

elif view_mode == "🗺️ Map Details":
    st.subheader("Geographic Distribution")

    # Create map
    estates_copy = estates.copy()

    # Color estates by textile distance
    def get_estate_color(dist):
        if dist > 800:
            return "#dc2626"  # Red - severe
        elif dist > 500:
            return "#f59e0b"  # Orange - underserved
        elif dist > 300:
            return "#fbbf24"  # Yellow - moderate
        else:
            return "#10b981"  # Green - well-served

    estates_copy["color"] = estates_copy["dist_textiles"].apply(get_estate_color)

    fig = go.Figure()

    # Add estates
    fig.add_trace(go.Scattermapbox(
        lat=estates_copy["lat"],
        lon=estates_copy["lon"],
        mode="markers",
        marker=dict(
            size=estates_copy["pop"] / 500,  # Scale by population
            color=estates_copy["color"],
            opacity=0.7
        ),
        text=estates_copy.apply(lambda r: f"{r['name']}<br>Distance: {r['dist_textiles']:.0f}m<br>Pop: {r['pop']:,}", axis=1),
        hoverinfo="text",
        name="Estates"
    ))

    # Add hubs if not baseline
    if selected_scenario != "baseline":
        hub_count = 10 if selected_scenario == "static_hubs" else 5
        hubs_to_show = hubs.head(hub_count)

        fig.add_trace(go.Scattermapbox(
            lat=hubs_to_show["lat"],
            lon=hubs_to_show["lon"],
            mode="markers",
            marker=dict(
                size=15,
                color="#3b82f6",
                symbol="star"
            ),
            text=hubs_to_show.apply(lambda r: f"Hub {r['hub_rank']}: {r['estate']}<br>Coverage: {r['population_in_radius']:,} residents", axis=1),
            hoverinfo="text",
            name="Proposed Hubs"
        ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=22.35, lon=114.15),
            zoom=10
        ),
        height=600,
        showlegend=True,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Legend
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("🟢 **<300m** - Well-served")
    col2.markdown("🟡 **300-500m** - Moderate")
    col3.markdown("🟠 **500-800m** - Underserved")
    col4.markdown("🔴 **>800m** - Severe barrier")

elif view_mode == "📈 Equity Analysis":
    st.subheader("Equity & Fairness Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Primary Equity Metric")

        # Textile burden progress bar
        burden_pct = current["textile_burden_pct"]
        target_pct = 30.0

        st.markdown(f"""
        **Textile Population Burden (>500m):**

        Current: **{burden_pct:.1f}%** (down from {baseline_metrics['textile_burden_pct']:.1f}%)

        Target: <{target_pct}%
        """)

        # Progress bar
        progress = min(1.0, (baseline_metrics['textile_burden_pct'] - burden_pct) / (baseline_metrics['textile_burden_pct'] - target_pct))
        st.progress(progress)

        if burden_pct <= target_pct:
            st.success(f"✓ TARGET MET: {burden_pct:.1f}% ≤ {target_pct}%")
        else:
            remaining = burden_pct - target_pct
            st.warning(f"⚠️ {remaining:.1f}% above target - {int((remaining / 100) * 2262060):,} residents still >500m")

    with col2:
        st.markdown("### Secondary Equity Metric")

        gini = current["district_gini"]
        baseline_gini = baseline_metrics["district_gini"]

        st.markdown(f"""
        **District Inequality (Gini Coefficient):**

        Current: **{gini:.2f}** (down from {baseline_gini:.2f})

        Lower is more equal.
        """)

        # Comparison across scenarios
        gini_data = pd.DataFrame([
            {"Scenario": "Baseline", "Gini": baseline_gini},
            {"Scenario": "Static Hubs", "Gini": scenarios_data["scenarios"]["static_hubs"]["district_gini"]},
            {"Scenario": "Mobile-First", "Gini": scenarios_data["scenarios"]["mobile_first"]["district_gini"]},
            {"Scenario": "Hybrid Equity", "Gini": scenarios_data["scenarios"]["hybrid_equity"]["district_gini"]}
        ])

        fig = px.bar(
            gini_data,
            x="Scenario",
            y="Gini",
            color="Gini",
            color_continuous_scale=["#10b981", "#fbbf24", "#ef4444"],
            title="District Inequality Across Scenarios"
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Beneficiary analysis
    st.markdown("---")
    st.markdown("### Who Benefits?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Estates Improved",
            current.get("beneficiary_estates", 0),
            delta=f"out of {baseline_metrics['estates_over_500m']} underserved"
        )

    with col2:
        pop_saved = baseline_metrics["population_over_500m"] - current["population_over_500m"]
        st.metric(
            "Residents Saved from >500m Zone",
            f"{pop_saved:,}",
            delta=f"{(pop_saved / baseline_metrics['population_over_500m'] * 100):.1f}% of underserved"
        )

    with col3:
        if current.get("worst_quartile_improvement"):
            st.metric(
                "Worst-Quartile Estates Improved",
                current["worst_quartile_improvement"],
                delta="Priority targeting"
            )

elif view_mode == "⚙️ Assumptions":
    st.subheader("Model Assumptions & Sensitivity")

    st.markdown("""
    <div class="assumption-box">
    <strong>⚠️ IMPORTANT:</strong> All intervention effects are <strong>MODELED ESTIMATES</strong> requiring validation through pilot implementation.
    Uncertainty range: <strong>±40%</strong> for all diversion and cost projections.
    </div>
    """, unsafe_allow_html=True)

    # Assumptions table
    st.markdown("### Key Assumptions")

    assumptions_data = {
        "Parameter": [
            "Distance Threshold (Underserved)",
            "Hub Service Radius",
            "Population Proxy",
            "New Hub Diversion",
            "Mobile Truck Diversion",
            "Retrofit Diversion",
            "Landfill Gate Fee"
        ],
        "Value": [
            ">500m",
            "800m",
            "rental_flats × 2.7",
            "0.8-1.5 tpd per hub",
            "1.2-2.0 tpd per truck",
            "0.3-0.6 tpd per retrofit cluster",
            "HK$365/tonne"
        ],
        "Source/Justification": [
            "Urban planning literature (participation drops 40-60%)",
            "10-minute walkable catchment (standard)",
            "Housing Authority standard occupancy rate",
            "MODELED - requires validation",
            "MODELED - requires validation",
            "MODELED - requires validation",
            "EPD current landfill fee (2024)"
        ]
    }

    st.table(pd.DataFrame(assumptions_data))

    # Sensitivity analysis
    st.markdown("---")
    st.markdown("### Sensitivity Analysis")

    st.markdown(f"""
    **What if our estimates are wrong?**

    Current scenario: **{scenario_options[selected_scenario]}**
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Optimistic Case** (+40% effectiveness)")
        optimistic_diversion = int(current["annual_diversion_tonnes"] * 1.4)
        st.markdown(f"- Diversion: {optimistic_diversion:,} tonnes/year")
        if current.get("payback_years_range"):
            st.markdown(f"- Payback: {current['payback_years_range'][0]} years")

    with col2:
        st.markdown("**Conservative Case** (-40% effectiveness)")
        conservative_diversion = int(current["annual_diversion_tonnes"] * 0.6)
        st.markdown(f"- Diversion: {conservative_diversion:,} tonnes/year")
        if current.get("payback_years_range"):
            st.markdown(f"- Payback: {current['payback_years_range'][1]} years")

    # Validation plan
    st.markdown("---")
    st.markdown("### 90-Day Validation Protocol")

    st.markdown("""
    **Phase 1: Baseline (Weeks 1-2)**
    - Install counters at 5 high-lockout estates
    - Measure actual textile tonnage
    - Validate population proxy (expected ±15% accuracy)

    **Phase 2: Pilot (Weeks 3-8)**
    - Deploy intervention based on selected scenario
    - Measure uplift vs baseline weekly

    **Phase 3: Validation (Weeks 9-10)**
    - Compare actual vs modeled uplift
    - If actual >70% of modeled → proceed to scale
    - If actual 40-70% → adjust model + re-test
    - If actual <40% → redesign intervention

    **Phase 4: Scale Decision (Weeks 11-12)**
    - Present findings to EPD
    - Recommend: expand OR pivot
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem;">
<strong>Green Loop Control Tower</strong> | DataHack 2026 Submission<br>
Data Sources: data.gov.hk (Collection Points, Public Housing, Historical Waste Data)<br>
Team: Saleh Furqan & Ibrahim Malik
</div>
""", unsafe_allow_html=True)

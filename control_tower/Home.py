#!/usr/bin/env python3
"""
Green Loop Control Tower - Main Landing Page
Interactive policy simulator for Hong Kong's recycling network
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

try:
    from control_tower.backend.theme import apply_theme
except ModuleNotFoundError:
    from backend.theme import apply_theme

# Page config
st.set_page_config(
    page_title="Green Loop Control Tower",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# Load data
DATA_PATH = Path(__file__).parent / "data" / "scenario_outputs.json"

@st.cache_data
def load_scenario_data():
    with open(DATA_PATH) as f:
        return json.load(f)

data = load_scenario_data()
scenarios = data["scenarios"]

# Header
st.title("🌱 Green Loop Control Tower")
st.markdown("**Interactive Policy Simulator for Hong Kong's Recycling Network**")

st.markdown("---")

# Quick Status Overview
st.subheader("Current Status & Best Scenario Impact")

baseline = scenarios["baseline"]
static = scenarios["static_hubs"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_estates = static["estates_over_500m"] - baseline["estates_over_500m"]
    st.metric(
        "Estates >500m",
        f"{static['estates_over_500m']}",
        delta=f"{delta_estates}",
        delta_color="inverse"
    )

with col2:
    delta_burden = static["textile_burden_pct"] - baseline["textile_burden_pct"]
    st.metric(
        "Textile Burden",
        f"{static['textile_burden_pct']:.1f}%",
        delta=f"{delta_burden:.1f}%",
        delta_color="inverse"
    )

with col3:
    diversion_mid = static["annual_diversion_tonnes"]
    st.metric(
        "Annual Diversion",
        f"{diversion_mid:,} t/y",
        delta=f"+{diversion_mid:,}",
        delta_color="normal"
    )

with col4:
    delta_gini = static["district_gini"] - baseline["district_gini"]
    st.metric(
        "District Inequality (Gini)",
        f"{static['district_gini']:.3f}",
        delta=f"{delta_gini:.3f}",
        delta_color="inverse"
    )

st.markdown("---")

# Navigation Cards
st.subheader("Explore the Control Tower")

st.markdown("""
Use the **sidebar** or click the links below to navigate:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🗺️ Interactive Map")
    st.markdown("""
    Explore Hong Kong estates with interactive mapping:
    - **Clickable estates** color-coded by coverage level
    - **Hub locations** overlayed on real HK geography
    - **Optional district boundary overlays** when GeoJSON is provided
    - **Filters** by district and distance threshold
    """)
    st.page_link("pages/1_🗺️_Interactive_Map.py", label="Open Interactive Map →", icon="🗺️")

    st.markdown("### 📈 Impact Analysis")
    st.markdown("""
    Detailed metrics and beneficiary analysis:
    - **Top beneficiaries** by estate and population
    - **Coverage charts** showing improvement distribution
    - **Diversion estimates** with uncertainty ranges
    - **Cost-benefit analysis** with payback periods
    """)
    st.page_link("pages/3_📈_Impact_Analysis.py", label="View Impact Analysis →", icon="📈")

with col2:
    st.markdown("### 📊 Scenario Comparison with Optimization Engine")
    st.markdown("""
    Advanced policy analysis with real algorithms:
    - **Split-map view** with side-by-side before/after visualization
    - **Pareto frontier analysis** (multi-objective optimization)
    - **Live greedy max-coverage** algorithm simulation
    - **3D tradeoff visualization** (cost vs equity vs impact)
    - **Radar charts** for multi-dimensional comparison
    """)
    st.page_link("pages/2_📊_Scenario_Compare.py", label="Run Optimization Analysis →", icon="📊")

    st.markdown("### ⚙️ Methodology & Assumptions")
    st.markdown("""
    Transparency and validation:
    - **Data sources** and processing pipeline
    - **Modeling assumptions** with uncertainty ranges
    - **Validation protocol** for pilot deployment
    - **Technical documentation**
    """)
    st.page_link("pages/4_⚙️_Assumptions.py", label="View Assumptions →", icon="⚙️")

st.markdown("---")

# Quick Scenario Comparison Table
st.subheader("Scenario Summary")

comparison_data = []
for key in ["baseline", "mobile_first", "hybrid_equity", "static_hubs"]:
    s = scenarios[key]
    comparison_data.append({
        "Scenario": s["name"],
        "Estates >500m": s["estates_over_500m"],
        "Burden %": f"{s['textile_burden_pct']:.1f}%",
        "Diversion (t/y)": f"{s['annual_diversion_tonnes_range'][0]:,} - {s['annual_diversion_tonnes_range'][1]:,}",
        "Cost (HK$M)": f"{s['total_cost_hkd'] / 1e6:.1f}",
        "Payback (years)": f"{s['payback_years']:.1f}" if s['payback_years'] else "N/A",
        "Gini": f"{s['district_gini']:.3f}"
    })

df = pd.DataFrame(comparison_data)
st.dataframe(df, width="stretch", hide_index=True)

st.markdown("---")

# Footer
st.markdown("""
**About:** The Green Loop Control Tower is a decision-support tool for optimizing Hong Kong's recycling infrastructure.
It combines geospatial analysis, optimization algorithms, and scenario modeling to help policymakers understand tradeoffs
between cost, equity, and environmental impact.

**Data:** Based on real Hong Kong public housing estates, recycling point locations, and demographic data.
Baseline and static hub scenarios are measured from pipeline outputs; mobile and hybrid scenarios are modeled estimates.
""")

st.info("💡 **Tip:** Start with the Interactive Map to explore estate-level coverage, then use Scenario Compare to understand tradeoffs.")

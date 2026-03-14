#!/usr/bin/env python3
"""Green Loop Control Tower - polished landing page."""

import pandas as pd
import streamlit as st

try:
    from control_tower.backend.scenario_engine import recommend_scenario
    from control_tower.backend.data_loader import load_scenario_outputs
    from control_tower.backend.theme import apply_theme
except ModuleNotFoundError:
    from backend.scenario_engine import recommend_scenario
    from backend.data_loader import load_scenario_outputs
    from backend.theme import apply_theme


st.set_page_config(
    page_title="Green Loop Control Tower",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


@st.cache_data
def load_data() -> dict:
    return load_scenario_outputs()


data = load_data()
scenarios = data["scenarios"]
baseline = scenarios["baseline"]
static = scenarios["static_hubs"]

st.markdown(
    """
<div class="gl-hero">
  <p class="gl-eyebrow">DataHack 2026 Demo App</p>
  <h2>Green Loop Control Tower</h2>
  <p>Interactive decision support for Hong Kong textile recycling access.
  Baseline + static hub scenarios are measured from pipeline outputs; mobile/hybrid are modeled with explicit assumptions.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.subheader("Headline Metrics (Baseline vs Static Hubs)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Estates >500m",
        f"{static['estates_over_500m']}",
        delta=f"{static['estates_over_500m'] - baseline['estates_over_500m']}",
        delta_color="inverse",
    )
with col2:
    st.metric(
        "Textile Burden",
        f"{static['textile_burden_pct']:.1f}%",
        delta=f"{static['textile_burden_pct'] - baseline['textile_burden_pct']:.1f}%",
        delta_color="inverse",
    )
with col3:
    st.metric(
        "Additional Diversion",
        f"{static['annual_diversion_tonnes_range'][0]:,}–{static['annual_diversion_tonnes_range'][1]:,} t/y",
    )
with col4:
    st.metric(
        "District Gini",
        f"{static['district_gini']:.3f}",
        delta=f"{static['district_gini'] - baseline['district_gini']:.3f}",
        delta_color="inverse",
    )

st.markdown("---")

st.subheader("Policy Selector")
control_col, reco_col = st.columns([1.2, 1.0])

with control_col:
    budget_m = st.slider("Budget (Capex, HK$M)", min_value=0, max_value=80, value=35, step=5)
    equity_weight = st.slider("Equity Priority", min_value=0, max_value=100, value=60, step=5)
    st.caption("Lower equity priority favors total diversion; higher equity priority favors distribution fairness.")

recommended_key = recommend_scenario(data, budget_m, equity_weight)
recommended = scenarios[recommended_key]

with reco_col:
    st.markdown('<div class="gl-panel">', unsafe_allow_html=True)
    st.markdown(f"**Recommended Mode:** `{recommended['name']}`")
    st.markdown(
        f"- Estates >500m: **{recommended['estates_over_500m']}**\n"
        f"- Burden: **{recommended['textile_burden_pct']:.1f}%**\n"
        f"- Diversion range: **{recommended['annual_diversion_tonnes_range'][0]:,}–{recommended['annual_diversion_tonnes_range'][1]:,} t/y**\n"
        f"- Capex: **HK${recommended['capex_hkd'] / 1e6:.1f}M**"
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("Navigate")
nav_left, nav_right = st.columns(2)

with nav_left:
    st.markdown("### 🗺️ Interactive Map")
    st.markdown("Estate markers, proposed hubs, and stream-specific public collection layers on a real HK basemap.")
    st.page_link("pages/1_🗺️_Interactive_Map.py", label="Open Map", icon="🗺️")

    st.markdown("### 📈 Impact Analysis")
    st.markdown("Coverage change, beneficiary estates, and cost/diversion ranges with clear measured vs modeled context.")
    st.page_link("pages/3_📈_Impact_Analysis.py", label="Open Impact Analysis", icon="📈")

with nav_right:
    st.markdown("### 📊 Scenario Compare")
    st.markdown("Scenario tradeoffs with split-map comparison, optimization simulation, and compact policy diagnostics.")
    st.page_link("pages/2_📊_Scenario_Compare.py", label="Open Scenario Compare", icon="📊")

    st.markdown("### ⚙️ Assumptions")
    st.markdown("Data sources, uncertainty bands, and 90-day validation protocol for defensible presentation claims.")
    st.page_link("pages/4_⚙️_Assumptions.py", label="Open Assumptions", icon="⚙️")

st.markdown("---")
st.subheader("Scenario Snapshot")

rows = []
for key in ["baseline", "mobile_first", "hybrid_equity", "static_hubs"]:
    s = scenarios[key]
    rows.append(
        {
            "Scenario": s["name"],
            "Estates >500m": s["estates_over_500m"],
            "Burden %": s["textile_burden_pct"],
            "Diversion Range (t/y)": f"{s['annual_diversion_tonnes_range'][0]:,} - {s['annual_diversion_tonnes_range'][1]:,}",
            "Capex (HK$M)": round(s["capex_hkd"] / 1e6, 1),
            "5Y Total Cost (HK$M)": round(s["total_cost_hkd"] / 1e6, 1),
            "Gini": s["district_gini"],
        }
    )

df = pd.DataFrame(rows)
st.dataframe(
    df,
    width="stretch",
    hide_index=True,
    column_config={
        "Burden %": st.column_config.NumberColumn(format="%.1f"),
        "Capex (HK$M)": st.column_config.NumberColumn(format="%.1f"),
        "5Y Total Cost (HK$M)": st.column_config.NumberColumn(format="%.1f"),
        "Gini": st.column_config.NumberColumn(format="%.3f"),
    },
)

st.info(
    "Start with the map page for the visual story, then use Impact + Assumptions pages to support Q&A with exact numbers."
)

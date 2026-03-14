#!/usr/bin/env python3
"""
Scenario Comparison - policy tradeoffs and optimization diagnostics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from scipy.spatial.distance import cdist

try:
    from control_tower.backend.theme import apply_theme
    from control_tower.backend.data_loader import (
        load_district_geojson,
        load_estates,
        load_hubs,
        load_scenario_outputs,
    )
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from backend.theme import apply_theme
    from backend.data_loader import (
        load_district_geojson,
        load_estates,
        load_hubs,
        load_scenario_outputs,
    )

# Page config
st.set_page_config(
    page_title="Scenario Compare - Green Loop",
    page_icon="📊",
    layout="wide"
)
apply_theme()

@st.cache_data
def get_inputs():
    return (
        load_scenario_outputs(),
        load_estates(),
        load_hubs(),
        load_district_geojson(),
    )


data, estates, hubs, district_geojson = get_inputs()
scenarios = data["scenarios"]

# Initialize session state
if "pareto_computed" not in st.session_state:
    st.session_state.pareto_computed = False

# Header
st.title("📊 Scenario Compare")
st.markdown("**Policy tradeoffs across baseline, static hubs, mobile-first, and hybrid equity modes.**")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Split-Map Comparison",
    "📈 Tradeoff Frontier",
    "⚡ Greedy Placement Simulator",
    "📊 Metrics Dashboard"
])

# ============================================================================
# TAB 1: SPLIT-MAP COMPARISON
# ============================================================================
with tab1:
    st.subheader("🗺️ Side-by-Side Map Comparison")

    col1, col2 = st.columns(2)

    scenario_options = {
        "baseline": "Baseline (Current)",
        "static_hubs": "Static Hubs",
        "mobile_first": "Mobile-First",
        "hybrid_equity": "Hybrid Equity"
    }

    with col1:
        scenario_left = st.selectbox(
            "Left Map",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x],
            index=0,
            key="left_scenario"
        )

    with col2:
        scenario_right = st.selectbox(
            "Right Map",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x],
            index=1,
            key="right_scenario"
        )

    def get_color(distance):
        """Sustainability-themed color scheme."""
        if distance < 300:
            return "#2E7D32"  # Dark Green
        elif distance < 500:
            return "#7CB342"  # Light Green
        elif distance < 800:
            return "#C0A04C"  # Olive/Gold
        else:
            return "#8D6E63"  # Brown

    def create_scenario_map(scenario_key, title):
        """Create a map for a given scenario."""
        m = folium.Map(
            location=[22.3193, 114.1694],
            zoom_start=11,
            tiles="CartoDB positron"
        )
        if district_geojson is not None:
            folium.GeoJson(
                district_geojson,
                name="District Boundaries",
                style_function=lambda _feature: {
                    "fillColor": "#00000000",
                    "color": "#5D6F63",
                    "weight": 1.0,
                    "fillOpacity": 0,
                },
            ).add_to(m)

        s = scenarios[scenario_key]

        # Get distances
        if "estate_distances_m" in s and scenario_key != "baseline":
            candidate_distances = np.asarray(s["estate_distances_m"], dtype=float)
            if len(candidate_distances) == len(estates):
                distances = candidate_distances
            else:
                distances = estates["dist_textiles"].to_numpy(dtype=float)
        else:
            distances = estates["dist_textiles"].to_numpy(dtype=float)

        # Add estates
        for idx, row in estates.iterrows():
            dist = distances[idx]
            color = get_color(dist)

            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=4,
                popup=f"<b>{row['estate']}</b><br>Distance: {int(dist)}m",
                tooltip=f"{row['estate']}: {int(dist)}m",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=1
            ).add_to(m)

        # Add hubs if applicable
        hubs_to_show = int(s.get("interventions", {}).get("new_hubs", 0))
        if hubs_to_show > 0:
            for idx, row in hubs.head(hubs_to_show).iterrows():
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    popup=f"Hub #{int(row['hub_rank'])}",
                    tooltip=f"Hub #{int(row['hub_rank'])}",
                    icon=folium.Icon(color="green", icon="recycle", prefix="fa", icon_color="white")
                ).add_to(m)

        # Add title with sustainability theme
        title_html = f'''
        <div style="position: fixed;
             top: 10px; left: 50%; transform: translateX(-50%);
             z-index: 9999; background-color: rgba(255, 255, 255, 0.98);
             padding: 10px 20px; border-radius: 8px;
             border: 2px solid #2E7D32; box-shadow: 0 3px 8px rgba(46, 125, 50, 0.2);">
            <h4 style="margin: 0; color: #1B5E20; font-size: 16px;">{title}</h4>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        return m

    # Create maps
    col_left, col_right = st.columns(2)

    with col_left:
        map_left = create_scenario_map(scenario_left, scenario_options[scenario_left])
        st_folium(
            map_left,
            width=650,
            height=500,
            key=f"map_left_{scenario_left}"
        )

        s_left = scenarios[scenario_left]
        st.metric("Burden %", f"{s_left['textile_burden_pct']:.1f}%")
        st.metric(
            "Diversion Range (t/y)",
            f"{s_left['annual_diversion_tonnes_range'][0]:,}-{s_left['annual_diversion_tonnes_range'][1]:,}",
        )

    with col_right:
        map_right = create_scenario_map(scenario_right, scenario_options[scenario_right])
        st_folium(
            map_right,
            width=650,
            height=500,
            key=f"map_right_{scenario_right}"
        )

        s_right = scenarios[scenario_right]
        st.metric("Burden %", f"{s_right['textile_burden_pct']:.1f}%")
        st.metric(
            "Diversion Range (t/y)",
            f"{s_right['annual_diversion_tonnes_range'][0]:,}-{s_right['annual_diversion_tonnes_range'][1]:,}",
        )

    # Comparison metrics
    st.markdown("### 📊 Comparison Summary")

    delta_burden = s_right['textile_burden_pct'] - s_left['textile_burden_pct']
    left_mid = (s_left["annual_diversion_tonnes_range"][0] + s_left["annual_diversion_tonnes_range"][1]) / 2
    right_mid = (s_right["annual_diversion_tonnes_range"][0] + s_right["annual_diversion_tonnes_range"][1]) / 2
    delta_diversion = right_mid - left_mid
    delta_cost = s_right['total_cost_hkd'] - s_left['total_cost_hkd']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Burden Difference",
            f"{abs(delta_burden):.1f}%",
            delta=f"{delta_burden:.1f}%",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            "Diversion Difference (midpoint)",
            f"{int(abs(delta_diversion)):,} t/y",
            delta=f"{int(delta_diversion):+,}",
            delta_color="normal"
        )

    with col3:
        st.metric(
            "Cost Difference",
            f"HK${abs(delta_cost / 1e6):.1f}M",
            delta=f"{delta_cost / 1e6:+.1f}M",
            delta_color="inverse"
        )

    with col4:
        delta_gini = s_right['district_gini'] - s_left['district_gini']
        st.metric(
            "Gini Difference",
            f"{abs(delta_gini):.3f}",
            delta=f"{delta_gini:.3f}",
            delta_color="inverse"
        )

# ============================================================================
# TAB 2: PARETO FRONTIER ANALYSIS
# ============================================================================
with tab2:
    st.subheader("📈 Tradeoff Frontier")

    st.markdown("""
    **What is a Pareto Frontier?**

    In multi-objective optimization, a solution is **Pareto optimal** if you cannot improve one objective
    without worsening another. The Pareto frontier shows all non-dominated solutions.

    **Our objectives:**
    1. **Minimize** textile burden (equity)
    2. **Maximize** diversion (environmental impact)
    3. **Minimize** cost (economic efficiency)
    """)

    # Compute Pareto frontier
    @st.cache_data
    def compute_pareto_frontier():
        """Identify Pareto-optimal scenarios using dominance analysis."""
        points = []
        for key in ["baseline", "mobile_first", "hybrid_equity", "static_hubs"]:
            s = scenarios[key]
            points.append({
                "name": s["name"],
                "key": key,
                "burden": s["textile_burden_pct"],  # Minimize
                "diversion": s["annual_diversion_tonnes"],  # Maximize
                "cost": s["total_cost_hkd"] / 1e6,  # Minimize
                "gini": s["district_gini"]
            })

        df = pd.DataFrame(points)

        # Pareto dominance: A dominates B if:
        # A.burden <= B.burden AND A.cost <= B.cost AND A.diversion >= B.diversion
        # AND at least one is strict inequality

        pareto_optimal = []
        for i, row_i in df.iterrows():
            dominated = False
            for j, row_j in df.iterrows():
                if i == j:
                    continue

                # Check if j dominates i
                if (row_j['burden'] <= row_i['burden'] and
                    row_j['cost'] <= row_i['cost'] and
                    row_j['diversion'] >= row_i['diversion'] and
                    (row_j['burden'] < row_i['burden'] or
                     row_j['cost'] < row_i['cost'] or
                     row_j['diversion'] > row_i['diversion'])):
                    dominated = True
                    break

            pareto_optimal.append(not dominated)

        df['pareto_optimal'] = pareto_optimal
        return df

    pareto_df = compute_pareto_frontier()

    # Show Pareto table
    st.markdown("### Pareto Optimality Analysis")

    display_df = pareto_df[['name', 'burden', 'diversion', 'cost', 'gini', 'pareto_optimal']].copy()
    display_df.columns = ['Scenario', 'Burden %', 'Diversion (t/y)', 'Cost (HK$M)', 'Gini', 'Pareto Optimal?']

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Pareto Optimal?": st.column_config.CheckboxColumn("Pareto Optimal?"),
            "Burden %": st.column_config.NumberColumn("Burden %", format="%.1f"),
            "Diversion (t/y)": st.column_config.NumberColumn("Diversion (t/y)", format="%d"),
            "Cost (HK$M)": st.column_config.NumberColumn("Cost (HK$M)", format="%.1f"),
            "Gini": st.column_config.NumberColumn("Gini", format="%.3f")
        }
    )

    optimal_count = pareto_df['pareto_optimal'].sum()
    st.success(f"**{optimal_count} / 4** scenarios are Pareto optimal (non-dominated)")

    # 3D Pareto frontier visualization
    st.markdown("### 3D Pareto Frontier")

    fig = go.Figure()

    # Pareto optimal points
    pareto_points = pareto_df[pareto_df['pareto_optimal']]
    non_pareto_points = pareto_df[~pareto_df['pareto_optimal']]

    fig.add_trace(go.Scatter3d(
        x=pareto_points['cost'],
        y=pareto_points['burden'],
        z=pareto_points['diversion'],
        mode='markers+text',
        marker=dict(
            size=12,
            color='green',
            symbol='diamond',
            line=dict(width=2, color='white')
        ),
        text=pareto_points['name'],
        textposition='top center',
        name='Pareto Optimal',
        hovertemplate="<b>%{text}</b><br>" +
                      "Cost: HK$%{x:.1f}M<br>" +
                      "Burden: %{y:.1f}%<br>" +
                      "Diversion: %{z:,} t/y<br>" +
                      "<extra></extra>"
    ))

    if len(non_pareto_points) > 0:
        fig.add_trace(go.Scatter3d(
            x=non_pareto_points['cost'],
            y=non_pareto_points['burden'],
            z=non_pareto_points['diversion'],
            mode='markers+text',
            marker=dict(
                size=10,
                color='#C5E1A5',
                symbol='circle',
                line=dict(width=1, color='#9CCC65')
            ),
            text=non_pareto_points['name'],
            textposition='top center',
            name='Dominated',
            hovertemplate="<b>%{text}</b><br>" +
                          "Cost: HK$%{x:.1f}M<br>" +
                          "Burden: %{y:.1f}%<br>" +
                          "Diversion: %{z:,} t/y<br>" +
                          "<extra></extra>"
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Cost (HK$ Million)',
            yaxis_title='Burden % (lower is better)',
            zaxis_title='Diversion (tonnes/year)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=600,
        showlegend=True
    )

    st.plotly_chart(fig, width="stretch")

    st.info(
        "Green diamonds are non-dominated scenarios. Pale circles are dominated by at least one other option."
    )

# ============================================================================
# TAB 3: LIVE HUB OPTIMIZATION
# ============================================================================
with tab3:
    st.subheader("⚡ Greedy Placement Simulator")

    st.markdown("""
    **Algorithm: Greedy Max-Coverage Hub Placement**

    This is the core optimization algorithm used in the Static Hubs scenario.
    Watch it run step-by-step!
    """)

    # Parameters
    col1, col2, col3 = st.columns(3)

    with col1:
        num_hubs = st.slider("Number of Hubs to Place", 1, 20, 5, key="num_hubs_sim")

    with col2:
        coverage_radius = st.slider("Coverage Radius (m)", 200, 1000, 500, 100, key="coverage_radius_sim")

    with col3:
        run_optimization = st.button("🚀 Run Optimization", type="primary")

    if run_optimization:
        with st.spinner("Running greedy max-coverage algorithm..."):

            # Prepare data
            estate_coords = estates[['lat', 'lon']].values
            populations = estates['population'].values

            # Convert lat/lon to approximate meters (rough approximation for HK)
            # 1 degree lat ≈ 111km, 1 degree lon ≈ 111km * cos(lat)
            lat_mean = np.mean(estate_coords[:, 0])
            coords_m = estate_coords.copy()
            coords_m[:, 0] = coords_m[:, 0] * 111000  # lat to meters
            coords_m[:, 1] = coords_m[:, 1] * 111000 * np.cos(np.radians(lat_mean))  # lon to meters

            # Greedy algorithm
            placed_hubs = []
            covered_estates = set()
            iteration_data = []

            for iteration in range(num_hubs):
                best_hub = None
                best_new_coverage = 0
                best_estates = set()

                # Try each uncovered estate as potential hub
                for idx in range(len(estates)):
                    if idx in [h['idx'] for h in placed_hubs]:
                        continue

                    # Calculate distances from this candidate hub to all estates
                    hub_coord = coords_m[idx].reshape(1, -1)
                    distances = cdist(hub_coord, coords_m, metric='euclidean')[0]

                    # Find newly covered estates
                    newly_covered = set()
                    new_population = 0

                    for estate_idx in range(len(estates)):
                        if estate_idx not in covered_estates and distances[estate_idx] <= coverage_radius:
                            newly_covered.add(estate_idx)
                            new_population += populations[estate_idx]

                    if new_population > best_new_coverage:
                        best_new_coverage = new_population
                        best_hub = idx
                        best_estates = newly_covered

                # Place best hub
                if best_hub is not None:
                    placed_hubs.append({
                        'idx': best_hub,
                        'estate': estates.iloc[best_hub]['estate'],
                        'lat': estates.iloc[best_hub]['lat'],
                        'lon': estates.iloc[best_hub]['lon'],
                        'new_population': best_new_coverage,
                        'iteration': iteration + 1
                    })
                    covered_estates.update(best_estates)

                    iteration_data.append({
                        'Iteration': iteration + 1,
                        'Hub Placed': estates.iloc[best_hub]['estate'],
                        'New Population Covered': int(best_new_coverage),
                        'Total Population Covered': int(sum(populations[list(covered_estates)])),
                        'Coverage %': round(sum(populations[list(covered_estates)]) / populations.sum() * 100, 1)
                    })

            st.session_state.optimization_results = {
                "hubs": placed_hubs,
                "iterations": iteration_data,
                "covered_estates": covered_estates,
                "params": {
                    "num_hubs": num_hubs,
                    "coverage_radius": coverage_radius,
                },
            }

    if st.session_state.get("optimization_results"):
        results = st.session_state.optimization_results
        run_num_hubs = int(results.get("params", {}).get("num_hubs", num_hubs))
        run_radius = int(results.get("params", {}).get("coverage_radius", coverage_radius))

        if run_num_hubs != num_hubs or run_radius != coverage_radius:
            st.info(
                "Showing previous run results. Click **Run Optimization** to recompute "
                "with current slider values."
            )

        # Show iteration table
        st.markdown("### 📋 Optimization Steps")
        iteration_df = pd.DataFrame(results['iterations'])
        st.dataframe(iteration_df, width="stretch", hide_index=True)

        # Show convergence chart
        st.markdown("### 📈 Coverage Convergence")

        fig_conv = go.Figure()

        fig_conv.add_trace(go.Scatter(
            x=iteration_df['Iteration'],
            y=iteration_df['Coverage %'],
            mode='lines+markers',
            name='Coverage %',
            line=dict(color='#2E7D32', width=3),
            marker=dict(size=10, color='#2E7D32')
        ))

        fig_conv.update_layout(
            xaxis_title="Hub Placement Iteration",
            yaxis_title="Population Coverage (%)",
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig_conv, width="stretch")

        # Show map with placed hubs
        st.markdown("### 🗺️ Optimized Hub Placement")

        m_opt = folium.Map(
            location=[22.3193, 114.1694],
            zoom_start=11,
            tiles="CartoDB positron"
        )

        # Add all estates
        for idx in range(len(estates)):
            row = estates.iloc[idx]
            if idx in results['covered_estates']:
                color = "#2E7D32"
                status = "Covered"
            else:
                color = "#8D6E63"
                status = "Not Covered"

            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=4,
                popup=f"<b>{row['estate']}</b><br>Status: {status}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=1
            ).add_to(m_opt)

        # Add placed hubs
        for hub in results['hubs']:
            folium.Marker(
                location=[hub['lat'], hub['lon']],
                popup=f"<b>Hub #{hub['iteration']}</b><br>{hub['estate']}<br>New coverage: {hub['new_population']:,}",
                tooltip=f"Hub #{hub['iteration']}",
                icon=folium.Icon(color="green", icon="star", prefix="fa")
            ).add_to(m_opt)

            # Draw coverage circle
            folium.Circle(
                location=[hub['lat'], hub['lon']],
                radius=run_radius,
                color='#2E7D32',
                fill=True,
                fillOpacity=0.15,
                weight=2
            ).add_to(m_opt)

        st_folium(m_opt, width=1400, height=600, key="optimization_map")

        # Summary
        final_coverage = iteration_df.iloc[-1]['Coverage %']
        total_covered = iteration_df.iloc[-1]['Total Population Covered']

        st.success(f"""
        **Optimization Complete!**

        - **{run_num_hubs} hubs placed** using greedy max-coverage algorithm
        - **{final_coverage}%** of population now within {run_radius}m
        - **{total_covered:,}** residents covered
        - **Algorithm complexity:** O(n² × k) where n = estates, k = hubs
        """)
    else:
        st.info("Set parameters and click **Run Optimization** to simulate hub placement.")

# ============================================================================
# TAB 4: METRICS DASHBOARD
# ============================================================================
with tab4:
    st.subheader("📊 Comprehensive Metrics Dashboard")

    # All scenarios comparison
    all_scenarios_data = []
    for key in ["baseline", "mobile_first", "hybrid_equity", "static_hubs"]:
        s = scenarios[key]
        all_scenarios_data.append({
            "Scenario": s["name"],
            "Burden %": s["textile_burden_pct"],
            "Estates >500m": s["estates_over_500m"],
            "Diversion (t/y)": s["annual_diversion_tonnes"],
            "Cost (HK$M)": s["total_cost_hkd"] / 1e6,
            "Payback (y)": s["payback_years"] if s["payback_years"] else 0,
            "Gini": s["district_gini"],
            "Beneficiaries": s["beneficiary_estates"]
        })

    df_all = pd.DataFrame(all_scenarios_data)

    # Radar chart
    st.markdown("### 🎯 Multi-Dimensional Comparison (Radar Chart)")

    # Normalize metrics for radar chart (0-1 scale, higher is better)
    df_radar = df_all.copy()
    df_radar['Equity Score'] = 100 - df_radar['Burden %']  # Invert burden
    df_radar['Impact Score'] = df_radar['Diversion (t/y)'] / df_radar['Diversion (t/y)'].max() * 100
    df_radar['Cost Efficiency'] = (1 - df_radar['Cost (HK$M)'] / df_radar['Cost (HK$M)'].max()) * 100
    df_radar['Fairness Score'] = (1 - df_radar['Gini']) * 100

    fig_radar = go.Figure()

    for idx, row in df_radar.iterrows():
        if row['Scenario'] != "Baseline (Current)":  # Skip baseline for clarity
            fig_radar.add_trace(go.Scatterpolar(
                r=[row['Equity Score'], row['Impact Score'],
                   row['Cost Efficiency'], row['Fairness Score']],
                theta=['Equity', 'Impact', 'Cost Efficiency', 'Fairness'],
                fill='toself',
                name=row['Scenario']
            ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500
    )

    st.plotly_chart(fig_radar, width="stretch")

    # Summary table
    st.markdown("### 📋 Complete Metrics Table")
    st.dataframe(df_all, width="stretch", hide_index=True)

st.markdown("---")
st.info(
    "Measured baseline/static outputs are shown alongside modeled mobile/hybrid scenarios to make policy tradeoffs explicit."
)

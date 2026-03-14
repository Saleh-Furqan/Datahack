#!/usr/bin/env python3
"""
Interactive Map - Clickable estates and hubs on Hong Kong geography
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from pathlib import Path
import json

try:
    from control_tower.backend.theme import apply_theme
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from backend.theme import apply_theme

# Page config
st.set_page_config(
    page_title="Interactive Map - Green Loop",
    page_icon="🗺️",
    layout="wide"
)
apply_theme()

# Paths
ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data" / "processed"
CT_DATA = Path(__file__).parent.parent / "data"
ASSETS_DIR = Path(__file__).parent.parent / "assets"

# Load data
@st.cache_data
def load_estates():
    return pd.read_csv(DATA_DIR / "estates_full_analysis.csv")

@st.cache_data
def load_hubs():
    return pd.read_csv(DATA_DIR / "optimized_hubs.csv")

@st.cache_data
def load_scenario_data():
    with open(CT_DATA / "scenario_outputs.json") as f:
        return json.load(f)


@st.cache_data
def load_district_geojson():
    geo_path = ASSETS_DIR / "hk_districts.geojson"
    if not geo_path.exists():
        return None
    with open(geo_path) as f:
        return json.load(f)

estates = load_estates()
hubs = load_hubs()
scenario_data = load_scenario_data()
district_geojson = load_district_geojson()

# Header
st.title("🗺️ Hong Kong Green Loop Coverage Map")
st.markdown("**Interactive estate-level view of textile recycling access**")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Scenario selector
scenario_options = {
    "baseline": "Baseline (Current State)",
    "static_hubs": "Static Hubs (Optimized)",
    "mobile_first": "Mobile-First Scenario",
    "hybrid_equity": "Hybrid Equity Scenario"
}

selected_scenario = st.sidebar.selectbox(
    "Select Scenario",
    options=list(scenario_options.keys()),
    format_func=lambda x: scenario_options[x],
    index=1  # Default to static_hubs
)

# District filter
all_districts = sorted(estates["district"].unique())
selected_districts = st.sidebar.multiselect(
    "Filter by District",
    options=all_districts,
    default=all_districts
)

# Distance threshold filter
max_distance = st.sidebar.slider(
    "Max Distance (m)",
    min_value=0,
    max_value=int(estates["dist_textiles"].max()),
    value=1000,
    step=100
)

# Show hubs toggle
show_hubs = st.sidebar.checkbox("Show Hub Locations", value=True)

# Cluster markers toggle
use_clustering = st.sidebar.checkbox("Cluster Markers", value=True)

st.sidebar.markdown("---")
st.sidebar.success("""
**Color Legend:**
- Dark Green: <300m (Well-served)
- Light Green: 300-500m (Moderate)
- Olive/Gold: 500-800m (Underserved)
- Brown: >800m (Critical)
""")

# Build scenario-specific estate view first, then filter.
scenario_info = scenario_data["scenarios"][selected_scenario]
estates_view = estates.copy()
if "estate_distances_m" in scenario_info and scenario_info["estate_distances_m"]:
    distances = np.asarray(scenario_info["estate_distances_m"], dtype=float)
    if len(distances) == len(estates_view):
        estates_view["display_distance"] = distances[estates_view.index]
    else:
        st.warning(
            f"Scenario distance array length mismatch ({len(distances)} vs {len(estates_view)}). "
            "Falling back to baseline distances."
        )
        estates_view["display_distance"] = estates_view["dist_textiles"]
else:
    estates_view["display_distance"] = estates_view["dist_textiles"]

estates_view["display_distance"] = estates_view["display_distance"].fillna(estates_view["dist_textiles"])

filtered_estates = estates_view[
    (estates_view["district"].isin(selected_districts))
    & (estates_view["display_distance"] <= max_distance)
].copy()

# Define color function with sustainability theme
def get_color(distance):
    """Return color based on distance to nearest hub."""
    if distance < 300:
        return "#2E7D32"  # Dark Green (well-served)
    elif distance < 500:
        return "#7CB342"  # Light Green (moderate)
    elif distance < 800:
        return "#C0A04C"  # Olive/Gold (underserved)
    else:
        return "#8D6E63"  # Brown (critical)

def get_status(distance):
    """Return status label based on distance."""
    if distance < 300:
        return "Well-served"
    elif distance < 500:
        return "Moderate"
    elif distance < 800:
        return "Underserved"
    else:
        return "Critical"

# Create base map centered on Hong Kong
m = folium.Map(
    location=[22.3193, 114.1694],
    zoom_start=11,
    tiles="CartoDB positron",
    attr="Map tiles by CartoDB, under CC BY 3.0"
)

if district_geojson is not None:
    folium.GeoJson(
        district_geojson,
        name="District Boundaries",
        style_function=lambda _feature: {
            "fillColor": "#00000000",
            "color": "#5D6F63",
            "weight": 1.2,
            "fillOpacity": 0,
        },
    ).add_to(m)

# Add estates
if use_clustering:
    marker_cluster = MarkerCluster(
        name="Estates",
        overlay=True,
        control=True
    ).add_to(m)
    marker_group = marker_cluster
else:
    marker_group = m

for idx, row in filtered_estates.iterrows():
    distance = row["display_distance"]
    color = get_color(distance)
    status = get_status(distance)

    # Create popup HTML
    popup_html = f"""
    <div style="width: 200px">
        <h4 style="margin: 0 0 8px 0;">{row['estate']}</h4>
        <p style="margin: 4px 0;"><b>District:</b> {row['district']}</p>
        <p style="margin: 4px 0;"><b>Population:</b> {int(row['population']):,}</p>
        <p style="margin: 4px 0;"><b>Distance:</b> {int(distance)}m</p>
        <p style="margin: 4px 0;"><b>Status:</b> <span style="color: {color};">{status}</span></p>
    </div>
    """

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=6,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=row["estate"],
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.7,
        weight=2
    ).add_to(marker_group)

# Add hubs if enabled and scenario has hubs
if show_hubs and scenario_info.get("interventions", {}).get("new_hubs", 0) > 0:
    hub_group = folium.FeatureGroup(name="Hubs", overlay=True, control=True)
    max_hubs = int(scenario_info["interventions"].get("new_hubs", 0))

    for idx, row in hubs.iterrows():
        if row["hub_rank"] <= max_hubs:
            popup_html = f"""
            <div style="width: 200px">
                <h4 style="margin: 0 0 8px 0;">🏢 Hub #{int(row['hub_rank'])}</h4>
                <p style="margin: 4px 0;"><b>Location:</b> {row['estate']}</p>
                <p style="margin: 4px 0;"><b>District:</b> {row['district']}</p>
                <p style="margin: 4px 0;"><b>New Coverage:</b> {int(row['new_population_covered']):,} people</p>
            </div>
            """

            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Hub #{int(row['hub_rank'])}",
                icon=folium.Icon(color="green", icon="recycle", prefix="fa")
            ).add_to(hub_group)

    hub_group.add_to(m)

# Add legend with sustainability-themed colors
legend_html = '''
<div style="position: fixed;
     bottom: 50px; left: 50px;
     width: 230px;
     z-index: 9999;
     background-color: rgba(255, 255, 255, 0.98);
     padding: 16px 18px;
     border-radius: 10px;
     border: 2px solid #2E7D32;
     box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);">
    <p style="margin: 0 0 12px 0; font-weight: bold; font-size: 15px; color: #1B5E20; border-bottom: 2px solid #A5D6A7; padding-bottom: 8px;">Coverage Level</p>
    <p style="margin: 6px 0; color: #2E7D32; font-size: 13px;"><span style="color: #2E7D32; font-size: 18px;">●</span> Well-served (&lt;300m)</p>
    <p style="margin: 6px 0; color: #558B2F; font-size: 13px;"><span style="color: #7CB342; font-size: 18px;">●</span> Moderate (300-500m)</p>
    <p style="margin: 6px 0; color: #827717; font-size: 13px;"><span style="color: #C0A04C; font-size: 18px;">●</span> Underserved (500-800m)</p>
    <p style="margin: 6px 0; color: #5D4037; font-size: 13px;"><span style="color: #8D6E63; font-size: 18px;">●</span> Critical (&gt;800m)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add layer control
folium.LayerControl().add_to(m)

# Display stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Estates Shown",
        f"{len(filtered_estates):,}",
        help="Number of estates matching current filters"
    )

with col2:
    well_served = len(filtered_estates[filtered_estates["display_distance"] < 300])
    st.metric(
        "Well-Served",
        f"{well_served}",
        help="Estates within 300m of recycling point"
    )

with col3:
    underserved = len(filtered_estates[filtered_estates["display_distance"] > 500])
    st.metric(
        "Underserved",
        f"{underserved}",
        help="Estates more than 500m from recycling point"
    )

with col4:
    avg_distance = filtered_estates["display_distance"].mean() if not filtered_estates.empty else float("nan")
    st.metric(
        "Avg Distance",
        f"{int(avg_distance)}m" if np.isfinite(avg_distance) else "N/A",
        help="Average distance to nearest hub"
    )

st.markdown("---")

# Render map
st.markdown("**Click on any estate or hub for details**")

# Fix map flickering by using session state key
if "map_key" not in st.session_state:
    st.session_state.map_key = 0

map_data = st_folium(
    m,
    width=1400,
    height=650,
    returned_objects=["last_object_clicked", "last_clicked", "zoom", "bounds"],
    key=f"map_{st.session_state.map_key}"  # Stable key prevents re-rendering
)

# Handle map clicks
if map_data and map_data.get("last_object_clicked"):
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Last Clicked")
    st.sidebar.json(map_data["last_object_clicked"])

# Estate spotlight
st.markdown("---")
st.subheader("🔦 Estate Spotlight")

if filtered_estates.empty:
    st.warning("No estates match the current filters. Expand district selection or increase max distance.")
else:
    selected_estate_name = st.selectbox(
        "Select an estate to view details",
        options=filtered_estates["estate"].tolist(),
        index=0
    )

    estate_info = filtered_estates[filtered_estates["estate"] == selected_estate_name].iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Estate:** {estate_info['estate']}")
        st.markdown(f"**District:** {estate_info['district']}")
        st.markdown(f"**Population:** {int(estate_info['population']):,}")

    with col2:
        st.markdown(f"**Distance to Hub:** {int(estate_info['display_distance'])}m")
        st.markdown(f"**Status:** {get_status(estate_info['display_distance'])}")
        st.markdown(f"**Coordinates:** {estate_info['lat']:.4f}, {estate_info['lon']:.4f}")

    with col3:
        if "district_vulnerability" in estate_info:
            st.markdown(f"**Vulnerability Index:** {estate_info['district_vulnerability']:.2f}")
        st.markdown(f"**Baseline Distance:** {int(estate_info['dist_textiles'])}m")

        improvement = estate_info['dist_textiles'] - estate_info['display_distance']
        if improvement > 0:
            st.markdown(f"**Improvement:** -{int(improvement)}m")

# Top beneficiaries
if selected_scenario != "baseline" and scenario_info.get("top_beneficiaries"):
    st.markdown("---")
    st.subheader("🏆 Top Beneficiary Estates")
    st.markdown(f"**Estates that benefit most from {scenario_options[selected_scenario]}**")

    beneficiaries_df = pd.DataFrame(scenario_info["top_beneficiaries"])
    beneficiaries_df = beneficiaries_df.rename(columns={
        "estate": "Estate",
        "district": "District",
        "population": "Population",
        "before_m": "Before (m)",
        "after_m": "After (m)",
        "reduction_m": "Reduction (m)",
        "newly_served": "Newly Served?"
    })

    st.dataframe(
        beneficiaries_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Newly Served?": st.column_config.CheckboxColumn("Newly Served?")
        }
    )

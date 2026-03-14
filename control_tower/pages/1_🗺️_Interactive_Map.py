#!/usr/bin/env python3
"""Interactive Hong Kong map with estates, hubs, and stream layers."""

from __future__ import annotations

import numpy as np
import streamlit as st
import folium
from folium.plugins import Fullscreen, MarkerCluster, MiniMap
from streamlit_folium import st_folium

try:
    from control_tower.backend.data_loader import (
        STREAM_FILTERS,
        load_collection_points,
        load_district_geojson,
        load_estates,
        load_hubs,
        load_optional_points_csv,
        load_scenario_outputs,
        stream_points,
    )
    from control_tower.backend.theme import apply_theme
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from backend.data_loader import (  # type: ignore
        STREAM_FILTERS,
        load_collection_points,
        load_district_geojson,
        load_estates,
        load_hubs,
        load_optional_points_csv,
        load_scenario_outputs,
        stream_points,
    )
    from backend.theme import apply_theme  # type: ignore


st.set_page_config(page_title="Interactive Map - Green Loop", page_icon="🗺️", layout="wide")
apply_theme()


@st.cache_data
def get_inputs():
    return (
        load_estates(),
        load_hubs(),
        load_scenario_outputs(),
        load_district_geojson(),
        load_collection_points(public_only=True),
        load_optional_points_csv("recycling_stations.csv"),
        load_optional_points_csv("waste_management_facilities.csv"),
    )


(
    estates,
    hubs,
    scenario_data,
    district_geojson,
    public_points,
    optional_recycling_stations,
    optional_waste_facilities,
) = get_inputs()
scenarios = scenario_data["scenarios"]

STREAM_LABELS = {
    "glass": "Glass",
    "textiles": "Textiles",
    "hazardous": "Hazardous",
    "batteries": "Batteries",
    "ewaste": "E-waste",
}
STREAM_COLORS = {
    "glass": "#2B8CBE",
    "textiles": "#B35806",
    "hazardous": "#E34A33",
    "batteries": "#6A51A3",
    "ewaste": "#2CA25F",
}


def distance_color(distance_m: float) -> str:
    if distance_m < 300:
        return "#1B9E77"
    if distance_m < 500:
        return "#66A61E"
    if distance_m < 800:
        return "#E6AB02"
    return "#D95F02"


def distance_label(distance_m: float) -> str:
    if distance_m < 300:
        return "Well-served (<300m)"
    if distance_m < 500:
        return "Moderate (300-500m)"
    if distance_m < 800:
        return "Underserved (500-800m)"
    return "Critical (>800m)"


def infer_lat_lon_columns(df):
    lat_candidates = ["lat", "latitude", "y", "northing"]
    lon_candidates = ["lon", "lgt", "lng", "longitude", "x", "easting"]
    lat_col = next((c for c in lat_candidates if c in df.columns), None)
    lon_col = next((c for c in lon_candidates if c in df.columns), None)
    return lat_col, lon_col


st.markdown(
    """
<div class="gl-hero">
  <p class="gl-eyebrow">Interactive Geo Layer</p>
  <h2>Hong Kong Estate + Stream Access Map</h2>
  <p>Click estates and hubs, switch scenarios, and overlay public collection points by waste stream.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.header("Map Controls")
scenario_options = {
    "baseline": "Baseline (Current)",
    "static_hubs": "Static Hubs",
    "mobile_first": "Mobile-First",
    "hybrid_equity": "Hybrid Equity",
}
selected_scenario = st.sidebar.selectbox(
    "Scenario",
    options=list(scenario_options.keys()),
    format_func=lambda x: scenario_options[x],
    index=1,
)

all_districts = sorted(estates["district"].dropna().unique().tolist())
selected_districts = st.sidebar.multiselect("Districts", all_districts, default=all_districts)

distance_cap = int(np.nanmax(estates["dist_textiles"].to_numpy(dtype=float)))
max_distance = st.sidebar.slider("Max Distance Filter (m)", min_value=200, max_value=distance_cap, value=1800, step=100)

st.sidebar.markdown("---")
show_estates = st.sidebar.checkbox("Show Estates", value=True)
show_hubs = st.sidebar.checkbox("Show Proposed Hubs", value=True)
show_hub_rings = st.sidebar.checkbox("Show Hub 800m Rings", value=True)
show_boundaries = st.sidebar.checkbox("Show District Boundaries", value=district_geojson is not None, disabled=district_geojson is None)

st.sidebar.markdown("---")
show_stream_layers = st.sidebar.checkbox("Show Public Stream Layers", value=True)
selected_streams = st.sidebar.multiselect(
    "Waste Streams (public points)",
    options=list(STREAM_FILTERS.keys()),
    default=["textiles", "glass"],
    format_func=lambda x: STREAM_LABELS[x],
)
max_points_per_stream = st.sidebar.slider("Max points per stream", min_value=300, max_value=5000, value=1800, step=100)
cluster_stream_points = st.sidebar.checkbox("Cluster stream points", value=True)

show_premium_points = st.sidebar.checkbox("Show Premium Recycling Stations Layer", value=True)
show_waste_facilities = st.sidebar.checkbox("Show Waste Facilities Layer", value=True)

scenario_info = scenarios[selected_scenario]
estates_view = estates.copy()
scenario_dist = scenario_info.get("estate_distances_m") or []
if len(scenario_dist) == len(estates_view):
    estates_view["display_distance"] = np.asarray(scenario_dist, dtype=float)
else:
    estates_view["display_distance"] = estates_view["dist_textiles"]
estates_view["baseline_distance"] = estates_view["dist_textiles"]
estates_view["distance_reduction"] = np.maximum(
    estates_view["baseline_distance"] - estates_view["display_distance"], 0
)

filtered = estates_view[
    estates_view["district"].isin(selected_districts) & (estates_view["display_distance"] <= max_distance)
].copy()

m = folium.Map(
    location=[22.3193, 114.1694],
    zoom_start=11,
    tiles="CartoDB Positron",
    control_scale=True,
    prefer_canvas=True,
)
Fullscreen(position="topright").add_to(m)
MiniMap(toggle_display=True, position="bottomright").add_to(m)

if show_boundaries and district_geojson is not None:
    folium.GeoJson(
        district_geojson,
        name="District Boundaries",
        style_function=lambda _f: {
            "fillColor": "#00000000",
            "color": "#517167",
            "weight": 1.2,
            "fillOpacity": 0,
        },
    ).add_to(m)

if show_estates:
    estate_group = folium.FeatureGroup(name=f"Estates ({len(filtered):,})", show=True)
    for row in filtered.itertuples():
        color = distance_color(float(row.display_distance))
        label = distance_label(float(row.display_distance))
        popup_html = (
            f"<b>{row.estate}</b><br>"
            f"District: {row.district}<br>"
            f"Population: {int(row.population):,}<br>"
            f"Scenario distance: {int(row.display_distance)}m<br>"
            f"Baseline distance: {int(row.baseline_distance)}m<br>"
            f"Improvement: {int(row.distance_reduction)}m<br>"
            f"Status: {label}"
        )
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=5.6,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{row.estate} ({int(row.display_distance)}m)",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.78,
            weight=1.2,
        ).add_to(estate_group)
    estate_group.add_to(m)

if show_hubs and scenario_info.get("interventions", {}).get("new_hubs", 0) > 0:
    hub_group = folium.FeatureGroup(name="Proposed Hubs", show=True)
    ring_group = folium.FeatureGroup(name="Hub Service Rings (800m)", show=show_hub_rings)
    hub_limit = int(scenario_info["interventions"].get("new_hubs", 0))

    for row in hubs[hubs["hub_rank"] <= hub_limit].itertuples():
        popup_html = (
            f"<b>Hub #{int(row.hub_rank)}: {row.estate}</b><br>"
            f"District: {row.district}<br>"
            f"New population covered: {int(row.new_population_covered):,}"
        )
        folium.Marker(
            location=[row.lat, row.lon],
            tooltip=f"Hub #{int(row.hub_rank)}",
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="green", icon="recycle", prefix="fa"),
        ).add_to(hub_group)

        if show_hub_rings:
            folium.Circle(
                location=[row.lat, row.lon],
                radius=800,
                color="#1F6F52",
                weight=1.5,
                fill=True,
                fill_color="#8EC8AE",
                fill_opacity=0.08,
            ).add_to(ring_group)

    hub_group.add_to(m)
    if show_hub_rings:
        ring_group.add_to(m)

if show_premium_points:
    premium = public_points[
        public_points["legend"].fillna("").str.contains("Recycling Stations/Recycling Stores", case=False, na=False)
    ].copy()
    if not premium.empty:
        premium_group = folium.FeatureGroup(name=f"Premium Recycling Stations ({len(premium):,})", show=False)
        for row in premium.itertuples():
            popup_html = f"<b>Premium Recycling Station</b><br>{(row.address_en or '')[:120]}"
            folium.CircleMarker(
                location=[row.lat, row.lon],
                radius=4.5,
                color="#2F5597",
                fill=True,
                fill_color="#2F5597",
                fill_opacity=0.8,
                weight=1,
                popup=folium.Popup(popup_html, max_width=260),
            ).add_to(premium_group)
        premium_group.add_to(m)

if show_premium_points and optional_recycling_stations is not None and not optional_recycling_stations.empty:
    rs_lat, rs_lon = infer_lat_lon_columns(optional_recycling_stations)
    if rs_lat and rs_lon:
        stations_group = folium.FeatureGroup(name="GREEN@ / Recycling Stations (external file)", show=False)
        for row in optional_recycling_stations.dropna(subset=[rs_lat, rs_lon]).itertuples():
            lat = float(getattr(row, rs_lat))
            lon = float(getattr(row, rs_lon))
            popup_html = "<b>Recycling Station</b>"
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="blue", icon="info-sign"),
                popup=popup_html,
            ).add_to(stations_group)
        stations_group.add_to(m)

if show_waste_facilities and optional_waste_facilities is not None and not optional_waste_facilities.empty:
    wf_lat, wf_lon = infer_lat_lon_columns(optional_waste_facilities)
    if wf_lat and wf_lon:
        facilities_group = folium.FeatureGroup(name="Waste Management Facilities (external file)", show=False)
        for row in optional_waste_facilities.dropna(subset=[wf_lat, wf_lon]).itertuples():
            lat = float(getattr(row, wf_lat))
            lon = float(getattr(row, wf_lon))
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="darkred", icon="industry", prefix="fa"),
                popup="<b>Waste Facility</b>",
            ).add_to(facilities_group)
        facilities_group.add_to(m)

stream_counts_note = []
if show_stream_layers and selected_streams:
    for stream in selected_streams:
        pts = stream_points(public_points, stream)
        total_count = len(pts)
        if total_count > max_points_per_stream:
            pts = pts.sample(n=max_points_per_stream, random_state=42)
            stream_counts_note.append(f"{STREAM_LABELS[stream]}: {max_points_per_stream:,}/{total_count:,} shown")
        else:
            stream_counts_note.append(f"{STREAM_LABELS[stream]}: {total_count:,} shown")

        group = folium.FeatureGroup(name=f"Public {STREAM_LABELS[stream]} Points", show=(stream == "textiles"))
        target = MarkerCluster(disableClusteringAtZoom=14).add_to(group) if cluster_stream_points else group

        for row in pts.itertuples():
            address = (row.address_en if isinstance(row.address_en, str) else "").strip()
            popup_html = (
                f"<b>{STREAM_LABELS[stream]} Collection Point</b><br>"
                f"Type: {row.legend}<br>"
                f"{address[:120]}"
            )
            folium.CircleMarker(
                location=[row.lat, row.lon],
                radius=3.2,
                color=STREAM_COLORS[stream],
                fill=True,
                fill_color=STREAM_COLORS[stream],
                fill_opacity=0.72,
                weight=1,
                popup=folium.Popup(popup_html, max_width=260),
            ).add_to(target)

        group.add_to(m)

legend_html = f"""
<div style="
    position: fixed; bottom: 32px; left: 20px; z-index: 9999;
    background: rgba(255,255,255,0.97); border: 1px solid #d6e3dc;
    border-radius: 12px; padding: 12px 14px; min-width: 230px;
    box-shadow: 0 8px 24px rgba(20,38,28,0.14); font-size: 13px;">
  <div style="font-weight: 700; color:#1f6f52; margin-bottom:8px;">Estate Accessibility</div>
  <div><span style="color:#1B9E77;">●</span> Well-served (&lt;300m)</div>
  <div><span style="color:#66A61E;">●</span> Moderate (300-500m)</div>
  <div><span style="color:#E6AB02;">●</span> Underserved (500-800m)</div>
  <div><span style="color:#D95F02;">●</span> Critical (&gt;800m)</div>
  <hr style="margin:8px 0;">
  <div style="font-weight: 700; color:#1f6f52; margin-bottom:4px;">Public Stream Layers</div>
  <div><span style="color:{STREAM_COLORS['glass']};">●</span> Glass</div>
  <div><span style="color:{STREAM_COLORS['textiles']};">●</span> Textiles</div>
  <div><span style="color:{STREAM_COLORS['hazardous']};">●</span> Hazardous</div>
  <div><span style="color:{STREAM_COLORS['batteries']};">●</span> Batteries</div>
  <div><span style="color:{STREAM_COLORS['ewaste']};">●</span> E-waste</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl(collapsed=False).add_to(m)

stats_1, stats_2, stats_3, stats_4 = st.columns(4)
with stats_1:
    st.metric("Estates shown", f"{len(filtered):,}")
with stats_2:
    st.metric("Underserved (>500m)", f"{int((filtered['display_distance'] > 500).sum()):,}")
with stats_3:
    st.metric("Mean distance", f"{int(filtered['display_distance'].mean()):,}m" if not filtered.empty else "N/A")
with stats_4:
    hubs_count = int(scenario_info.get("interventions", {}).get("new_hubs", 0))
    st.metric("Hubs in scenario", str(hubs_count))

if stream_counts_note:
    st.caption(" | ".join(stream_counts_note))
if optional_recycling_stations is None or optional_waste_facilities is None:
    st.caption(
        "Optional layers can be enabled by adding `data/raw/recycling_stations.csv` and/or "
        "`data/raw/waste_management_facilities.csv` with latitude/longitude columns."
    )

st.markdown("#### Interactive Map")
map_data = st_folium(
    m,
    width=1400,
    height=700,
    returned_objects=["last_object_clicked"],
)

if map_data.get("last_object_clicked"):
    click = map_data["last_object_clicked"]
    if isinstance(click, dict) and "lat" in click and "lng" in click:
        st.caption(f"Last click: {click['lat']:.5f}, {click['lng']:.5f}")

st.markdown("---")
st.subheader("Priority Estates Still Beyond 500m")
remaining = filtered[filtered["display_distance"] > 500].copy()
if remaining.empty:
    st.success("No estates in the current filter are above 500m.")
else:
    remaining["distance_m"] = remaining["display_distance"].round(1)
    show = remaining.sort_values("distance_m", ascending=False)[
        ["estate", "district", "population", "distance_m", "distance_reduction"]
    ].head(20)
    st.dataframe(
        show,
        hide_index=True,
        width="stretch",
        column_config={
            "population": st.column_config.NumberColumn("Population", format="%d"),
            "distance_m": st.column_config.NumberColumn("Distance (m)", format="%.1f"),
            "distance_reduction": st.column_config.NumberColumn("Improvement (m)", format="%.1f"),
        },
    )

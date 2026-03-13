#!/usr/bin/env python3
"""
The Open-Access Gap Analysis
Comparing nominal coverage vs publicly-usable coverage
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import folium
from math import radians, cos, sin, asin, sqrt
import json
from pathlib import Path

Path('visualizations').mkdir(exist_ok=True)
Path('data/processed').mkdir(exist_ok=True)

print("="*70)
print("DATAHACK 2026: The Open-Access Gap Analysis")
print("Nominal Coverage vs Publicly-Usable Coverage")
print("="*70)

# Load data
print("\n[1/6] Loading data...")
df_cp = pd.read_csv('data/raw/collection_points.csv', encoding='utf-8-sig')

# Categorize by access type
df_cp['is_public'] = df_cp['accessibilty_notes'].str.contains('For public use', na=False)
df_public = df_cp[df_cp['is_public']]
df_restricted = df_cp[~df_cp['is_public']]

print(f"  Total collection points: {len(df_cp):,}")
print(f"  Public-access points: {len(df_public):,} ({len(df_public)/len(df_cp)*100:.1f}%)")
print(f"  Restricted points: {len(df_restricted):,} ({len(df_restricted)/len(df_cp)*100:.1f}%)")

# Load estates
with open('data/raw/public_housing.json') as f:
    ph = json.load(f)

estates = []
for e in ph:
    try:
        flats = int(e['No. of Rental Flats']['en'].split('as at')[0].replace(' ','').replace(',',''))
    except:
        flats = None
    estates.append({
        'name': e['Estate Name']['en'],
        'district': e['District Name']['en'],
        'lat': e['Estate Map Latitude'],
        'lon': e['Estate Map Longitude'],
        'flats': flats,
        'pop': int(flats*2.7) if flats else None
    })

df_est = pd.DataFrame(estates)
print(f"  Public housing estates: {len(df_est)}")
print(f"  Total population: {df_est['pop'].sum():,}")

# Distance calculation
print("\n[2/6] Calculating distances (2 scenarios)...")
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 2*asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))*6371000

# Scenario 1: All collection points
dist_all = []
for _, est in df_est.iterrows():
    dists = df_cp.apply(lambda cp: haversine(est['lat'], est['lon'], cp['lat'], cp['lgt']), axis=1)
    dist_all.append(dists.min())
df_est['dist_all'] = dist_all

# Scenario 2: Public-access only
dist_public = []
for _, est in df_est.iterrows():
    if len(df_public) > 0:
        dists = df_public.apply(lambda cp: haversine(est['lat'], est['lon'], cp['lat'], cp['lgt']), axis=1)
        dist_public.append(dists.min())
    else:
        dist_public.append(float('inf'))
df_est['dist_public'] = dist_public

# Calculate "Openness Penalty"
df_est['openness_penalty'] = df_est['dist_public'] - df_est['dist_all']

print("  Done")

# Categorize
print("\n[3/6] Computing accessibility metrics...")
def categorize(d):
    return 'Well' if d<300 else ('Mod' if d<500 else 'Under')

df_est['category_all'] = df_est['dist_all'].apply(categorize)
df_est['category_public'] = df_est['dist_public'].apply(categorize)

# Key statistics
total_pop = df_est['pop'].sum()

# Scenario 1: All points
well_all = df_est[df_est['category_all'] == 'Well']['pop'].sum()
mod_all = df_est[df_est['category_all'] == 'Mod']['pop'].sum()
under_all = df_est[df_est['category_all'] == 'Under']['pop'].sum()

# Scenario 2: Public only
well_pub = df_est[df_est['category_public'] == 'Well']['pop'].sum()
mod_pub = df_est[df_est['category_public'] == 'Mod']['pop'].sum()
under_pub = df_est[df_est['category_public'] == 'Under']['pop'].sum()

print("\n" + "="*70)
print("KEY FINDINGS: The Open-Access Gap")
print("="*70)

print("\nSCENARIO 1: All Collection Points (Nominal Coverage)")
print(f"  Well-served (<300m): {well_all:,} residents ({well_all/total_pop*100:.1f}%)")
print(f"  Moderate (300-500m): {mod_all:,} residents ({mod_all/total_pop*100:.1f}%)")
print(f"  Underserved (>500m): {under_all:,} residents ({under_all/total_pop*100:.1f}%)")
print(f"  Median distance: {df_est['dist_all'].median():.0f}m")

print("\nSCENARIO 2: Public-Access Points Only (Usable Coverage)")
print(f"  Well-served (<300m): {well_pub:,} residents ({well_pub/total_pop*100:.1f}%)")
print(f"  Moderate (300-500m): {mod_pub:,} residents ({mod_pub/total_pop*100:.1f}%)")
print(f"  Underserved (>500m): {under_pub:,} residents ({under_pub/total_pop*100:.1f}%)")
print(f"  Median distance: {df_est['dist_public'].median():.0f}m")

print("\nTHE GAP (Delta)")
gap_well = well_all - well_pub
gap_under = under_pub - under_all
median_penalty = df_est['dist_public'].median() - df_est['dist_all'].median()

print(f"  Loss of well-served residents: {gap_well:,} ({gap_well/total_pop*100:.1f}%)")
print(f"  Increase in underserved: {gap_under:,} ({gap_under/total_pop*100:.1f}%)")
print(f"  Median distance penalty: +{median_penalty:.0f}m")
print(f"  Mean openness penalty: {df_est['openness_penalty'].mean():.0f}m")

print("\n" + "="*70)
print("YOUR HOOK:")
print("="*70)
print(f'\n"Hong Kong has {len(df_cp):,} recycling collection points,')
print(f'but only {len(df_public):,} ({len(df_public)/len(df_cp)*100:.0f}%) are open to the public.')
print(f'This creates an open-access gap: {gap_well:,} residents')
print(f'({gap_well/total_pop*100:.1f}%) lose well-served status when restricted')
print('points are excluded from analysis."\n')
print("="*70)

# Top estates with highest openness penalty
print("\n[4/6] Identifying high-penalty estates...")
top_penalty = df_est.nlargest(15, 'openness_penalty')
print("\nTop 15 estates with highest Openness Penalty:")
print("-"*70)
for _, row in top_penalty.iterrows():
    print(f"  {row['name'][:35]:35} | All: {row['dist_all']:4.0f}m | Public: {row['dist_public']:4.0f}m | Penalty: +{row['openness_penalty']:4.0f}m")

# Visualizations
print("\n[5/6] Creating visualizations...")

# Comparison plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Distance distributions
axes[0,0].hist(df_est['dist_all'], bins=40, alpha=0.7, label='All points', color='blue')
axes[0,0].hist(df_est['dist_public'], bins=40, alpha=0.7, label='Public only', color='red')
axes[0,0].axvline(300, color='green', linestyle='--', linewidth=1)
axes[0,0].axvline(500, color='orange', linestyle='--', linewidth=1)
axes[0,0].set_xlabel('Distance (m)')
axes[0,0].set_ylabel('Number of Estates')
axes[0,0].set_title('Distance Distribution Comparison')
axes[0,0].legend()

# Category comparison
categories = ['Well\n(<300m)', 'Moderate\n(300-500m)', 'Under\n(>500m)']
all_counts = [well_all/1000, mod_all/1000, under_all/1000]
pub_counts = [well_pub/1000, mod_pub/1000, under_pub/1000]
x = range(len(categories))
width = 0.35
axes[0,1].bar([i-width/2 for i in x], all_counts, width, label='All points', color='blue', alpha=0.7)
axes[0,1].bar([i+width/2 for i in x], pub_counts, width, label='Public only', color='red', alpha=0.7)
axes[0,1].set_ylabel('Population (thousands)')
axes[0,1].set_title('Accessibility by Scenario')
axes[0,1].set_xticks(x)
axes[0,1].set_xticklabels(categories)
axes[0,1].legend()

# Openness Penalty distribution
axes[1,0].hist(df_est['openness_penalty'], bins=40, edgecolor='black')
axes[1,0].set_xlabel('Openness Penalty (meters)')
axes[1,0].set_ylabel('Number of Estates')
axes[1,0].set_title('Distribution of Openness Penalty')
axes[1,0].axvline(df_est['openness_penalty'].median(), color='red', linestyle='--',
                   label=f'Median: {df_est["openness_penalty"].median():.0f}m')
axes[1,0].legend()

# Top penalty estates
top10 = df_est.nlargest(10, 'openness_penalty')
axes[1,1].barh(range(len(top10)), top10['openness_penalty'])
axes[1,1].set_yticks(range(len(top10)))
axes[1,1].set_yticklabels([name[:25] for name in top10['name']])
axes[1,1].set_xlabel('Openness Penalty (m)')
axes[1,1].set_title('Top 10 Estates by Openness Penalty')
axes[1,1].invert_yaxis()

plt.tight_layout()
plt.savefig('visualizations/open_access_gap.png', dpi=300, bbox_inches='tight')
print("  Saved: visualizations/open_access_gap.png")

# Interactive map
print("  Creating comparison map...")
m = folium.Map(location=[22.35, 114.15], zoom_start=11)

# Add public points (blue)
for _, row in df_public.sample(min(500, len(df_public))).iterrows():
    folium.CircleMarker([row['lat'], row['lgt']], radius=2, color='blue',
                       fill=True, opacity=0.4, popup='Public access').add_to(m)

# Add restricted points (gray)
for _, row in df_restricted.sample(min(500, len(df_restricted))).iterrows():
    folium.CircleMarker([row['lat'], row['lgt']], radius=2, color='gray',
                       fill=True, opacity=0.3, popup='Restricted').add_to(m)

# Add estates colored by penalty
for _, row in df_est.iterrows():
    if row['openness_penalty'] > 100:
        color = 'red'
        radius = 10
    elif row['openness_penalty'] > 50:
        color = 'orange'
        radius = 8
    else:
        color = 'green'
        radius=6

    folium.CircleMarker([row['lat'], row['lon']], radius=radius, color=color,
                       fill=True, fillOpacity=0.7,
                       popup=f"<b>{row['name']}</b><br>All points: {row['dist_all']:.0f}m<br>Public only: {row['dist_public']:.0f}m<br>Penalty: +{row['openness_penalty']:.0f}m").add_to(m)

m.save('visualizations/access_gap_map.html')
print("  Saved: visualizations/access_gap_map.html")

# Save results
print("\n[6/6] Saving data...")
df_est.to_csv('data/processed/estates_access_gap.csv', index=False)

summary = {
    'total_points': len(df_cp),
    'public_points': len(df_public),
    'restricted_points': len(df_restricted),
    'public_percentage': float(len(df_public)/len(df_cp)*100),
    'total_population': int(total_pop),
    'scenario_all': {
        'median_distance': float(df_est['dist_all'].median()),
        'well_served_pop': int(well_all),
        'underserved_pop': int(under_all)
    },
    'scenario_public': {
        'median_distance': float(df_est['dist_public'].median()),
        'well_served_pop': int(well_pub),
        'underserved_pop': int(under_pub)
    },
    'the_gap': {
        'well_served_loss': int(gap_well),
        'well_served_loss_pct': float(gap_well/total_pop*100),
        'underserved_increase': int(gap_under),
        'median_distance_penalty': float(median_penalty),
        'mean_openness_penalty': float(df_est['openness_penalty'].mean())
    }
}

with open('data/processed/access_gap_stats.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)
print("\nKey metrics computed:")
print(f"  - Open-access gap: {len(df_cp) - len(df_public):,} restricted points")
print(f"  - Well-served population loss: {gap_well:,} ({gap_well/total_pop*100:.1f}%)")
print(f"  - Median distance penalty: +{median_penalty:.0f}m")
print(f"\nNext: Use these numbers for your presentation!")
print("="*70)

#!/usr/bin/env python3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
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
print("DATAHACK 2026: Initial Analysis")
print("="*70)

print("\n[1/5] Loading data...")
df_cp = pd.read_csv('data/raw/collection_points.csv', encoding='utf-8-sig')
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
print(f"  Loaded {len(df_cp):,} collection points, {len(df_est)} estates")

print("\n[2/5] Calculating distances...")
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 2*asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))*6371000

distances = []
for _, est in df_est.iterrows():
    dists = df_cp.apply(lambda cp: haversine(est['lat'], est['lon'], cp['lat'], cp['lgt']), axis=1)
    distances.append(dists.min())
df_est['dist'] = distances

print("\n[3/5] Categorizing...")
df_est['category'] = df_est['dist'].apply(lambda d: 'Well' if d<300 else ('Mod' if d<500 else 'Under'))

total_pop = df_est['pop'].sum()
under_pop = df_est[df_est['category']=='Under']['pop'].sum()
pct = under_pop/total_pop*100

print("\n"+"="*70)
print("KEY FINDING:")
print("="*70)
print(f"\n{pct:.1f}% of public housing residents ({under_pop:,} people)")
print("live >500m from recycling collection points\n")
print("="*70)

print("\n[4/5] Creating visualizations...")
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.hist(df_est['dist'], bins=40)
plt.axvline(300, color='g', linestyle='--')
plt.axvline(500, color='r', linestyle='--')
plt.xlabel('Distance (m)')
plt.title('Distance Distribution')

plt.subplot(1,2,2)
df_est['category'].value_counts().plot(kind='bar', color=['g','orange','r'])
plt.title('Accessibility Categories')
plt.tight_layout()
plt.savefig('visualizations/analysis.png', dpi=200)
print("  Saved: visualizations/analysis.png")

m = folium.Map(location=[22.35, 114.15], zoom_start=11)
colors = {'Well':'green', 'Mod':'orange', 'Under':'red'}
for _, row in df_est.iterrows():
    folium.CircleMarker([row['lat'], row['lon']], radius=6, 
                       color=colors[row['category']], fill=True,
                       popup=f"{row['name']}<br>{row['dist']:.0f}m").add_to(m)
m.save('visualizations/map.html')
print("  Saved: visualizations/map.html")

print("\n[5/5] Saving results...")
df_est.to_csv('data/processed/estates_analyzed.csv', index=False)
with open('data/processed/stats.json', 'w') as f:
    json.dump({'underserved_pct': float(pct), 'underserved_pop': int(under_pop), 
               'total_pop': int(total_pop), 'median_dist': float(df_est['dist'].median())}, f, indent=2)

print("\n"+"="*70)
print("COMPLETE! Your hook: {:.1f}% underserved".format(pct))
print("="*70)

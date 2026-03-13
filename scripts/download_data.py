#!/usr/bin/env python3
"""
Data download script for DataHack 2026
Downloads all required datasets from data.gov.hk
"""

import os
import requests
from pathlib import Path

# Create data directory structure
data_dir = Path(__file__).parent.parent / 'data' / 'raw'
data_dir.mkdir(parents=True, exist_ok=True)

print("DataHack 2026 - Data Download Script")
print("=" * 50)

# Dataset URLs and metadata
datasets = {
    "recycling_stations": {
        "name": "Open Space Database of Recycling Stations",
        "url": "https://data.gov.hk/en-data/dataset/hk-epd-wrrteam-recycling-station",
        "priority": "CRITICAL",
        "notes": "Premium collection points - high capacity"
    },
    "collection_points": {
        "name": "Recyclable Collection Points Data",
        "url": "https://data.gov.hk/en-data/dataset/hk-epd-recycteam-waste-less-recyclable-collection-points-data",
        "priority": "CRITICAL",
        "notes": "Basic access points - street bins and small collection spots"
    },
    "public_housing": {
        "name": "Public Housing Estates Database",
        "url": "https://data.gov.hk/en-data/dataset/hk-housing-eslocator-eslocator",
        "priority": "CRITICAL",
        "notes": "Population centers - cleaner data, 45% of HK population"
    },
    "private_buildings": {
        "name": "Private Buildings Database",
        "url": "https://data.gov.hk/en-data/dataset/hk-had-json1-db-of-private-buildings-in-hong-kong",
        "priority": "IMPORTANT",
        "notes": "Additional population centers - may need geocoding"
    },
    "census_2021": {
        "name": "2021 Population Census",
        "url": "https://www.censtatd.gov.hk/en/",
        "priority": "IMPORTANT",
        "notes": "Population by district - for weighting and validation"
    },
    "waste_facilities": {
        "name": "Waste Management Facilities",
        "url": "https://data.gov.hk/en-data/dataset/hk-epd-kmuteam-epdwmf",
        "priority": "OPTIONAL",
        "notes": "Landfills, transfer stations - reference only"
    },
    "waste_historical": {
        "name": "Solid Waste Historical Data",
        "url": "https://data.gov.hk/en-datasets/search/%20Solid%20Waste",
        "priority": "OPTIONAL",
        "notes": "Recovery trends - only if estimating tonnage"
    }
}

print("\nDatasets to download:\n")
for key, info in datasets.items():
    print(f"[{info['priority']}] {info['name']}")
    print(f"  URL: {info['url']}")
    print(f"  Notes: {info['notes']}\n")

print("=" * 50)
print("\nIMPORTANT INSTRUCTIONS:")
print("=" * 50)
print("""
1. Visit each URL above in your browser
2. Look for download links (usually CSV, JSON, or Excel format)
3. Download files to: data/raw/
4. Rename files descriptively:
   - recycling_stations.csv
   - collection_points.csv
   - public_housing.csv
   - etc.

PRIORITY:
- Start with CRITICAL datasets
- Move to IMPORTANT if time permits
- Skip OPTIONAL unless ahead of schedule

DATA FREEZE CHECKPOINT:
- Set a hard deadline (Hour 6 / 6 hours from start)
- If CRITICAL datasets not ready by then:
  → PIVOT to Public Housing Only mode
  → Simplify analysis to just housing estates + recycling points

After downloading, run:
  python scripts/validate_data.py

This will check:
- Files exist and can be opened
- Coordinates are present and valid
- Data quality issues
""")

print("\n" + "=" * 50)
print("NEXT STEPS:")
print("=" * 50)
print("""
1. Download the datasets manually (cannot automate without API keys)
2. Save to data/raw/ with descriptive names
3. Run validation script: python scripts/validate_data.py
4. Proceed to data cleaning: notebooks/02_data_cleaning.ipynb
""")

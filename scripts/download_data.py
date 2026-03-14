#!/usr/bin/env python3
"""Print dataset source links and expected local paths for approach2."""

from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = [
    {
        "priority": "REQUIRED",
        "name": "Recyclable Collection Points Data",
        "url": "https://data.gov.hk/en-data/dataset/hk-epd-recycteam-waste-less-recyclable-collection-points-data",
        "save_as": "data/raw/collection_points.csv",
    },
    {
        "priority": "REQUIRED",
        "name": "Public Housing Estates Database",
        "url": "https://data.gov.hk/en-data/dataset/hk-housing-eslocator-eslocator",
        "save_as": "data/raw/public_housing.json",
    },
    {
        "priority": "OPTIONAL",
        "name": "Open Space Database of Recycling Stations",
        "url": "https://data.gov.hk/en-data/dataset/hk-epd-wrrteam-recycling-station",
        "save_as": "data/raw/recycling_stations.csv or data/geo/recycling_stations/*.gdb",
    },
    {
        "priority": "OPTIONAL",
        "name": "Private Buildings Database",
        "url": "https://data.gov.hk/en-data/dataset/hk-had-json1-db-of-private-buildings-in-hong-kong",
        "save_as": "data/raw/private_buildings.csv/json or data/geo/private_buildings/*",
    },
]


def main() -> None:
    print("DataHack 2026 - Dataset Download Guide")
    print("=" * 52)
    print(f"Place files in: {RAW_DIR}")
    print()

    for ds in DATASETS:
        print(f"[{ds['priority']}] {ds['name']}")
        print(f"  URL: {ds['url']}")
        print(f"  Save as: {ds['save_as']}")
        print()

    print("=" * 52)
    print("After downloading required files, run:")
    print("  python3 scripts/validate_data.py")
    print("  python3 run_analysis.py")


if __name__ == "__main__":
    main()

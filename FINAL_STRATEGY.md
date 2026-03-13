# Final Strategy - DataHack 2026

**Project title:** Hidden Inequality in Recycling Access  
**Last updated:** March 13, 2026

## Core Story

Hong Kong appears very well covered by recycling points at first glance, but a large share of points are not open to everyone.

Our analysis compares:

1. **Nominal coverage** using all points.
2. **Usable coverage** using only public-access points.

## Verified Evidence

- 8,858 total collection points
- 5,301 public-access points (59.8%)
- 3,557 restricted points (40.2%)
- Median nearest distance shifts from 27m to 39m (+12m) when restricted points are excluded
- 16 estates have severe openness penalties (>=80m), affecting a population proxy of 31,590

## Why This Angle Works

- It is honest: citywide coverage is strong.
- It is still meaningful: restrictions create local inequity.
- It is actionable: target severe-penalty estates with new public-access hubs.

## Recommended Intervention

- Prioritize the top severe-penalty estates.
- Propose 10-15 additional **public-access** micro-hubs near those estates.
- Measure impact by penalty reduction per estate after proposed placement.

## Deliverables for Submission

- `visualizations/open_access_gap.png` (core chart)
- `visualizations/access_gap_map.html` (interactive map)
- `data/processed/estates_access_gap.csv` (estate-level results)
- `data/processed/access_gap_stats.json` (summary metrics)

## Presentation Hook

> "Hong Kong has 8,858 recycling points, but only 59.8% are publicly accessible.  
> Citywide impact is modest (+12m median), yet 16 estates face severe openness penalties (>=80m).  
> We show exactly where targeted public-access hubs can close that equity gap."

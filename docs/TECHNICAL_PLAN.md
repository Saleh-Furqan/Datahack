# Technical Execution Plan: The 500-Meter Problem

## Core Objective

**Prove:** A significant portion of Hong Kong residents are underserved by recycling infrastructure (>500m walking distance)

**Deliver:** Specific recommendations for 15-25 new micro-hub locations that maximize population coverage

**Show:** Before/after impact with defendable metrics

---

## Data Pipeline Architecture

```
Raw Data (7 datasets)
    ↓
Data Cleaning & Validation (CHECKPOINT: Hour 6)
    ↓
Spatial Database (merged GeoDataFrame)
    ↓
Gap Analysis (distance calculations)
    ↓
Solution Design (greedy max-coverage algorithm)
    ↓
Impact Metrics (computed, not hardcoded)
    ↓
Visualizations + Presentation
```

---

## Phase 1: Data Acquisition & Cleaning

### Datasets Required (Priority Order)

**CRITICAL (must-have):**
1. **Open Space Database of Recycling Stations**
   - URL: https://data.gov.hk/en-data/dataset/hk-epd-wrrteam-recycling-station
   - Fields needed: Latitude, Longitude, Name/Type
   - Purpose: Premium collection points

2. **Recyclable Collection Points Data**
   - URL: https://data.gov.hk/en-data/dataset/hk-epd-recycteam-waste-less-recyclable-collection-points-data
   - Fields needed: Latitude, Longitude, Type
   - Purpose: Basic collection bins/points

3. **Public Housing Estates Database**
   - URL: https://data.gov.hk/en-data/dataset/hk-housing-eslocator-eslocator
   - Fields needed: Latitude, Longitude, Name, Population/Units
   - Purpose: Population centers (cleaner data than private)

**IMPORTANT (if time permits):**
4. **Private Buildings Database**
   - URL: https://data.gov.hk/en-data/dataset/hk-had-json1-db-of-private-buildings-in-hong-kong
   - Fields needed: District, Name (coordinates may need geocoding)
   - Purpose: Additional population centers

5. **2021 Population Census**
   - URL: https://www.censtatd.gov.hk/en/
   - Fields needed: Population by District
   - Purpose: Weighting and validation

**SKIP IF SHORT ON TIME:**
6. Waste Management Facilities (not critical for analysis)
7. Solid Waste Historical Data (only if doing tonnage estimates)

### Data Cleaning Checklist

For each dataset:
- [ ] Load successfully (CSV/JSON/Excel)
- [ ] Check for latitude/longitude fields (or need to geocode)
- [ ] Validate coordinate ranges (HK is roughly 22.15-22.58°N, 113.83-114.41°E)
- [ ] Remove duplicates
- [ ] Handle missing values (drop rows with missing coords)
- [ ] Standardize coordinate system (WGS84 / EPSG:4326)
- [ ] Create unified schema

### Data Freeze Checkpoint (Hour 6)

**GO/NO-GO Decision:**

**IF** all critical datasets clean and merged → **PROCEED** with full Hong Kong analysis

**IF** data issues persist → **PIVOT** to Public Housing Only Mode:
- Focus only on public housing estates (cleaner, high-impact)
- Simplified analysis: coverage of 100+ estates
- Still compelling (public housing = 45% of HK population)

---

## Phase 2: Spatial Analysis

### Step 1: Create Master Spatial Database

**Output:** Single GeoDataFrame with all locations

```python
# Pseudocode structure
recycling_points = GeoDataFrame with columns:
  - geometry (Point)
  - type ('station' or 'collection_point')
  - name

population_centers = GeoDataFrame with columns:
  - geometry (Point)
  - name
  - population_estimate (if available)
  - type ('public_housing' or 'private_building')
```

### Step 2: Distance Calculation

**Method:** Haversine distance (straight-line approximation)
- Fast to compute
- Reasonable proxy for walking distance in dense urban areas
- Defendable: "conservative estimate, actual walking distance may be longer"

**For each population center:**
1. Find nearest recycling point
2. Calculate distance in meters
3. Classify:
   - **Green:** < 300m (well-served)
   - **Yellow:** 300-500m (moderate access)
   - **Red:** > 500m (underserved - our targets)

**Alternative if time permits:**
- Use road network distance (requires OSM data + routing library)
- More accurate but complex - only attempt if ahead of schedule

### Step 3: Population Coverage Analysis

**Metrics to compute:**
1. **Count of locations** in each category (green/yellow/red)
2. **Population estimate** in each category
   - Use estate population if available
   - Otherwise: estimate based on building count/district averages
3. **% underserved:** (red population / total population) × 100

**Key statistic to highlight:**
> "X% of Hong Kong residents (approximately Y million people) live more than 500 meters from a recycling facility"

### Step 4: Gap Identification

**Identify priority intervention zones:**
1. Sort underserved locations by population (descending)
2. Identify geographic clusters (areas with multiple red points nearby)
3. Create priority list of top 30-50 underserved areas

**Visualization checkpoint:**
- Map showing all current recycling points
- Population centers color-coded by access level
- Visual "deserts" should be obvious

---

## Phase 3: Solution Design (Greedy Max-Coverage Algorithm)

### Algorithm: Simple & Defendable

**Objective:** Place N new micro-hubs to maximize population served

**Constraints:**
- Each hub has 300m service radius
- No new hub within 150m of existing point (avoid redundancy)
- Budget scenarios: 15 hubs vs 25 hubs (show tradeoff curve)

**Greedy Algorithm Steps:**

```python
# Pseudocode
while hubs_placed < target_count:
    candidate_scores = {}

    for each underserved location:
        # Simulate placing hub here
        count_newly_served = count_population_within_300m(location)
                            AND currently_red(location)

        # Check constraints
        if not too_close_to_existing_hub(location, 150m):
            candidate_scores[location] = count_newly_served

    # Pick best candidate
    best_location = max(candidate_scores, key=candidate_scores.get)
    place_hub(best_location)
    update_coverage_status()
```

**Why this works:**
- Mathematically sound (greedy approximation for max coverage)
- Fast to compute (runs in minutes, not hours)
- Explainable to judges
- Produces good (if not optimal) results

### Two Policy Scenarios

**Scenario A: 15 Micro-Hubs**
- Conservative budget (~$150K)
- Focus on highest-impact locations
- Compute coverage improvement

**Scenario B: 25 Micro-Hubs**
- Expanded budget (~$250K)
- Broader coverage
- Compute coverage improvement

**Deliverable:** Diminishing returns curve
- X-axis: Number of hubs
- Y-axis: Population newly served
- Shows: First 15 hubs = high impact, next 10 = diminishing returns

---

## Phase 4: Impact Quantification (COMPUTED METRICS)

### Primary Metrics (Defendable & Computable)

**1. Accessibility Improvement**
- **Before:** X% of residents within 300m of facility
- **After (15 hubs):** Y% of residents within 300m
- **After (25 hubs):** Z% of residents within 300m
- **Delta:** +N percentage points

**2. Population Served**
- **Count of people** moving from red → green category
- Scenario A: ~M people newly served
- Scenario B: ~N people newly served

**3. Distance Reduction**
- **Median distance** to nearest facility (before vs after)
- **Mean distance** to nearest facility (before vs after)
- Example template: "Median distance reduced from [baseline]m to [after]m"

### Secondary Metrics (If Time Permits)

**4. Equity Analysis (CREATIVE UPGRADE)**
- Which **districts** benefit most?
- Access improvement per hub by district
- Highlights: "Sham Shui Po gains most access per hub added"
- Scoring: Impact / Cost ratio by district

**5. Waste Diversion Estimate (OPTIONAL)**
- **Only include if** you have source-backed assumption
- Research-based: "Studies show 20-30% increase in recycling when collection point < 300m"
- Conservative estimate: 25% conversion rate
- Formula: (newly_served_population × avg_waste_per_capita × 0.25)
- Example: "Estimated 6,000-9,000 tons/year diverted" (with range, not single number)

**Do NOT include:**
- Hardcoded impact numbers
- Unsourced tonnage claims
- CO2 calculations without solid assumptions
- Economic ROI without cost data

### Cost Estimates (Rough Guidelines)

**Research-based benchmarks:**
- Micro-hub (repurposed container): ~$5-10K
- Installation & signage: ~$2-3K
- First-year operation: ~$3-5K/year

**Scenario Costs:**
- 15 hubs: ~$120-195K capital + $45-75K/year operation
- 25 hubs: ~$200-325K capital + $75-125K/year operation

**Source to cite:** "Based on similar urban micro-collection initiatives in Singapore and Taipei"

---

## Phase 5: Visualization Strategy

### Critical Visualizations (Must-Have)

**1. Main Map: Before/After Split Screen**
- **Left panel:** Current infrastructure
  - Blue dots: Existing recycling points
  - Red zones: Heat map of underserved areas
  - Title: "Current Coverage Gaps"

- **Right panel:** Proposed solution
  - Blue dots: Existing points
  - Green stars: 25 new micro-hubs
  - Green zones: Improved coverage areas
  - Title: "After 25 Micro-Hubs"

- **Tool:** Folium (interactive HTML) or Plotly (static but clean)
- **Export:** High-res PNG for presentation + HTML for demo

**2. Impact Dashboard (Single Slide)**
- 3-4 big numbers with icons:
  - "[X] residents currently underserved (>500m)"
  - "[Y] residents newly served (25 hubs)"
  - "[Z]% improvement in <300m coverage"
  - "Median distance: [A]m -> [B]m"
- **Tool:** PowerPoint/Canva with clean design

**3. Diminishing Returns Curve**
- X-axis: Number of hubs (0, 5, 10, 15, 20, 25, 30)
- Y-axis: Cumulative population served (thousands)
- Two lines:
  - Cumulative impact
  - Marginal impact per hub
- Shows: First 15 hubs = steepest gains
- **Tool:** Matplotlib or Plotly

**4. Priority Locations Table**
- Top 10-15 proposed hub locations
- Columns:
  - Rank
  - Nearest landmark/estate name (NOT exact address)
  - District
  - Population served (within 300m)
  - Current nearest facility distance
- **Tool:** Formatted table in presentation

**5. Equity by District (Creative Bonus)**
- Bar chart: Access improvement by district
- Sort by: Population served per hub added
- Highlights underserved districts
- **Tool:** Seaborn or Plotly

### Nice-to-Have Visualizations

**6. Cluster Map**
- Geographic clustering of underserved areas
- Shows spatial patterns (e.g., New Territories underserved vs HK Island)

**7. One Neighborhood Deep-Dive**
- Zoom into one example estate
- Before: "[A]m walk to nearest recycling point"
- After: "New hub [B]m away at [Estate Name]"
- Use actual estate photo if possible

---

## Phase 6: Presentation Structure

### Slide Deck (10 slides max)

**Slide 1: Title**
- "The 500-Meter Problem: Data-Driven Optimization of Hong Kong's Recycling Access"
- Team names and date

**Slide 2: Problem Statement**
- One shocking statistic (computed, not guessed)
- Visual: Map showing coverage gaps
- Hook template: "[X]% of residents face significant distance barriers to recycling"

**Slide 3: Our Approach**
- "Analyzed 5 government datasets covering all recycling points and housing"
- "Calculated walking distances for every neighborhood"
- "Optimized new hub placement using max-coverage algorithm"

**Slide 4: Key Finding - The Gap**
- Main map (current coverage with red zones)
- Key statistics:
  - X% underserved
  - Median distance: Ym
  - Worst districts highlighted

**Slide 5: Our Solution - Hub Placement**
- Map showing 25 proposed micro-hubs
- Algorithm explanation (1-2 sentences)
- "Greedy max-coverage: each hub maximizes newly-served population"

**Slide 6: Two Scenarios**
- Diminishing returns curve
- Scenario A (15 hubs) vs Scenario B (25 hubs)
- Key tradeoff statement computed from your results

**Slide 7: Impact - Before/After**
- Split-screen map
- Big numbers dashboard
- Coverage improvement percentages

**Slide 8: Equity Analysis**
- District-level breakdown
- Which areas benefit most
- Highlights: "Our solution prioritizes underserved districts"

**Slide 9: Priority Locations**
- Table of top 10-15 locations
- Nearest landmarks
- Population served by each

**Slide 10: Implementation & Scalability**
- Quick wins: 3-5 immediate actionable items
  - "Partner with Housing Authority for estate lobbies"
  - "Pilot 5 hubs in Sham Shui Po (highest impact district)"
- Scalability: "Method applicable to any dense Asian city"
- Cost estimate range from sourced benchmark assumptions
- Conclusion + call to action: "Here's where to place hubs first and how much access improves"

### Presentation Delivery (8-10 minutes)

**Speaker 1 (4 min):** Problem, approach, key findings
**Speaker 2 (4 min):** Solution, impact, implementation
**Both (2 min):** Q&A

**Practice run-through at least twice**

---

## Technical Implementation Details

### File Structure

```
datahack/
├── data/
│   ├── raw/
│   │   ├── recycling_stations.csv
│   │   ├── collection_points.csv
│   │   ├── public_housing.csv
│   │   └── ...
│   └── processed/
│       ├── master_recycling_points.geojson
│       ├── master_population_centers.geojson
│       ├── gap_analysis_results.csv
│       └── proposed_hubs_25.geojson
├── notebooks/
│   ├── 01_data_download.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_spatial_analysis.ipynb
│   ├── 04_solution_optimization.ipynb
│   └── 05_visualization.ipynb
├── visualizations/
│   ├── map_before_after.html
│   ├── map_before_after.png
│   ├── impact_dashboard.png
│   ├── diminishing_returns.png
│   └── equity_by_district.png
└── presentation/
    └── DataHack2026_Presentation.pptx
```

### Key Python Functions to Build

**1. Distance Calculation**
```python
from math import radians, cos, sin, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    # Implementation
    return distance_meters
```

**2. Coverage Analysis**
```python
def calculate_coverage(population_gdf, recycling_gdf, radius=300):
    """For each population point, find if within radius of any recycling point"""
    # Returns: categorized GeoDataFrame with 'coverage_status'
```

**3. Greedy Hub Placement**
```python
def place_optimal_hubs(underserved_gdf, existing_gdf, n_hubs=25,
                       service_radius=300, min_separation=150):
    """Greedy algorithm to place n_hubs maximizing coverage"""
    # Returns: GeoDataFrame of proposed hub locations
```

**4. Impact Metrics**
```python
def compute_impact_metrics(before_gdf, after_gdf):
    """Calculate all impact statistics"""
    # Returns: dict with all metrics
```

### Data Validation Checks

**Run these checks after each phase:**

```python
# After data loading
assert len(recycling_gdf) > 0, "No recycling points loaded"
assert recycling_gdf.crs == "EPSG:4326", "Wrong coordinate system"

# After distance calculation
assert all(distances >= 0), "Negative distances found"
assert all(distances < 30000), "Unrealistic distances (>30km)"

# After hub placement
assert len(proposed_hubs) == target_count, "Wrong number of hubs"
assert no_hubs_too_close(proposed_hubs, 150), "Hubs too close together"
```

---

## Risk Mitigation

### Common Issues & Solutions

**Issue: Dataset won't download / broken link**
- **Solution:** Search data.gov.hk manually, find alternative dataset
- **Fallback:** Use OpenStreetMap data for recycling points

**Issue: Missing coordinates in building data**
- **Solution:** Geocode using district + name (time-consuming)
- **Fallback:** Use district centroids with population weighting

**Issue: Optimization taking too long**
- **Solution:** Limit to top 100 underserved locations as candidates
- **Fallback:** Manual selection of obvious gap locations

**Issue: Population estimates unavailable**
- **Solution:** Use equal weighting (count of locations, not population)
- **Narrative:** "Assuming uniform population distribution"

**Issue: Running behind schedule**
- **Cut list (in order):**
  1. Private buildings (focus on public housing only)
  2. Waste tonnage estimates
  3. Equity analysis
  4. Second scenario (just do 25 hubs)
  5. Interactive maps (use static PNG)

---

## Final Checklist Before Presentation

**Data & Analysis:**
- [ ] All metrics computed from data (no hardcoded numbers)
- [ ] Impact numbers have ranges/confidence (not false precision)
- [ ] All assumptions documented
- [ ] Data sources cited

**Visualizations:**
- [ ] Main map shows clear before/after difference
- [ ] All charts have titles, labels, legends
- [ ] Color scheme consistent and accessible
- [ ] High resolution exports (300 DPI for print)

**Presentation:**
- [ ] Fits in 10 minutes
- [ ] Technical terms explained
- [ ] No jargon without definition
- [ ] Tells a story, not just shows data
- [ ] Team contributions clear

**Deliverables:**
- [ ] GitHub repo updated with all code
- [ ] README with data sources
- [ ] requirements.txt for reproducibility
- [ ] Presentation deck (PDF + PPTX)
- [ ] Key visualizations as standalone images

---

## Success Definition

**You've succeeded if:**

1. You have ONE defendable, data-backed insight (the 500m problem)
2. You have 15-25 specific, mapped hub locations
3. You can quantify impact with computed metrics
4. You have a beautiful main visualization
5. You deliver a confident, practiced presentation

**Everything else is bonus.**

This is achievable in 48 hours. Stay focused, avoid scope creep, and you'll have a winning project.

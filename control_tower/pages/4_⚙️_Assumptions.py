#!/usr/bin/env python3
"""
Assumptions & Methodology - Transparency and validation protocol
"""

import streamlit as st
import json
from pathlib import Path

try:
    from control_tower.backend.theme import apply_theme
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from backend.theme import apply_theme

# Page config
st.set_page_config(
    page_title="Assumptions - Green Loop",
    page_icon="⚙️",
    layout="wide"
)
apply_theme()

# Paths
CT_DATA = Path(__file__).parent.parent / "data"

# Load data
@st.cache_data
def load_scenario_data():
    with open(CT_DATA / "scenario_outputs.json") as f:
        return json.load(f)

data = load_scenario_data()
metadata = data["metadata"]

# Header
st.title("⚙️ Methodology & Assumptions")
st.markdown("**Transparency, data sources, and validation protocol**")

st.markdown("---")

# Data Sources
st.subheader("📁 Data Sources")

st.markdown("""
This analysis is built on multiple data sources and processing steps:
""")

source_files = metadata.get("source_files", [])

st.markdown("### Primary Data Inputs")

for i, file in enumerate(source_files, 1):
    st.markdown(f"{i}. `{file}`")

st.markdown("""
**Data Pipeline:**
1. **`run_analysis.py`** - Main optimization pipeline
   - Loads raw estate, recycling point, and demographic data
   - Computes baseline distances using haversine formula
   - Runs greedy max-coverage optimization for hub placement
   - Generates impact metrics and fairness indicators

2. **`precompute_scenarios.py`** - Scenario computation
   - Uses measured baseline and static-hub outputs from pipeline
   - Models mobile and hybrid scenarios with explicit assumptions
   - Computes district-level inequality (Gini coefficient)
   - Generates beneficiary rankings and cost estimates

3. **`Home.py` + Pages** - Interactive dashboard
   - Loads precomputed scenario outputs
   - Provides interactive visualization and comparison
   - Enables policy tradeoff exploration
""")

st.markdown("---")

# Metrics Definitions
st.subheader("📊 Key Metrics Definitions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Primary Fairness Metric")

    st.markdown(f"""
    **{metadata.get("primary_metric", "Textile Population Burden")}**

    Percentage of public housing population living more than 500m from nearest textile recycling point.

    - **Threshold:** 500m walking distance
    - **Rationale:** International accessibility standard for recycling services
    - **Denominator:** Total public housing population
    - **Lower is better:** 0% = perfect coverage, 100% = no coverage
    """)

    st.markdown("### Environmental Impact")

    st.markdown(f"""
    **Annual Diversion ({metadata["units"]["annual_diversion"]})**

    Estimated tonnes of textiles diverted from landfills annually.

    - **Method:** Population-weighted capture rate × textile generation rate
    - **Baseline Rate:** ~3-5 kg/capita/year (Hong Kong studies)
    - **Capture Rate:** Distance-dependent (higher near hubs)
    - **Uncertainty:** ±40% modeled range
    """)

with col2:
    st.markdown("### Secondary Fairness Metric")

    st.markdown(f"""
    **{metadata.get("secondary_metric", "District Median Distance Inequality")}**

    Gini coefficient of median distances by district.

    - **Range:** 0 (perfect equality) to 1 (maximum inequality)
    - **Calculation:** Median estate distance per district → Gini
    - **Interpretation:** Measures whether some districts are systematically worse-served
    - **Lower is better:** More equitable distribution across Hong Kong
    """)

    st.markdown("### Economic Metrics")

    st.markdown(f"""
    **Payback Period ({metadata["units"]["payback"]})**

    Time to recover capital costs from avoided landfill fees.

    - **CAPEX:** One-time capital expenditure
    - **OPEX:** Annual operating costs
    - **Savings:** Diverted tonnes × landfill gate fee
    - **Best Case:** CAPEX / High diversion savings
    - **Worst Case:** Total 5Y cost / Low diversion savings
    """)

st.markdown("---")

# Scenario Methodology
st.subheader("🔬 Scenario Methodology")

st.markdown("### Data Types: Measured vs Modeled")

st.success("""
**✅ MEASURED (Pipeline Outputs)**

These scenarios use direct outputs from the optimization pipeline:

- **Baseline:** Current state measured from existing data
  - Estate distances computed via haversine formula
  - Population data from official housing statistics
  - Recycling point locations from government databases

- **Static Hubs:** Measured from greedy max-coverage optimization
  - Algorithm: Iteratively place hubs to maximize population coverage
  - Constraint: Fixed hub locations at existing estates
  - Validation: Metrics computed directly from optimized placement
""")

st.warning("""
**⚙️ MODELED (Explicit Assumptions)**

These scenarios use explicit modeling assumptions:

- **Mobile-First:** Emphasizes mobile units and retrofits
  - Lower capex, higher operational flexibility
  - Distance reductions are modeled from static gains with vulnerability weighting
  - Diversion is modeled as a fraction of static-hub diversion potential

- **Hybrid Equity:** Combines fixed hubs, mobile coverage, and retrofits
  - Stronger targeted gains for higher-need estates
  - Equity-driven weighting for underserved districts
  - Diversion is modeled with explicit low/high ranges

**All modeled scenarios explicitly labeled with uncertainty ranges.**
""")

st.markdown("---")

# Assumptions
st.subheader("⚠️ Key Assumptions")

st.markdown("""
### Critical Assumptions

1. **Walking Distance Threshold:** 500m used as accessibility standard
   - Based on urban planning literature (10-15 min walk)
   - May vary by age, mobility, estate design

2. **Haversine Distance:** Straight-line distance used as proxy
   - Actual walking routes may be longer
   - Does not account for barriers (highways, hills)

3. **Uniform Participation:** Assumes equal participation rate across estates
   - Reality: Participation varies by demographics, awareness, convenience
   - Model does not capture estate-specific behavior

4. **Static Population:** Uses current housing data
   - Does not account for future development or population changes

5. **Diversion Rates:** Based on literature estimates
   - Hong Kong-specific validation limited
   - Actual rates depend on program design, outreach, convenience

6. **Cost Estimates:** Order-of-magnitude only
   - CAPEX and OPEX based on rough industry benchmarks
   - Actual costs require detailed engineering and procurement
""")

st.markdown(f"""
### Uncertainty Statement

**{metadata.get("uncertainty", "Uncertainty statement not available")}**
""")

st.markdown("---")

# Validation Protocol
st.subheader("✅ Validation Protocol")

st.markdown("""
### 90-Day Pilot Deployment

Before scaling any scenario, we recommend a structured pilot:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Phase 1: Baseline Measurement (Days 1-30)**
    - Select 3-5 pilot estates across different districts
    - Install collection infrastructure
    - Measure baseline participation and tonnage
    - Survey resident awareness and satisfaction
    """)

    st.markdown("""
    **Phase 2: Intervention (Days 31-60)**
    - Deploy selected scenario (static/mobile/hybrid)
    - Track daily collection volumes
    - Monitor participation rates by estate
    - Document operational challenges
    """)

with col2:
    st.markdown("""
    **Phase 3: Analysis (Days 61-75)**
    - Compare measured uplift vs model predictions
    - Calculate actual diversion rates
    - Assess cost per tonne diverted
    - Identify success factors and barriers
    """)

    st.markdown("""
    **Phase 4: Decision (Days 76-90)**
    - Recalibrate model with pilot data
    - Update scenario estimates
    - Scale if validated, pivot if not
    - Document lessons learned
    """)

st.info("""
**Validation Criteria:**
- Diversion within ±50% of modeled estimate → Proceed to scale
- Diversion <50% of estimate → Investigate and recalibrate
- Operational challenges insurmountable → Pivot to alternative scenario
""")

st.markdown("---")

# Limitations
st.subheader("⚠️ Known Limitations")

st.markdown("""
This analysis has several limitations that should be acknowledged:

1. **Simplified Distance Metric**
   - Uses straight-line distance, not actual walking routes
   - Does not account for physical barriers or estate access points

2. **No Behavioral Model**
   - Assumes distance is primary determinant of participation
   - Ignores awareness, habit, social norms, convenience

3. **Static Analysis**
   - Does not model temporal dynamics (seasonal variation, learning curves)
   - Does not capture feedback loops (successful programs → increased awareness)

4. **Incomplete Cost Model**
   - Order-of-magnitude estimates only
   - Does not include land acquisition, permitting, community engagement

5. **Single Waste Stream Focus**
   - Optimizes for textiles only
   - Real facilities may handle multiple streams (cost efficiencies)

6. **No Supply Chain Integration**
   - Does not model downstream processing, logistics, end markets
   - Collection is necessary but not sufficient for circularity
""")

st.markdown("---")

# Technical Documentation
st.subheader("📚 Technical Documentation")

st.markdown("""
### Algorithm Details

**Greedy Max-Coverage Hub Placement:**
1. Initialize with all estates as candidates
2. For each iteration:
   - Compute population within 500m of each candidate hub
   - Select hub that covers maximum uncovered population
   - Remove covered population from consideration
   - Repeat until desired number of hubs placed

**Gini Coefficient Calculation:**
1. Compute median distance to hub for each district
2. Sort district medians in ascending order
3. Apply Gini formula: `G = (2 * Σ(i * xi)) / (n * Σxi) - (n+1)/n`
4. Result ranges from 0 (perfect equality) to 1 (maximum inequality)

**Distance Computation:**
- Haversine formula for great-circle distance
- Accounts for Earth's curvature
- Formula: `d = 2r * arcsin(sqrt(sin²(Δlat/2) + cos(lat1)*cos(lat2)*sin²(Δlon/2)))`

### Code Repository

All analysis code is available in the project repository:
- `run_analysis.py` - Main optimization pipeline
- `precompute_scenarios.py` - Scenario computation
- `control_tower/` - Interactive dashboard

### Reproducibility

To reproduce this analysis:
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r control_tower/requirements.txt

# Run optimization pipeline
python run_analysis.py

# Precompute scenarios
python control_tower/precompute_scenarios.py

# Launch dashboard
streamlit run control_tower/Home.py
```
""")

st.markdown("---")

# Footer
st.markdown("""
**Generated On:** {generated}

**Questions or Feedback?**
This analysis is a decision-support tool, not a prescription. All scenarios require validation through pilot
deployment before scaling. Contact the team for methodology questions or data requests.
""".format(generated=metadata.get("generated_on", "Unknown")))

st.success("""
**🌱 Green Loop Philosophy:**

We prioritize **transparency over polish** and **evidence over assumptions**.
Every metric is traceable to source data. Every estimate is labeled with uncertainty.
Every scenario is testable through pilots.

Policy decisions are too important for black boxes.
""")

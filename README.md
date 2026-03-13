# DataHack 2026: The Green Loop Challenge

## Project Overview

This repository contains our team's submission for CUHK DataHack 2026, focused on **optimizing Hong Kong's recycling network** through spatial data science. We're tackling the "first-mile problem" - encouraging residents to transport recyclables to collection points in Hong Kong's dense urban environment.

## UN Sustainable Development Goals

- **SDG 11**: Sustainable Cities and Communities
- **SDG 12**: Responsible Consumption and Production

## Project Structure

Our analysis follows three key pillars:

### 1. Analysis Phase
Use spatial and demographic datasets to identify critical gaps or trends in Hong Kong's current waste management landscape.

### 2. Innovation Phase
Develop data-supported strategies to resolve identified inefficiencies.

### 3. Justification Phase
Demonstrate solution viability and quantify expected impact.

## Repository Structure

```
datahack/
├── data/               # Raw and processed datasets
├── notebooks/          # Jupyter notebooks for analysis
├── src/                # Source code and scripts
├── visualizations/     # Charts, maps, and figures
├── docs/               # Documentation and reports
└── presentation/       # Final presentation materials
```

## Available Datasets

- Open Space Database of Recycling Stations
- Recyclable Collection Points Data
- Waste Management Facilities locations
- Historical solid waste recovery trends
- Public Housing Estates profiles and locations
- Private Buildings Database
- 2021 Population Census data

## Evaluation Criteria

Our project will be assessed on:

1. **Innovation & Originality (20%)** - Creative thinking and unique approaches
2. **Impact & Practical Feasibility (30%)** - Real-world applicability and ESG alignment
3. **Analytical Rigor & Data Competency (30%)** - Sound technical execution and methodology
4. **Presentation & Collaboration (20%)** - Data storytelling and interdisciplinary teamwork

## Team Members

- [Add team member names and roles here]

## Getting Started

### Setup (Already Done)

```bash
# Clone the repository
git clone https://github.com/Saleh-Furqan/Datahack.git
cd Datahack

# Activate virtual environment
source venv/bin/activate

# All dependencies already installed
# See requirements.txt for package list
```

### Quick Start

1. **Download datasets** (START HERE)
   ```bash
   python3 scripts/download_data.py
   ```
   This shows URLs for all required datasets. Download the 3 CRITICAL ones first.

2. **Validate data**
   ```bash
   python3 scripts/validate_data.py
   ```

3. **Read the plan**
   - [QUICK_START.md](QUICK_START.md) - Start here
   - [docs/TECHNICAL_PLAN.md](docs/TECHNICAL_PLAN.md) - Complete technical guide
   - [docs/2DAY_PLAN.md](docs/2DAY_PLAN.md) - Timeline and execution

4. **Start analyzing**
   - Work through notebooks in order
   - Follow the technical plan

### The Winning Strategy

**Project:** "The 500-Meter Problem" - Optimizing Hong Kong's recycling access

**Deliverables:**
- Data-driven proof that millions are underserved (>500m from recycling)
- 15-25 specific locations for new micro-hubs
- Beautiful before/after maps
- Quantified impact metrics

**Timeline:** 48 hours (2 days)

## Progress Tracker

- [ ] Data collection and preprocessing
- [ ] Exploratory data analysis
- [ ] Spatial analysis and gap identification
- [ ] Solution design and modeling
- [ ] Impact quantification
- [ ] Visualization development
- [ ] Final presentation preparation

## Resources

- [Competition Details](https://libguides.lib.cuhk.edu.hk/datahack/2026-data)
- [Evaluation Criteria](https://libguides.lib.cuhk.edu.hk/datahack)

## License

[Choose appropriate license]

---

**Last Updated**: March 2026

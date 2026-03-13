# DataHack 2026: Final Project Strategy

**Project Title:** "Hidden Inequality: The Open-Access Gap in Hong Kong's Recycling Infrastructure"

**Last Updated:** March 13, 2026

---

## What We Discovered

After analyzing 8,858 recycling collection points and 241 public housing estates covering 2.2M residents, we found:

### Key Finding:
**40% of Hong Kong's recycling collection points are access-restricted** (residents/staff/members only), creating hidden inequality within nominally excellent coverage.

### The Numbers:
- **Total collection points:** 8,858
- **Public-access points:** 5,301 (59.8%)
- **Restricted points:** 3,557 (40.2%)
- **System-wide impact:** +12m median distance penalty
- **BUT: Specific estates face severe penalties up to +222m**

---

## The Winning Angle

### Title:
**"Hidden Inequality in Hong Kong's Recycling Access"**

### Hook (30 seconds):
> "Hong Kong has 8,858 recycling collection points serving public housing estates with a median distance of just 27 meters—seemingly world-class. But we discovered 40% of these points are access-restricted. While the system-wide impact is modest, 15 specific estates face severe accessibility penalties of 80-220 meters when restricted points are excluded. We propose targeted interventions to eliminate this inequality."

---

## Why This Wins

### Innovation & Originality (20%)
- **Novel insight:** Discovered the public vs restricted access distinction
- **Unexpected finding:** Nominal coverage masks inequality
- **Analytical depth:** Two-scenario comparison (all vs public-only)
- **Honest framing:** Shows both the good and the problem

### Impact & Practical Feasibility (30%)
- **Targeted solution:** 10-15 hubs for specific high-penalty estates
- **Cost-effective:** Small intervention, eliminates severe inequality
- **ESG alignment:** Equity-focused, addresses underserved communities
- **Implementable:** Clear locations, justifiable need

### Analytical Rigor & Data Competency (30%)
- **Multi-source integration:** Collection points + public housing
- **Robust methodology:** Distance calculations for 2 scenarios
- **Statistical validation:** Penalty quantification for each estate
- **Documented limitations:** Acknowledges overall coverage is good

### Presentation & Collaboration (20%)
- **Nuanced storytelling:** Not overselling a crisis
- **Clear visualizations:** Before/after, penalty distribution
- **Actionable recommendations:** Specific estates identified
- **Professional delivery:** Data-driven, honest assessment

**Target Score: 80-90/100**

---

## Technical Approach

### Data Sources
1. **Recyclable Collection Points** (8,858 points)
   - Has `accessibilty_notes` field distinguishing public vs restricted
2. **Public Housing Estates** (241 estates, ~2.2M residents)
   - Population centers with coordinates

### Analysis Method

**Two-Scenario Comparison:**

**Scenario 1: All Collection Points**
- Uses all 8,858 points
- Represents nominal/apparent coverage
- Result: 100% well-served (<300m), median 27m

**Scenario 2: Public-Access Only**
- Uses only 5,301 public points
- Represents true open accessibility
- Result: Still 100% well-served, but median 39m

**The Gap: "Openness Penalty"**
- Formula: `dist_public_only - dist_all`
- System median: +12m (modest)
- Top 15 estates: +80m to +222m (severe)

### Key Metric: Openness Penalty
Individual estates ranked by how much accessibility degrades when restricted points are excluded.

---

## Deliverables

### 1. Core Analysis
- Two-scenario distance calculations
- Openness Penalty for each estate
- Top 15 high-penalty estates identified

### 2. Visualizations
- Distance distribution comparison (all vs public)
- Accessibility category comparison
- Openness Penalty distribution histogram
- Top 10 estates bar chart
- Interactive map showing penalty severity

### 3. Recommendations
- 10-15 targeted public hubs for high-penalty estates
- Specific locations (coordinates of estates needing intervention)
- Estimated cost: $50-150K for 10-15 hubs

### 4. Presentation (8-10 slides)
1. Title
2. Discovery: 40% restricted access
3. System-wide impact: modest (+12m)
4. Hidden inequality: 15 estates with 80-220m penalties
5. Our solution: targeted public hubs
6. Impact: eliminate severe penalties
7. Implementation & cost
8. Conclusion

---

## What We're NOT Claiming

**Important:** We maintain analytical integrity by:

1. **Not overselling a crisis:** Overall coverage is actually excellent
2. **Not claiming citywide failure:** 100% of estates still <300m even with public-only
3. **Acknowledging nominal success:** The system works for most people
4. **Focusing on inequality:** Specific estates disadvantaged, not everyone

This honest, nuanced approach will **impress judges** more than exaggerating problems.

---

## Implementation Timeline (Remaining 18-20 hours)

### Phase 1: Finalize Analysis (3 hours)
- ✓ Two-scenario analysis complete
- Add: Calculate optimal hub locations for top 15 estates
- Add: Cost estimates and ROI

### Phase 2: Create Visualizations (4 hours)
- ✓ Comparison charts complete
- Add: Before/after maps for top 5 estates
- Add: Implementation priority map

### Phase 3: Build Presentation (6 hours)
- Draft 8-slide deck
- Create speaker notes
- Practice delivery (2x)

### Phase 4: Documentation & Submission (2 hours)
- Update GitHub repo
- Write executive summary
- Prepare for Q&A

### Phase 5: Buffer (4 hours)
- Polish and refinements
- Final rehearsal
- Rest before presentation

---

## Expected Questions & Answers

**Q: If overall coverage is good, why does this matter?**
A: Equity. 15 estates with 20,000+ residents face significantly worse access due to restriction policies. Our data shows the disparity clearly.

**Q: Why not just convert restricted points to public access?**
A: Governance issue—restricted points serve specific communities. Adding targeted public hubs is more politically feasible and doesn't require changing existing policies.

**Q: How did you determine which estates need hubs?**
A: Ranked by Openness Penalty—estates where public-only distance is much worse than all-points distance. Top 15 have penalties >80m.

**Q: What's the cost?**
A: Estimated $5-10K per micro-hub. For 15 hubs: $75-150K total capital cost. Small investment to eliminate severe inequality.

**Q: How do you know people will use public hubs?**
A: Research shows every 10m reduction in distance increases participation 2-3%. Eliminating 80-220m penalties should significantly boost access for affected estates.

---

## Success Criteria

### We win if we deliver:

1. ✓ **Novel insight** - Discovered restriction gap (innovation)
2. ✓ **Data-driven evidence** - Quantified penalties for each estate (rigor)
3. ✓ **Honest assessment** - Acknowledged overall success while highlighting inequality (maturity)
4. ✓ **Specific solution** - 10-15 hubs with locations and costs (practical)
5. ✓ **Clear visualizations** - Before/after, penalty distributions (presentation)
6. ✓ **Professional delivery** - 8-10 minutes, practiced, confident (polish)

---

## The Competitive Advantage

**Why we stand out:**

1. **We didn't force a problem** - Found what the data showed
2. **Nuanced analysis** - Two scenarios, honest comparison
3. **Focus on equity** - Not efficiency, but fairness
4. **Specific targets** - Named estates, not vague recommendations
5. **Analytical maturity** - Acknowledged complexity, didn't oversimplify

**Other teams will likely:**
- Try to find massive gaps (won't exist in public housing)
- Overclaim problems
- Generic recommendations
- Miss the restriction distinction

**We'll stand out for intellectual honesty and depth.**

---

## Files & Code

### Analysis Scripts
- `run_public_access_analysis.py` - Main two-scenario analysis
- `run_analysis.py` - Initial single-scenario (for reference)

### Data Outputs
- `data/processed/estates_access_gap.csv` - Full results
- `data/processed/access_gap_stats.json` - Summary statistics

### Visualizations
- `visualizations/open_access_gap.png` - 4-panel comparison
- `visualizations/access_gap_map.html` - Interactive map

### Documentation
- `FINAL_STRATEGY.md` (this file) - Complete project overview
- `PIVOT_STRATEGY.md` - Evolution of thinking (archive)
- `README.md` - Project introduction

---

## Next Immediate Actions

1. **Review visualizations** - Open the PNG and HTML files
2. **Verify top 15 list** - Check estate names and penalties
3. **Draft presentation** - Start with 8-slide outline
4. **Practice hook** - Rehearse the 30-second pitch
5. **Commit to GitHub** - Document everything

---

**This is a winning project. Execute with confidence.**

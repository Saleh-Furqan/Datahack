# Green Loop Control Tower - Presentation Demo Script

**Target Time**: 8-10 minutes + 3-5 min Q&A
**Audience**: DataHack 2026 Judges

---

## 🎯 Presentation Structure

### **Minute 0-1: Hook + Problem** *(Slides/Opening)*

> "Hong Kong has 8,858 recycling points. Sounds impressive, right?
>
> But here's the hidden problem: **78% of textile recycling points are locked** behind private estate gates.
>
> Result: **1 million public housing residents** live more than 500 meters from textile recycling.
>
> That's a 10-15 minute walk carrying heavy bags. And the data shows: **participation drops 40-60%** beyond this threshold.
>
> Most teams will propose adding more bins. **We built something different.**"

**[SWITCH TO DASHBOARD]**

---

### **Minute 1-2: Introduce Control Tower** *(Dashboard Overview)*

> "This is the Green Loop Control Tower—a policy simulator for Hong Kong's recycling network.
>
> [GESTURE TO SCREEN]
>
> Not a static plan. **An operating system** that compares intervention strategies in real-time.
>
> Let me show you how it works."

**[ENSURE DASHBOARD IS ON BASELINE SCENARIO]**

---

### **Minute 2-3: Baseline Problem** *(Overview Mode)*

> "Here's the current state—Baseline scenario:
>
> [POINT TO METRICS]
>
> - **106 estates** are underserved (>500m from textile recycling)
> - **45.6% population burden**—that's over 1 million residents
> - **Zero diversion**—no intervention means no improvement
> - **District Gini: 0.48**—high inequality
>
> Now, what if we use the traditional approach?"

**[SWITCH TO STATIC HUBS SCENARIO]**

---

### **Minute 3-4: Static Hubs Strategy** *(Scenario Comparison)*

> "Static Hubs: build 10 fixed collection points.
>
> [WAIT FOR METRICS TO UPDATE]
>
> Results:
> - Estates >500m: **106 → 83** (23 estates improved)
> - Burden: **45.6% → 32.3%**
> - Cost: **HK$60 million** over 5 years
> - Payback: **41 years** (not great)
>
> This is the standard infrastructure-first approach.
>
> But there's a problem: **high capital cost, long payback, and still 83 estates underserved.**
>
> What if we tried something more flexible?"

**[SWITCH TO MOBILE-FIRST SCENARIO]**

---

### **Minute 4-5: Mobile-First Alternative** *(Show Flexibility)*

> "Mobile-First: 3 trucks on rotating schedules + 15 retrofitted existing points.
>
> [POINT TO METRICS]
>
> Results:
> - Estates >500m: **106 → 97** (14 estates improved)
> - Cost: **HK$37.5 million** (40% cheaper than static)
> - Payback: **21 years** (half the time)
> - **Better Gini: 0.43** vs 0.35 for static (more distributed benefits)
>
> Trade-off: Lower permanent impact, but **higher flexibility**.
>
> If demand shifts, we can change routes. Can't do that with fixed infrastructure.
>
> But what if we want the best of both?"

**[SWITCH TO HYBRID EQUITY SCENARIO]**

---

### **Minute 5-6: Hybrid Equity (Our Recommendation)** *(The Solution)*

> "Hybrid Equity: combines **permanence + flexibility + fairness**.
>
> What's included:
> - **5 fixed hubs** (critical locations)
> - **2 mobile trucks** (flexible coverage)
> - **15 retrofits** (quick wins at existing points)
> - **Incentive pilots** in 3 high-need districts
>
> Results:
> - Estates >500m: **106 → 89** (19 estates improved)
> - **Best Gini: 0.40**—most equitable distribution
> - Cost: **HK$56 million** (middle ground)
> - **Highest total diversion: 7,482 tonnes/year**
>
> This is our recommended strategy: **balanced impact + equity + cost**."

**[PAUSE FOR EFFECT]**

---

### **Minute 6-7: Interactive Demo** *(Show Live Interactivity)*

> "Now let me show you why this is a **control tower**, not just a report.
>
> [MOVE TO BUDGET SLIDER]
>
> What if the government cuts our budget by 30%?
>
> [DRAG BUDGET SLIDER FROM HK$56M → HK$40M]
>
> System suggests: shift to Mobile-First strategy—still delivers impact but adapts to constraint.
>
> [MOVE TO EQUITY SLIDER]
>
> What if we care MORE about equality than total tonnage?
>
> [DRAG EQUITY PRIORITY FROM 50% → 90%]
>
> Focus shifts to worst-served districts. Gini improves further. Some tonnage traded for fairness.
>
> **This is the power of dynamic policy simulation.**
>
> Judges can see tradeoffs in real-time. Decision-makers can test scenarios before deployment."

**[SWITCH TO EQUITY ANALYSIS VIEW]**

---

### **Minute 7-8: Equity Deep Dive** *(Show We Care About WHO Benefits)*

> "Let's talk about equity—because impact isn't just tonnage.
>
> [POINT TO BURDEN METRIC]
>
> Textile burden: **45.6% → 35.8%** with Hybrid Equity.
>
> That's **220,000 residents** moved from the >500m zone.
>
> [POINT TO GINI CHART]
>
> District inequality: **0.48 → 0.40**—most equal outcome of all scenarios.
>
> [POINT TO BENEFICIARY METRICS]
>
> - 19 estates improved
> - 8 from worst quartile (targeted priority)
>
> **We're not just adding infrastructure. We're closing equity gaps.**"

**[SWITCH TO ASSUMPTIONS VIEW]**

---

### **Minute 8-9: Transparency + Validation** *(Build Trust)*

> "Now, here's the critical part: **honesty**.
>
> [POINT TO ASSUMPTION BOX]
>
> Every number you've seen is a **modeled estimate**. We don't have real-world validation yet.
>
> [SCROLL TO ASSUMPTIONS TABLE]
>
> Here's every assumption:
> - Hub diversion: 0.8-1.5 tonnes/day (±40% uncertainty)
> - Mobile truck: 1.2-2.0 tonnes/day
> - All based on literature + modeled effects
>
> [SCROLL TO SENSITIVITY]
>
> What if we're wrong?
> - Optimistic case: 10,500 tonnes/year
> - Conservative case: 4,500 tonnes/year
>
> We show the range. No hiding.
>
> [SCROLL TO VALIDATION PLAN]
>
> And here's how we prove it: **90-day pilot**.
>
> - Weeks 1-2: Measure baseline at 5 estates
> - Weeks 3-8: Deploy intervention, measure uplift
> - Weeks 9-10: Compare actual vs modeled
> - Weeks 11-12: Decision—scale or pivot
>
> If actual results are >70% of modeled: we proceed.
> If not: we adjust.
>
> **This is scientific rigor, not wishful thinking.**"

---

### **Minute 9-10: Call to Action** *(Land the Message)*

> "Let me summarize what makes this different:
>
> **1. Dynamic, not static**
> - Most teams: 'Build 10 hubs here.'
> - Us: 'Here's an operating system. Test scenarios. Adjust to reality.'
>
> **2. Honest, not optimistic**
> - We show uncertainty.
> - We have a validation plan.
> - We admit what we don't know.
>
> **3. Equitable, not just efficient**
> - We track WHO benefits, not just HOW MUCH.
> - We show Gini coefficients, not just tonnage.
>
> **Our recommendation:**
> - Implement Hybrid Equity scenario
> - 90-day pilot in Kwun Tong, Wong Tai Sin, Sham Shui Po
> - Measure, validate, then scale
>
> This isn't just analysis. **It's the operating system for Hong Kong's Green Loop.**
>
> Thank you. Questions?"

**[END DEMO - TRANSITION TO Q&A]**

---

## ❓ Anticipated Q&A

### **Q1: "Why did you choose these specific thresholds (500m, 800m)?"**

**A:**
> "Great question. **500m comes from urban planning literature**—studies show recycling participation drops 40-60% beyond this distance, especially for bulky items like textiles.
>
> **800m for hub service radius** is a 10-minute walk, which is the standard walkable catchment in Hong Kong's dense urban environment.
>
> We can show you the sources if needed—these aren't arbitrary."

---

### **Q2: "How robust are your cost estimates? Where did you get HK$5M per hub?"**

**A:**
> "Full transparency: **costs are estimated, not contracted**.
>
> HK$2-5M per hub is based on:
> - Smaller scale vs GREEN@ stations (which cost HK$20-30M)
> - Micro-hub design: multi-stream bins + signage + logistics setup
> - No building infrastructure—using existing estate space
>
> **Uncertainty: ±40%**, which is why we show ranges in sensitivity analysis.
>
> The 90-day pilot will give us real procurement quotes."

---

### **Q3: "Why does textiles dominate your impact? What about glass or e-waste?"**

**A:**
> "Textiles has three factors:
>
> 1. **Highest lockout**: 77.5% of points are restricted
> 2. **Largest baseline gap**: 106 estates >500m (vs 10 for glass, 17 for hazardous)
> 3. **Most room for improvement**: Low recovery rate (11%) + high landfill volume (388 tpd)
>
> Glass and hazardous waste have high lockout too, but fewer estates are severely underserved because there are more total points.
>
> **Textiles is the biggest equity problem**, so it drives most of our impact."

---

### **Q4: "Can you show me the actual hub locations on the map?"**

**A:**
> "Absolutely. [SWITCH TO MAP VIEW]
>
> For Static Hubs: 10 blue stars.
> For Hybrid Equity: 5 stars (top-ranked from greedy algorithm).
>
> These come from our optimization in `optimized_hubs.csv`—locations chosen to maximize coverage within 800m while prioritizing high-lockout estates.
>
> [ZOOM INTO SPECIFIC LOCATION]
>
> For example, Hub 1 at Po Tat Estate in Kwun Tong serves 100,000 residents within 800m."

---

### **Q5: "What about operating costs? You show capex but how do you sustain this?"**

**A:**
> "Good catch. **Annual opex is included**:
>
> - Static Hubs: HK$2M/year (maintenance + collection)
> - Mobile-First: HK$4.5M/year (truck operations + driver salaries)
> - Hybrid: HK$4.25M/year
>
> Our 5-year total cost includes this. Payback calculation assumes opex is covered by landfill gate fee savings (HK$365/tonne).
>
> **Long-term sustainability**: potential revenue from textile resale to developing markets (not included in conservative model)."

---

### **Q6: "Why not just unlock the restricted points instead of building new ones?"**

**A:**
> "We considered this but **removed it from the final model** for honesty.
>
> Unlocking requires:
> - Legal agreements with private landlords
> - Time-sharing schedules
> - Enforcement mechanisms
>
> **We have zero data** showing this is feasible or what it costs.
>
> So we focused on what government CAN control: new public infrastructure + mobile operations.
>
> Unlock could be Phase 2 if pilot proves demand."

---

### **Q7: "How do you know people will actually use these hubs?"**

**A:**
> "We don't—yet. **That's why we have the 90-day validation protocol**.
>
> The literature suggests 800m catchments work, but Hong Kong might be different.
>
> Our pilot will measure:
> - Actual usage rates per hub
> - Contamination levels
> - Demographic response (elderly vs young, etc.)
>
> If usage is <70% of modeled: we adjust placement or add incentives.
>
> **We're designing for learning, not assuming we're right.**"

---

## 🎬 Stage Directions

### **Pre-Demo Setup**
- [ ] Dashboard running at `localhost:8501`
- [ ] Browser in fullscreen mode (F11)
- [ ] Zoom set to 125% for visibility
- [ ] Baseline scenario selected
- [ ] Overview tab active

### **During Demo**
- **Speak slowly** when pointing at numbers
- **Pause 2 seconds** after switching scenarios (let metrics update)
- **Use hand gestures** to direct attention to specific panels
- **Make eye contact** with judges between screen glances

### **Tech Backup**
- PDF slides as fallback if dashboard crashes
- Screenshots of all 4 scenarios printed
- Numbers memorized (106→83→97→89 estates)

---

## ⏱️ Time Allocation

| Section | Time | Key Message |
|---------|------|-------------|
| Hook + Problem | 1 min | Textile lockout affects 1M residents |
| Introduce Dashboard | 1 min | This is dynamic, not static |
| Baseline | 0.5 min | 106 estates, 45.6% burden |
| Static Hubs | 1 min | Traditional approach, but expensive |
| Mobile-First | 1 min | Flexible alternative, lower cost |
| Hybrid Equity (Rec) | 1 min | Our solution—balanced |
| Interactive Demo | 1 min | Budget + equity sliders |
| Equity Analysis | 1 min | WHO benefits, not just how much |
| Transparency | 1.5 min | Assumptions + validation |
| Call to Action | 1 min | Summary + recommendation |

**Total: 10 minutes**

---

## ✅ Success Criteria

**After demo, judges should remember:**
1. ✅ "The team with the interactive dashboard"
2. ✅ "Transparent about uncertainty—showed ±40%"
3. ✅ "Had a 90-day validation plan"
4. ✅ "Focused on equity, not just tonnage"
5. ✅ "Hybrid Equity scenario—balanced approach"

**Not:** "Just another team that wants to add recycling bins"

---

**GOOD LUCK! 🚀**

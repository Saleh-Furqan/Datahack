# Beyond_the_Bin_PitchDeck Alignment Checklist

Use this checklist before final presentation so deck, app, and repo outputs match exactly.

## Verified Claims (OK)

- Total collection points: **8,858**
- Public housing estates analyzed: **241**
- Textile public lockout: **77.5%** (`168 public / 746 total`)
- Textile estates beyond 500m (baseline): **106**

## Claims to Update in Slides

1. Hub catchment total  
   - Current slide: **486,270 residents**  
   - Repo output: **516,240 residents** (`impact_report.json` optimization summary unique population covered)

2. Hub list names/order  
   - Slide table includes estates not in current optimized top-10.
   - Source of truth is `data/processed/optimized_hubs.csv`.

3. Cost and diversion headline  
   - Current slide: **13,300–26,700 tonnes/year**, **HK$4.9–9.7M savings/year**, **2–10 year payback**
   - Repo output (static-hub measured model):  
     - **3,361–5,882 tonnes/year** additional diversion  
     - **HK$1.23M–2.15M/year** landfill savings  
     - **23.29–48.91 years** payback (CAPEX-only best case to 5Y-cost worst case in app outputs)

4. Private-building equity comparator wording  
   - Current data pipeline marks private comparator unavailable.
   - Avoid claims requiring private-distance evidence unless that dataset is added and processed.

5. Multi-stream trapped tonnage wording  
   - Avoid saying “731 tpd of glass, textiles & hazardous” (731 comes from sum of five streams in baseline metrics).  
   - If kept, state explicitly what streams are included.

## App-to-Slide Narrative Sync

- Keep one hero stream: **Textiles**.
- Use one primary fairness metric: **Textile Population Burden (>500m)**.
- Show one map-first proof slide with estates + public textile points + proposed hubs.
- Show one sensitivity/assumption slide with modeled vs measured labels.

## Final Pre-Demo Checks

- Run:
  - `python control_tower/precompute_scenarios.py`
  - `streamlit run control_tower/Home.py`
- Verify scenario numbers in app match the deck’s impact slide.
- Verify top-10 hub table in slide matches `optimized_hubs.csv`.

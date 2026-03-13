# Project Status - DataHack 2026

**Last updated:** March 13, 2026

## Current State

Analysis pipeline is working end-to-end with validated inputs.

## Verified Metrics

- Total points: 8,858
- Public-access points: 5,301 (59.8%)
- Restricted points: 3,557 (40.2%)
- Median distance (all points): 27m
- Median distance (public-only): 39m
- Median openness penalty: +12m
- Severe-penalty estates (>=80m): 16
- Population proxy in severe-penalty estates: 31,590

## Completed

- [x] Rebuilt `scripts/validate_data.py` with required/optional dataset checks
- [x] Hardened `run_public_access_analysis.py` (robust flat parsing, reproducible map sampling)
- [x] Regenerated processed outputs and visualizations
- [x] Updated onboarding docs for teammates

## Next Work (Team)

- [ ] Build `proposed_hubs` file for top severe-penalty estates
- [ ] Add final slide deck in `presentation/`
- [ ] Add concise methodology + assumptions slide notes
- [ ] Rehearse 8-10 minute delivery

# Final Strategy (Approach 2)

## Core Thesis

Hong Kong has many recycling points in total, but low-value streams (especially textiles and glass) are highly locked behind non-public locations. This creates a practical access barrier for public housing residents and contributes to low recovery.

## What Is Strong and Defensible

- We measure lockout directly from `accessibilty_notes`.
- We quantify stream-specific distance barriers for all 241 public housing estates.
- We optimize hub placement with a transparent greedy max-coverage approach.
- We add equity-prioritized scoring (textile rescue + district vulnerability bonus).
- We produce a complete before/after impact table for each focus stream.

## Current Verified Story

- Textiles lockout is the worst (77.5%).
- Textiles has the largest access barrier (106 estates >500m).
- Fairness metric (textile population burden >500m) is 45.6%.
- 10 optimized hubs reduce textiles underserved estates from 106 to 83.
- 301,590 residents are moved out of the >500m textile-access zone.

## Visual Story Lock (Keep It Uncluttered)

Use exactly four core visuals:

1. Hero stream (textiles): baseline barrier and before/after improvement.
2. One fairness metric: textile population burden beyond 500m.
3. One optimization map: underserved estates + selected hub locations.
4. One sensitivity/assumption slide: payback range and modeling bounds.

## What We Will Not Overclaim

- We do not claim private-vs-public equity multipliers unless private-building coordinates are loaded.
- We label diversion and payback as modeled estimates based on explicit assumptions.
- We present assumptions in-slide (capture factors, gate fee, threshold definitions).

## Recommended 8-Slide Arc

1. Problem framing: lockout by material stream.
2. Evidence: access barriers by stream, focus on textiles.
3. Spatial pattern: district-level textile access burden.
4. Method: greedy placement objective and constraints.
5. Solution: 10 hub locations and coverage.
6. Impact: before/after estates and population.
7. Economics: modeled diversion and payback with assumptions.
8. Implementation: pilot sequence and measurement plan.

## Q&A-Ready Methodology Points

- Why 500m threshold: consistent underserved boundary in our analysis.
- Why 800m hub radius: practical walkable catchment for incremental service.
- Why textiles moves most: highest lockout + largest baseline underserved population.
- Why payback is wide: conservative-to-optimistic capture assumptions.

## Immediate Risk to Manage

If private-building geodata remains unavailable, remove all private comparator claims from final slides and keep the narrative centered on public-housing lockout and underserved reduction.

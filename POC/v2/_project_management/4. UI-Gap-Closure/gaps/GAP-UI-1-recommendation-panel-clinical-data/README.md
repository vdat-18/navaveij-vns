# GAP-UI-1 — Recommendation Panel Clinical Data

**Title:** Remove fabricated clinical alerts and wire package/pricing/gauge data from API
**Status:** Not started
**Wave:** 1

---

## Objective
Fix five critical bugs in `RecommendationPanel.tsx` where hardcoded/fabricated clinical data is displayed to physicians instead of actual API-sourced data, and where a runtime crash occurs on null reasoning trace.

## Scope
1. Remove `DEFAULT_CRITICAL_ALERTS` hardcoded fallback — replace with "Insufficient data" empty state when no valid signals are returned
2. Wire package name from `data.resolved_package.name` (not hardcoded "Diamond Plus Center")
3. Wire package price from `data.resolved_package.price_thb` (not hardcoded ฿15,000); render `null` as "Price TBD"
4. Add null guard: `data.reasoning_trace?.split('\n') ?? []` to prevent TypeError crash
5. Fix `ClinicalRiskGauge` to handle all four levels: `"High"` → 85%, `"Medium"` → 55%, `"Low"` → 25%, `"Critical"` → 95%

## Primary Files
`src/components/dashboard/RecommendationPanel.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20% · Hybrid Recommendation Engine 35%

# GAP-UI-6 — Error & Loading States

**Title:** Add inline error states to all screens; fix loading indicator placement; replace window.alert()
**Status:** Not started
**Wave:** 1

---

## Objective
Ensure all three screens provide meaningful user feedback on API failure, and that loading states appear in place of content rather than below it.

## Scope
1. Add `error` state + error message UI to `RecommendationPanel` — `if (!data && !loading)` must show error, not render `null`
2. Add `error` state to `PatientList` — distinguish network error ("Failed to load patients") from empty-results ("No patients found")
3. Add `error` state to `AccessMonitoringScreen` — show error message on initial load failure
4. Fix loading state placement in `TrendTimelineScreen` — render loading indicator in place of `<BiomarkerTrendGrid>`, not below it
5. Fix loading state placement in `AccessMonitoringScreen`
6. Replace `window.alert("Approval failed...")` in `RecommendationPanel` with inline error banner

## Primary Files
- `src/components/dashboard/RecommendationPanel.tsx`
- `src/components/dashboard/PatientList.tsx`
- `src/components/access-monitoring/AccessMonitoringScreen.tsx`
- `src/components/trend-timeline/TrendTimelineScreen.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%

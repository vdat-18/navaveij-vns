# GAP-UI-2 — Patient Context Header

**Title:** Wire patient demographics and analysis timestamp from API data
**Status:** Not started
**Wave:** 1

---

## Objective
Replace hardcoded patient demographics ("35 Yrs / Male / Asian") and analysis timestamp ("16 MAR 2026 • 18:43") with values sourced from the selected patient object and recommendation API response.

## Scope
1. Wire patient age, sex, and demographic summary from selected patient object fields
2. Wire "Last Analysis Run" timestamp from recommendation API response `metadata` object

## Primary Files
`src/app/page.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%

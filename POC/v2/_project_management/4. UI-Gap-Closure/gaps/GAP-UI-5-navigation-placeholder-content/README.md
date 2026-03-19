# GAP-UI-5 — Navigation & Placeholder Content

**Title:** Replace all placeholder labels and remove duplicate/incorrect navigation elements
**Status:** Not started
**Wave:** 1

---

## Objective
Remove all development-era placeholder content (Screen 1/2/3 labels, Sample Links, wrong routes) and fix duplicate navigation elements that currently render twice simultaneously.

## Scope
1. Replace "Screen 1", "Screen 2", "Screen 3" nav labels in `Sidebar.tsx` with: "Clinical Dashboard", "Trend & Timeline", "Access Monitoring"
2. Fix "Support" link in `Sidebar.tsx` — route to `/support` or remove; must not route to `/audit`
3. Remove duplicate nav links from `page.tsx` header (Governance, Trend & Timeline already in Sidebar)
4. Remove "Sample Link 1/2/3" placeholder footer content from `page.tsx`
5. Remove duplicate "Back to Summary" link from `TrendTimelineScreen.tsx` (already rendered by page layout)
6. Fix "No entities found" → "No patients found" in `PatientList.tsx`

## Primary Files
- `src/components/Sidebar.tsx`
- `src/app/page.tsx`
- `src/components/trend-timeline/TrendTimelineScreen.tsx`
- `src/components/dashboard/PatientList.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%

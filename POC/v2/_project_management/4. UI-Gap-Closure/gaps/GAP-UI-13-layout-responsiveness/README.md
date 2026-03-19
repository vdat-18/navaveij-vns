# GAP-UI-13 — Layout Responsiveness

**Title:** Fix sidebar-layout coupling and LiveMetricsBar display issues
**Status:** Not started
**Wave:** 2

---

## Objective
Fix the hardcoded `pl-64` layout coupling, improve the alert count display from an ambiguous slash-delimited string to labelled severity badges, and eliminate layout shift in the metrics bar loading state.

## Scope
1. Define `--sidebar-width: 16rem` CSS variable in `globals.css`; use it in `layout.tsx` (`padding-left: var(--sidebar-width)`) and `Sidebar.tsx` (`width: var(--sidebar-width)`) to decouple the values
2. Fix `LiveMetricsBar.tsx` alert counts: replace `"${critical}/${high}/${medium}/${low}"` string with four labelled, colour-coded severity badge elements (e.g., `🔴 2 Critical  🟠 5 High  🟡 3 Medium  🟢 1 Low`)
3. Fix `LiveMetricsBar.tsx` loading skeleton: match the structure of the loaded card (same grid layout) to prevent CLS on snapshot load

## Primary Files
- `src/app/layout.tsx`
- `src/app/globals.css`
- `src/components/access-monitoring/LiveMetricsBar.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%

# GAP-UI-11 — Chart Component Deduplication

**Title:** Extract shared chart tooltip, config constants, and clinical reference values
**Status:** Not started
**Wave:** 2

---

## Objective
Eliminate copy-pasted Recharts configuration and tooltip components across `BiomarkerCharts.tsx` and `BiomarkerTrendGrid.tsx`, and centralise clinical reference values.

## Scope
1. Create `src/components/charts/ChartTooltip.tsx` — shared, typed Recharts tooltip component; remove `CustomTooltip` from `BiomarkerCharts.tsx` and `TrendTooltip` from `BiomarkerTrendGrid.tsx`
2. Create `src/components/charts/chartConfig.ts` — exports shared `defaultCartesianGrid`, `defaultXAxisProps`, `defaultYAxisProps` constants; update both chart files to import these
3. Extract `BMI_TARGET = 23` and `BP_SYSTOLIC_NORMAL = 120` to `src/shared/clinicalConstants.ts` (or add to existing `src/shared/utils.ts`); remove hardcoded references from `TrendTimelineScreen.tsx` and `BiomarkerCharts.tsx`
4. Use `useId()` hook to scope SVG gradient ID in `BiomarkerCharts.tsx` (prevents document-level ID collision)
5. Fix `BiomarkerCharts.tsx` grid: `md:grid-cols-3` → `md:grid-cols-2`

## Primary Files
- `src/components/dashboard/BiomarkerCharts.tsx`
- `src/components/trend-timeline/BiomarkerTrendGrid.tsx`
- `src/components/charts/ChartTooltip.tsx` (new)
- `src/components/charts/chartConfig.ts` (new)
- `src/shared/clinicalConstants.ts` (new or update existing)

## Depends On
GAP-UI-9 — typed `ChartTooltipProps` interface needed for shared tooltip component

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%

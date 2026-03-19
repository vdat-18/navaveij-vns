# GAP-UI-9 — Type Safety & API Service

**Title:** Replace all `any` types with proper interfaces; add Axios interceptors and timeout
**Status:** Not started
**Wave:** 2

---

## Objective
Eliminate all `useState<any>` and untyped function parameters to restore TypeScript's compile-time safety, and centralise API error handling via Axios interceptors.

## Scope
1. Replace `useState<any>(null)` in `page.tsx` with `useState<Patient | null>(null)` (use existing `Patient` type)
2. Replace `useState<any>(null)` in `RecommendationPanel.tsx` with a typed `RecommendationResponse` interface derived from the API contract
3. Replace `useState<any>(null)` in `TrendTimelineScreen.tsx` with a typed biomarker data interface
4. Type `renderBoldText` parameter as `string` (not `any`)
5. Extract shared `ChartTooltipProps` interface for Recharts tooltip components (used by both `BiomarkerCharts` and `BiomarkerTrendGrid`)
6. Add return type annotations to all service functions in `api.ts`
7. Add Axios request interceptor for centralised error handling; add 30-second `timeout` to both Axios instances
8. Add comment to `api.ts` explaining `apiV1` (legacy `/api/v1/` routes) vs `apiV3` (contract API `/api/` routes)

## Primary Files
- `src/services/api.ts`
- `src/app/page.tsx`
- `src/components/dashboard/RecommendationPanel.tsx`
- `src/components/trend-timeline/TrendTimelineScreen.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
Pluggable AI Architecture + Data Standards 25%

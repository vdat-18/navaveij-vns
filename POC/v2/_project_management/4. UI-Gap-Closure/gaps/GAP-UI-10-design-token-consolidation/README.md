# GAP-UI-10 — Design Token Consolidation

**Title:** Remove dual CSS system and replace raw hex values with design tokens
**Status:** Not started
**Wave:** 2

---

## Objective
Eliminate the parallel `.navavej-*` CSS class system that duplicates Tailwind tokens, and replace all raw hex colour values with CSS variables or Tailwind tokens throughout the codebase.

## Scope
1. Audit `globals.css`: remove `.navavej-*` utility classes that duplicate existing Tailwind `navavej-*` utility tokens (keep only classes with unique structural behaviour like `glass-sidebar`)
2. Replace `#00ABC7` with `var(--color-navavej-teal)` or `text-navavej-teal` in all TSX/CSS files
3. Replace `#9D0A31` with `var(--color-navavej-red)` or `text-navavej-red` in all TSX/CSS files
4. Replace `#E9ECEF` with `var(--color-navavej-border)` in all TSX/CSS files
5. Standardise lab interpretation colours: replace `text-emerald-500` with `text-green-600` (or a new design token) for consistency
6. Apply full priority colour map across `ScreeningGapStatus.tsx`, `AnomalyAlertsPanel.tsx`, `RecommendationPanel.tsx`:
   - Red → `text-navavej-red`
   - Orange → `text-orange-500` (or add `navavej-orange` token)
   - Yellow → `text-yellow-500`
   - Green → `text-emerald-500`

## Primary Files
- `src/app/globals.css`
- `src/components/dashboard/LabResultsGrid.tsx`
- `src/components/trend-timeline/ScreeningGapStatus.tsx`
- `src/components/access-monitoring/AnomalyAlertsPanel.tsx`
- `src/components/dashboard/BiomarkerCharts.tsx`
- `src/components/trend-timeline/BiomarkerTrendGrid.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%

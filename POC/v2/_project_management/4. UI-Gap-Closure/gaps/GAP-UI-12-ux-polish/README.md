# GAP-UI-12 — UX Polish

**Title:** Remove dead code and fix minor UX inconsistencies
**Status:** Not started
**Wave:** 2

---

## Objective
Fix five small but visible UX and code-quality issues that collectively create a "messy" impression: a dead import, an unnecessary useMemo, misleading hover behaviour, alarm-fatigue animation, and a clinically misleading status fallback.

## Scope
1. Remove stray duplicate `import { Search } from "lucide-react"` at line 525 of `RecommendationPanel.tsx`
2. Replace `useMemo(() => [...], [])` wrapping a static array in `AuditLogSearchPanel.tsx` with a module-level `const`
3. Fix `hover:scale-[1.02]` + `cursor-default` inconsistency on lab result cards in `LabResultsGrid.tsx` — remove hover scale (card is non-interactive) or add `cursor-pointer` and an action
4. Restrict `animate-pulse` in `LabResultsGrid.tsx` to `interpretation === "H"` only — remove from `"L"` (low) values
5. Replace `"active"` hardcoded fallback for unknown clinical status in `ClinicalEventTimeline.tsx` with `"unknown"`

## Primary Files
- `src/components/dashboard/RecommendationPanel.tsx`
- `src/components/access-monitoring/AuditLogSearchPanel.tsx`
- `src/components/dashboard/LabResultsGrid.tsx`
- `src/components/trend-timeline/ClinicalEventTimeline.tsx`

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20%

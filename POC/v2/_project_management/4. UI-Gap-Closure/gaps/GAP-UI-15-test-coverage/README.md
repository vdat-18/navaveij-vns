# GAP-UI-15 — Test Coverage

**Title:** Set up Vitest + React Testing Library and write critical-path tests
**Status:** Not started
**Wave:** 3

---

## Objective
Establish a working test setup and write tests covering the six most critical paths identified in the audit, particularly the clinical data and security fixes from Wave 1.

## Scope
1. Install: `vitest`, `@vitest/ui`, `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom`, `@vitejs/plugin-react`, `jsdom`
2. Create `vitest.config.ts` with jsdom environment and `@testing-library/jest-dom` setup
3. Add scripts to `package.json`: `"test": "vitest run"`, `"test:watch": "vitest"`, `"test:coverage": "vitest run --coverage"`
4. Write tests:
   - `RecommendationPanel.test.tsx`: verify no fabricated alerts shown on empty/unexpected API response
   - `RecommendationPanel.test.tsx`: verify `ClinicalRiskGauge` renders correct position for High / Medium / Low / Critical
   - `PatientList.test.tsx`: verify error state shown on API failure (not empty-list state)
   - `RecommendationPanel.test.tsx`: verify approval call is made with correct (non-hardcoded) physician ID after GAP-UI-4
   - `AuditLogSearchPanel.test.tsx`: verify HTTPS message shown when `crypto.subtle` is undefined
   - `Sidebar.test.tsx`: verify `aria-current="page"` present on active link

## Primary Files
- `package.json`
- `vitest.config.ts` (new)
- `src/components/dashboard/RecommendationPanel.test.tsx` (new)
- `src/components/dashboard/PatientList.test.tsx` (new)
- `src/components/access-monitoring/AuditLogSearchPanel.test.tsx` (new)
- `src/components/Sidebar.test.tsx` (new)

## Depends On
GAP-UI-1 through GAP-UI-8 — tests verify Wave 1 fixes are correctly implemented

## Checkpoint Files
- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## TOR Reference
UX/Explainability (XAI) 20% · Security, Privacy & Audit 20%

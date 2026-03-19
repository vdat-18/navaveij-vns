# UI Gap Closure Plan
> **Date:** 2026-03-19 · **Total Gaps:** 15 (GAP-UI-1 through GAP-UI-15) · **Source Findings:** 53

## Planning Principles

1. **Clinical correctness first** — any gap that could display wrong clinical data to a physician is fixed before code quality gaps
2. **Wave sequencing enforced** — Wave 2 gaps do not begin until all Wave 1 gaps are closed and verified
3. **No silent fallbacks** — all placeholder/hardcoded data removed, not replaced with different placeholders
4. **Type safety gates Wave 2** — `any` types are the root cause of several Wave 1 crashes; fix types in Wave 2 prevents regression

## Target End State

After all 15 gaps are closed:
- Zero hardcoded clinical data displayed to users
- Sidebar visible with correct theming and active state
- All three screens show meaningful error states on API failure
- Auth context not exposed in client-side JS
- TypeScript compiles clean (`npx tsc --noEmit` zero errors)
- ESLint passes (`npm run lint` zero warnings)
- 6+ critical-path tests passing

## Workstreams

### WS-A — Visual & Clinical Correctness (Wave 1)
GAP-UI-1, GAP-UI-2, GAP-UI-3, GAP-UI-4, GAP-UI-5, GAP-UI-6, GAP-UI-7, GAP-UI-8

### WS-B — Code Quality & Consolidation (Wave 2)
GAP-UI-9, GAP-UI-10, GAP-UI-11, GAP-UI-12, GAP-UI-13

### WS-C — Hardening (Wave 3)
GAP-UI-14, GAP-UI-15

## Execution Steps

| Step | Gap | Description | Gate |
|---|---|---|---|
| 1 | GAP-UI-3 | Fix sidebar theming (glass-sidebar, teal-accent, remove dark class) | Visual: sidebar visible |
| 2 | GAP-UI-1 | Fix RecommendationPanel clinical data (alerts, package, price, gauge) | Visual: correct data displays |
| 3 | GAP-UI-2 | Fix patient context header (demographics, timestamp) | Visual: per-patient data |
| 4 | GAP-UI-5 | Fix navigation labels and remove all placeholder content | Visual: no "Screen N" labels |
| 5 | GAP-UI-6 | Add error and loading states to all three screens | Functional: error states visible |
| 6 | GAP-UI-4 | Fix auth security (move out of NEXT_PUBLIC, fix physician_id) | Security: DevTools check |
| 7 | GAP-UI-7 | Fix anomaly alert persistence | Functional: persist or disable |
| 8 | GAP-UI-8 | Add crypto.subtle guard | Functional: HTTPS message shown |
| **WAVE 1 GATE** | — | All Wave 1 items verified per Verification Plan | All checks pass |
| 9 | GAP-UI-9 | Replace all `any` types; add Axios interceptors and timeout | `tsc --noEmit` clean |
| 10 | GAP-UI-10 | Consolidate design tokens; remove dual CSS system | No raw hex in source |
| 11 | GAP-UI-11 | Extract shared chart components and clinical constants | No duplicate tooltip code |
| 12 | GAP-UI-12 | UX polish (dead import, useMemo, hover/pulse/status fixes) | Lint clean |
| 13 | GAP-UI-13 | Fix layout coupling and LiveMetricsBar display | Visual: alert badges show |
| **WAVE 2 GATE** | — | `tsc --noEmit` + `npm run lint` both clean | Both pass |
| 14 | GAP-UI-14 | Accessibility (aria, Image, ErrorBoundary) | Axe scan no violations |
| 15 | GAP-UI-15 | Test coverage setup and critical-path tests | `npm run test` passes |
| **WAVE 3 GATE** | — | All tests pass; Lighthouse accessibility ≥ 80 | Full pass |

## Gap-to-Task Mapping

| GAP-UI | Title | Wave | Source Gaps | Primary Files |
|---|---|---|---|---|
| GAP-UI-1 | Recommendation Panel Clinical Data | 1 | G-01, G-04, G-05, G-06, G-07 | `RecommendationPanel.tsx` |
| GAP-UI-2 | Patient Context Header | 1 | G-02, G-03 | `page.tsx` |
| GAP-UI-3 | Sidebar Theming | 1 | G-08, G-09, G-10 | `globals.css`, `layout.tsx`, `Sidebar.tsx` |
| GAP-UI-4 | Auth & Security | 1 | G-11, G-12, G-13, G-14 | `api.ts`, `access-monitoring/page.tsx`, `TrendTimelineScreen.tsx` |
| GAP-UI-5 | Navigation & Placeholder Content | 1 | G-15, G-16, G-17, G-18, G-23, G-24 | `Sidebar.tsx`, `page.tsx`, `TrendTimelineScreen.tsx`, `PatientList.tsx` |
| GAP-UI-6 | Error & Loading States | 1 | G-19, G-20, G-22 | `RecommendationPanel.tsx`, `PatientList.tsx`, `AccessMonitoringScreen.tsx`, `TrendTimelineScreen.tsx` |
| GAP-UI-7 | Anomaly Alert Persistence | 1 | G-21 | `AnomalyAlertsPanel.tsx`, `api.ts` |
| GAP-UI-8 | Crypto Audit Guard | 1 | G-25 | `AuditLogSearchPanel.tsx` |
| GAP-UI-9 | Type Safety & API Service | 2 | G-26, G-27, G-28, G-29, G-30, G-35, G-36 | `api.ts`, `page.tsx`, `RecommendationPanel.tsx`, `TrendTimelineScreen.tsx` |
| GAP-UI-10 | Design Token Consolidation | 2 | G-31, G-32, G-42, G-44 | `globals.css`, `LabResultsGrid.tsx`, `ScreeningGapStatus.tsx`, `AnomalyAlertsPanel.tsx` |
| GAP-UI-11 | Chart Component Deduplication | 2 | G-33, G-34, G-38, G-39 | `BiomarkerCharts.tsx`, `BiomarkerTrendGrid.tsx` |
| GAP-UI-12 | UX Polish | 2 | G-37, G-40, G-41, G-43, G-45 | `RecommendationPanel.tsx`, `AuditLogSearchPanel.tsx`, `LabResultsGrid.tsx`, `ClinicalEventTimeline.tsx` |
| GAP-UI-13 | Layout Responsiveness | 2 | G-46, G-47, G-48 | `layout.tsx`, `LiveMetricsBar.tsx` |
| GAP-UI-14 | Accessibility | 3 | G-49, G-50, G-51, G-52 | `Sidebar.tsx`, `PatientList.tsx`, `layout.tsx` |
| GAP-UI-15 | Test Coverage | 3 | (blanket) | `package.json`, `vitest.config.ts` (new), test files (new) |

## Risk Register

| Risk | Mitigation |
|---|---|
| GAP-UI-4 auth refactor may break local dev workflow | Keep `API_AUTH_MODE=disabled` path working in dev; only enforce server-side auth in staging |
| GAP-UI-7 — backend may not have an alert persistence endpoint | Implement disabled-with-tooltip state as the acceptable POC resolution |
| GAP-UI-9 type changes may expose previously hidden bugs | Fix bugs as they surface; do not suppress with type assertions |
| GAP-UI-15 tests may require mocking the BAML/API layer | Use `msw` or Axios mock adapters for test isolation |

## Definition of Done

A gap is closed when:
1. All scope items in its README are implemented
2. `_development_summary.md` updated with change description
3. `_lastest_test_results.md` updated with test evidence (manual verification or automated test output)
4. No new TypeScript errors introduced (`tsc --noEmit` still clean for that file)

## Closure Status

| GAP-UI | Title | Wave | Status |
|---|---|---|---|
| GAP-UI-1 | Recommendation Panel Clinical Data | 1 | Not started |
| GAP-UI-2 | Patient Context Header | 1 | Not started |
| GAP-UI-3 | Sidebar Theming | 1 | Not started |
| GAP-UI-4 | Auth & Security | 1 | Not started |
| GAP-UI-5 | Navigation & Placeholder Content | 1 | Not started |
| GAP-UI-6 | Error & Loading States | 1 | Not started |
| GAP-UI-7 | Anomaly Alert Persistence | 1 | Not started |
| GAP-UI-8 | Crypto Audit Guard | 1 | Not started |
| GAP-UI-9 | Type Safety & API Service | 2 | Not started |
| GAP-UI-10 | Design Token Consolidation | 2 | Not started |
| GAP-UI-11 | Chart Component Deduplication | 2 | Not started |
| GAP-UI-12 | UX Polish | 2 | Not started |
| GAP-UI-13 | Layout Responsiveness | 2 | Not started |
| GAP-UI-14 | Accessibility | 3 | Not started |
| GAP-UI-15 | Test Coverage | 3 | Not started |

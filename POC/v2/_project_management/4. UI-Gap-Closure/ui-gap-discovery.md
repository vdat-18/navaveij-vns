# UI Gap Discovery
> **Date:** 2026-03-19 · **Source:** Full code audit of `POC/v2/frontend/src/` (20 files)

## Gap Register

---

### GAP-UI-1 — Recommendation Panel Clinical Data
**Wave:** 1 | **Severity:** Critical | **Files:** `src/components/dashboard/RecommendationPanel.tsx`

#### Issues
| G# | Line | Issue | Root Cause |
|---|---|---|---|
| G-01 | L116–138 | Hardcoded `DEFAULT_CRITICAL_ALERTS` fallback displays fabricated "Hypertensive Crisis" and "High ASCVD Risk" alerts when API returns an unexpected shape | Developer placeholder never removed; no type-safe guard on normalization function |
| G-04 | L268 | Package name hardcoded as "Diamond Plus Center" for all patients | String literal copied from sample data, never wired to API response |
| G-05 | L272 | Package price hardcoded as ฿15,000 for all tiers | Same as above |
| G-06 | L324 | `data.reasoning_trace.split('\n')` throws `TypeError` if field is `null` or absent | No optional chaining; `data` is typed `any` so TypeScript does not catch it |
| G-07 | L78–79 | `ClinicalRiskGauge` only handles binary `"High"` vs everything-else; `"Medium"`, `"Low"`, `"Critical"` all show the same gauge position | Incomplete implementation; only two branches coded |

#### Fixed State
- `DEFAULT_CRITICAL_ALERTS` removed; component shows "Insufficient data" empty state when no valid signals
- Package name and price sourced from `data.resolved_package.name` and `data.resolved_package.price_thb`
- `data.reasoning_trace?.split('\n') ?? []` with null-safe fallback
- `ClinicalRiskGauge` maps `"High"` → 85%, `"Medium"` → 55%, `"Low"` → 25%, `"Critical"` → 95%

---

### GAP-UI-2 — Patient Context Header
**Wave:** 1 | **Severity:** Critical | **Files:** `src/app/page.tsx`

#### Issues
| G# | Line | Issue | Root Cause |
|---|---|---|---|
| G-02 | L153 | Patient demographics hardcoded as "35 Yrs / Male / Asian" for all patients | Placeholder copied from design mockup, never wired to data |
| G-03 | L162 | "Last Analysis Run" timestamp hardcoded as "16 MAR 2026 • 18:43" | Same — copied from mockup |

#### Fixed State
- Age, sex, and demographic data sourced from selected patient object fields
- Timestamp sourced from recommendation API response `metadata` object

---

### GAP-UI-3 — Sidebar Theming
**Wave:** 1 | **Severity:** Critical | **Files:** `src/app/globals.css`, `src/app/layout.tsx`, `src/components/Sidebar.tsx`

#### Issues
| G# | Location | Issue | Root Cause |
|---|---|---|---|
| G-08 | `Sidebar.tsx` L26 | `glass-sidebar` CSS class undefined — sidebar is fully transparent and unreadable | Class referenced but never defined in `globals.css` |
| G-09 | `Sidebar.tsx` L34, 52–56 | `teal-accent` Tailwind token undefined — active nav item has no highlight, all items look identical | Token referenced but not defined in `@theme` block |
| G-10 | `layout.tsx` L27 | `className="dark"` hardcoded on `<html>` but no dark-mode CSS exists — dark-palette sidebar colours render over white background | Developer enabled dark mode class without implementing dark CSS |

#### Fixed State
- `glass-sidebar` defined in `globals.css`: dark semi-transparent background with `backdrop-filter: blur()`
- `--color-teal-accent` added to `@theme` block as alias for `--color-navavej-teal`
- `className="dark"` removed from `<html>`; sidebar uses explicit colours instead of dark-mode palette

---

### GAP-UI-4 — Auth & Security
**Wave:** 1 | **Severity:** Critical | **Files:** `src/services/api.ts`, `src/app/access-monitoring/page.tsx`, `src/components/trend-timeline/TrendTimelineScreen.tsx`

#### Issues
| G# | Location | Issue | Root Cause |
|---|---|---|---|
| G-11 | `api.ts` L7–9 | Auth user ID, role, and scopes stored in `NEXT_PUBLIC_*` env vars — bundled into client JS, visible in DevTools; default is admin with full scopes | Convenience shortcut in POC setup never revisited |
| G-12 | `api.ts` L71 | `physician_id: "dr-admin-001"` hardcoded in every approval call — audit trail records wrong identity | Hardcoded from sample data |
| G-13 | `TrendTimelineScreen.tsx` L153 | Raw `patientToken` (API security token) displayed verbatim in UI header | Developer debugging output left in production view |
| G-14 | `access-monitoring/page.tsx` L8–9 | Role resolved at build-time from `NEXT_PUBLIC_AUTH_ROLE`; unknown roles silently fall back to `"admin"` | Missing validation; unsafe default |

#### Fixed State
- Auth context read from a Next.js server-side API route, not `NEXT_PUBLIC_*` vars
- `physician_id` sourced from authenticated user context
- `patientToken` removed from visible UI display
- Unknown roles show an access-denied state rather than silently escalating to admin

---

### GAP-UI-5 — Navigation & Placeholder Content
**Wave:** 1 | **Severity:** High | **Files:** `src/components/Sidebar.tsx`, `src/app/page.tsx`, `src/components/trend-timeline/TrendTimelineScreen.tsx`, `src/components/dashboard/PatientList.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-15 | `Sidebar.tsx` L63 | "Support" link routes to `/audit` (Governance page) — copy-paste error |
| G-16 | `page.tsx` L14 vs L64–75 | Duplicate nav links (Governance, Trend & Timeline) rendered simultaneously in page header and sidebar |
| G-17 | `Sidebar.tsx` L16–19 | Nav labels "Screen 1", "Screen 2", "Screen 3" — development placeholders in production |
| G-18 | `page.tsx` L187–196 | "Sample Link 1/2/3" footer placeholder content visible to clinical staff |
| G-23 | `TrendTimelineScreen.tsx` L167 | Duplicate "Back to Summary" link — already rendered by page layout |
| G-24 | `PatientList.tsx` L121 | "No entities found" — backend jargon; should be "No patients found" |

#### Fixed State
- "Support" link removed or routed to appropriate destination
- Duplicate nav links removed from page header (sidebar is the sole nav)
- Nav labels replaced: "Clinical Dashboard", "Trend & Timeline", "Access Monitoring"
- Footer placeholder removed or replaced with real links
- Duplicate "Back to Summary" link removed from `TrendTimelineScreen`
- "No entities found" → "No patients found"

---

### GAP-UI-6 — Error & Loading States
**Wave:** 1 | **Severity:** High | **Files:** `src/components/dashboard/RecommendationPanel.tsx`, `src/components/dashboard/PatientList.tsx`, `src/components/access-monitoring/AccessMonitoringScreen.tsx`, `src/components/trend-timeline/TrendTimelineScreen.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-19 | Multiple | No error states — API failures show blank screen or empty list with no user feedback |
| G-20 | `TrendTimelineScreen`, `AccessMonitoringScreen` | Loading indicator renders below content (after empty charts/tables), not in place of it |
| G-22 | `RecommendationPanel.tsx` L173 | `window.alert()` used for clinical failure feedback — blocks thread, inaccessible |

#### Fixed State
- All three screens have explicit `error` state that renders an inline error message
- `PatientList` distinguishes network error from empty-results state
- Loading indicator renders in place of content (conditional render, not appended below)
- `window.alert()` replaced with inline error banner

---

### GAP-UI-7 — Anomaly Alert Persistence
**Wave:** 1 | **Severity:** High | **Files:** `src/components/access-monitoring/AnomalyAlertsPanel.tsx`, `src/services/api.ts`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-21 | `AnomalyAlertsPanel.tsx` L36–44 | Acknowledge/Resolve buttons only update local React state — no API call; changes lost on refresh |

#### Fixed State
- If backend endpoint exists: API call made on acknowledge/resolve; local state updated only on success
- If backend endpoint does not exist: buttons disabled with "Persistence not yet supported" tooltip — no silent no-op

---

### GAP-UI-8 — Crypto Audit Guard
**Wave:** 1 | **Severity:** High | **Files:** `src/components/access-monitoring/AuditLogSearchPanel.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-25 | `AuditLogSearchPanel.tsx` L29–46 | `crypto.subtle.digest()` called with no availability check — silently fails in HTTP contexts (non-HTTPS) |

#### Fixed State
- `if (!crypto?.subtle)` guard added before use
- User-facing message "Hash verification requires a secure (HTTPS) connection" shown when unavailable
- Entire block wrapped in `try/catch` with inline error display

---

### GAP-UI-9 — Type Safety & API Service
**Wave:** 2 | **Severity:** High | **Files:** `src/services/api.ts`, `src/app/page.tsx`, `src/components/dashboard/RecommendationPanel.tsx`, `src/components/trend-timeline/TrendTimelineScreen.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-26 | `page.tsx` L33 | `useState<any>(null)` for selected patient |
| G-27 | `RecommendationPanel.tsx` L141 | `useState<any>(null)` for entire recommendation API response — all downstream accesses untyped |
| G-28 | `TrendTimelineScreen.tsx` L19 | `useState<any>(null)` for biomarker data |
| G-29 | `RecommendationPanel.tsx` L31 | `renderBoldText(text: any)` — accepts any type |
| G-30 | `BiomarkerCharts.tsx` + `BiomarkerTrendGrid.tsx` | Duplicate tooltip components both typed `any` for Recharts props |
| G-35 | `api.ts` | No Axios interceptors for error handling; no request timeout; all error handling duplicated per-component |
| G-36 | `api.ts` | `apiV1`/`apiV3` naming confusing (V3 variable name, `/api` path); no documentation |

#### Fixed State
- All `useState<any>` replaced with proper interfaces derived from existing `types/` files and API contracts
- `renderBoldText` typed as `(text: string) => React.ReactNode`
- Shared typed `ChartTooltipProps` interface extracted
- Axios interceptors added for centralised error handling; 30s timeout on both instances
- `apiV1`/`apiV3` rename or document with comments

---

### GAP-UI-10 — Design Token Consolidation
**Wave:** 2 | **Severity:** Medium | **Files:** `src/app/globals.css`, `src/components/dashboard/LabResultsGrid.tsx`, `src/components/trend-timeline/ScreeningGapStatus.tsx`, `src/components/access-monitoring/AnomalyAlertsPanel.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-31 | `globals.css` | Two parallel styling systems: `.navavej-*` custom CSS classes AND Tailwind `navavej-*` utilities doing the same thing |
| G-32 | Multiple chart files | Raw hex values `#00ABC7`, `#9D0A31`, `#E9ECEF` duplicated across `BiomarkerCharts`, `BiomarkerTrendGrid`, `AuditLogSearchPanel` instead of using tokens |
| G-42 | `LabResultsGrid.tsx` | Mixed tokens: `text-emerald-500` (raw Tailwind) vs `text-navavej-red` (design token) for lab interpretation colours |
| G-44 | `ScreeningGapStatus.tsx` | `"Orange"` → `text-orange-500` (raw Tailwind), `"Red"` → `text-navavej-red` (token); no `"Yellow"`/`"Green"` handling |

#### Fixed State
- Redundant `.navavej-*` CSS classes removed from `globals.css`; Tailwind tokens are the single source of truth
- All `#00ABC7` / `#9D0A31` / `#E9ECEF` replaced with `var(--color-navavej-teal)` / `var(--color-navavej-red)` / `var(--color-navavej-border)` or Tailwind tokens
- Lab interpretation colours standardised to design tokens
- Full priority colour map (Red/Orange/Yellow/Green) consistently applied across all components

---

### GAP-UI-11 — Chart Component Deduplication
**Wave:** 2 | **Severity:** Medium | **Files:** `src/components/dashboard/BiomarkerCharts.tsx`, `src/components/trend-timeline/BiomarkerTrendGrid.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-33 | Both chart files | Recharts `<CartesianGrid>`, `<XAxis>`, `<YAxis>` configurations copy-pasted verbatim |
| G-34 | 3 files | BMI reference `23` / `23.0` and BP reference `120` hardcoded in `TrendTimelineScreen`, `BiomarkerCharts` |
| G-38 | `BiomarkerCharts.tsx` L127 | SVG gradient `id="colorBmi"` is document-global — conflicts if component rendered twice |
| G-39 | `BiomarkerCharts.tsx` | `md:grid-cols-3` on a 2-chart layout — permanent empty column |

#### Fixed State
- `src/components/charts/ChartTooltip.tsx` created — shared typed tooltip component
- `src/components/charts/chartConfig.ts` created — shared Recharts axis/grid constants
- `src/shared/clinicalConstants.ts` updated with `BMI_TARGET = 23`, `BP_SYSTOLIC_NORMAL = 120`
- `useId()` hook used for SVG gradient ID scoping
- Grid corrected to `md:grid-cols-2`

---

### GAP-UI-12 — UX Polish
**Wave:** 2 | **Severity:** Medium | **Files:** `src/components/dashboard/RecommendationPanel.tsx`, `src/components/access-monitoring/AuditLogSearchPanel.tsx`, `src/components/dashboard/LabResultsGrid.tsx`, `src/components/trend-timeline/ClinicalEventTimeline.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-37 | `AuditLogSearchPanel.tsx` | `useMemo` wrapping a static constant array — provides zero benefit |
| G-40 | `LabResultsGrid.tsx` | `hover:scale-[1.02]` + `cursor-default` — hover transform implies interactivity that doesn't exist |
| G-41 | `LabResultsGrid.tsx` | `animate-pulse` on all non-normal labs (including low) — visual alarm fatigue |
| G-43 | `ClinicalEventTimeline.tsx` | `"active"` hardcoded as fallback for unknown clinical status — clinically misleading |
| G-45 | `RecommendationPanel.tsx` L525 | Stray duplicate `import { Search }` at bottom of file |

#### Fixed State
- Static array moved to module-level constant
- Lab cards: either `cursor-pointer` (if made interactive) or `hover:scale-[1.02]` removed
- `animate-pulse` restricted to `"H"` (high) interpretation only
- Unknown clinical status → `"unknown"` (not `"active"`)
- Duplicate import removed

---

### GAP-UI-13 — Layout Responsiveness
**Wave:** 2 | **Severity:** Medium | **Files:** `src/app/layout.tsx`, `src/components/access-monitoring/LiveMetricsBar.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-46 | `layout.tsx` L32 | `pl-64` hardcoded — coupled to `w-64` sidebar with no shared token |
| G-47 | `LiveMetricsBar.tsx` L21–24 | Alert counts rendered as `"2/5/3/1"` — visually ambiguous, no per-severity colour coding |
| G-48 | `LiveMetricsBar.tsx` | Loading state returns different card structure than loaded state — layout shift |

#### Fixed State
- Sidebar width defined as CSS variable `--sidebar-width: 16rem`; both `layout.tsx` and `Sidebar.tsx` reference it
- Alert counts displayed as labelled, colour-coded severity badges (Critical / High / Medium / Low)
- Loading skeleton matches loaded card structure to prevent CLS

---

### GAP-UI-14 — Accessibility
**Wave:** 3 | **Severity:** Low | **Files:** `src/components/Sidebar.tsx`, `src/components/dashboard/PatientList.tsx`, `src/app/layout.tsx`

#### Issues
| G# | Location | Issue |
|---|---|---|
| G-49 | `Sidebar.tsx` | No `aria-current="page"` on active link; no `aria-label` on `<aside>` |
| G-50 | `PatientList.tsx` | Search `<input>` missing `aria-label` / `<label>` |
| G-51 | `Sidebar.tsx` | Logo `<img>` without `width`/`height` — CLS; should use Next.js `<Image>` |
| G-52 | `layout.tsx` | No `ErrorBoundary` at root layout level |

#### Fixed State
- `aria-current="page"` on active nav link; `aria-label="Main navigation"` on `<aside>`
- Search input has `aria-label="Search patients"`
- `<img>` replaced with `<Image width={…} height={…} />`
- Root `<ErrorBoundary>` wraps `{children}` in layout

---

### GAP-UI-15 — Test Coverage
**Wave:** 3 | **Severity:** High | **Files:** `package.json`, `vitest.config.ts` (new), `src/**/*.test.tsx` (new)

#### Issues
The entire frontend has zero tests — no test runner, no testing libraries, no test files.

#### Fixed State
- Vitest + React Testing Library + `@testing-library/jest-dom` installed and configured
- Test scripts added to `package.json`: `"test": "vitest"`, `"test:ui": "vitest --ui"`, `"test:coverage": "vitest --coverage"`
- Critical path tests written:
  - Patient selection → recommendation load cycle
  - API failure → error state rendering (not blank screen)
  - Physician approve/reject flow records correct physician ID
  - `ClinicalRiskGauge` renders correct gauge position for High/Medium/Low/Critical
  - `normalizeCriticalAlerts` returns empty array (not fabricated data) on unexpected input
  - `crypto.subtle` guard shows HTTPS message when unavailable

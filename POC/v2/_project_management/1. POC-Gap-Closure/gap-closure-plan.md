# Gap-Closure Plan — POC v2 to v3 Demo Readiness

**Date:** 2026-03-18
**Input discovery:** `gap-discovery.md`  
**Goal:** Deliver a contract-compliant, demo-ready implementation aligned with v3 requirements and evaluation scoring.

---

## 1) Planning Principles

1. **Contract-first delivery**
   - Backend/API/output contracts are fixed before major UI work.

2. **Scoring-weighted execution**
   - Prioritize Hybrid/MCP (35%) and Pluggable/FHIR (25%) gaps first.

3. **Evidence-driven completion**
   - Every closed gap must have explicit verification output.

4. **Low-risk migration**
   - Add compatibility shims only when needed; avoid uncontrolled rewrites.

5. **Runtime-stable baseline before gap closure**
   - Resolve startup/config/test harness blockers in current POC before GAP-1 implementation work.

---

## 2) Target End State

At completion, the POC must demonstrate:

- Contract-compliant backend endpoints:
  - `POST /api/recommend`
  - `GET /api/timeline/{patient_token}`
  - `GET /api/monitoring-snapshot`
  - `GET /api/audit-logs`
- Stage-2-complete recommendation output aligned with schema contracts.
- Three usable screens matching v3 demo intent:
  - Screen 1: Individual Recommendation + XAI
  - Screen 2: Trend & Timeline
  - Screen 3: Access Monitoring
- Clear security evidence:
  - Auth gate behavior, masking path, audit integrity, role-aware monitoring access.
- Repeatable verification checklist and baseline-vs-final comparison.

---

## 3) Workstream Overview

## WS-A — Contract Alignment (Backend Core)

**Covers gaps:** GAP-1, GAP-2, GAP-3  
**Priority:** P0 (must finish first)

Deliverables:
- v3-aligned API route surface and request/response shapes.
- Stage-2 assembly layer for recommendation output.
- MCP parameter normalization policy (`patient_token` boundary consistency).

Acceptance checks:
- Endpoint smoke tests pass for all 4 required routes.
- `/api/recommend` response includes required Stage-2 fields.
- Tool-call path is traceable and consistent for token handling.

## WS-B — Screen Contract Implementation

**Covers gaps:** GAP-4, GAP-5  
**Priority:** P1 (after WS-A baseline)

Deliverables:
- Screen 2 with timeline + biomarker contract behavior.
- Screen 3 with monitoring snapshot, anomaly display, audit search, hash verification UI.

Acceptance checks:
- Screen 2 renders contract-required sections and data bindings.
- Screen 3 renders KPIs/anomalies/audit filters and verifies hash check.

## WS-C — Security & Standards Evidence Hardening

**Covers gaps:** GAP-6, GAP-7  
**Priority:** P1/P2 (in parallel with WS-B where possible)

Deliverables:
- Entry-point auth scope verification behavior for recommendation flow.
- Role-aware access behavior for monitoring resources.
- Visible terminology mapping evidence (LOINC/SNOMED/ICD) in required views.

Acceptance checks:
- Unauthorized requests are rejected with safe response behavior.
- Monitoring access paths respect role constraints.
- Terminology fields are present end-to-end where contract expects them.

## WS-D — Reliability & Verification

**Covers gaps:** GAP-8, GAP-9  
**Priority:** P2 (continuous; finalize at end)

Deliverables:
- Frontend compile/runtime issues resolved.
- Contract-focused smoke/integration validation pack.
- Closure evidence package in project-management files.

Acceptance checks:
- Frontend builds/runs without critical route failures.
- Verification suite demonstrates all required endpoint/screen contracts.

---

## 4) Execution Sequence

## Step 0 — Baseline and Branch Hygiene

- Re-run baseline checks from `gaps/GAP-0-baseline-run/README.md`.
- Capture current failures in `gaps/_lastest_test_results.md`.
- Confirm starting point before edits.

## Step 0.5 — POC Stabilization Gate (must pass before GAP-1)

### Objective

Ensure `POC/v2` runs reliably in current architecture without introducing v3 gap-closure changes yet.

### Required fixes

1. **Environment loading consistency**
   - Ensure runtime and all test entrypoints load `.env` in a consistent way.
   - Remove mismatch where one script succeeds (`load_dotenv`) and another fails due missing `LLM_*`.

2. **Port/run isolation**
   - Standardize dev execution to use an explicit port for this POC workspace.
   - Prevent collisions with other local Navaveij services.

3. **Test harness alignment**
   - Normalize Python module path behavior for tests/scripts.
   - Eliminate collection/runtime failures caused by missing module paths.
   - Convert async test execution into a consistent runnable mode in CI/local.

4. **Fixture and identifier alignment**
   - Align test patient IDs and script assumptions with actual dataset shape (`id_*` registry IDs or mapped test fixtures).
   - Remove stale assumptions such as hardcoded `P001` in health checks used as success criteria.

5. **Safety and script hygiene**
   - Remove/replace non-baseline scripts that call external model endpoints with hardcoded credentials.
   - Keep only local POC verification scripts in baseline execution path.

### Stabilization acceptance gate

- API start and smoke tests pass on designated POC port.
- Recommendation endpoint succeeds for at least one valid in-repo patient fixture.
- Baseline test command set runs without environment-path surprises.
- Remaining failures, if any, are deterministic and documented with owner and next action.

Only after this gate is met should GAP-1/GAP-2 contract changes begin.

## Step 1 — Backend Contract Lock (WS-A)

- Introduce/align required v3 endpoints.
- Implement Stage-2 response assembler and required metadata shaping.
- Normalize token parameter usage in MCP workflow boundary.
- Add minimal contract tests for new endpoints.

Gate to proceed:
- All required routes return expected status and base schema.

## Step 2 — Screen 1 Contract Stabilization (WS-A/WS-B bridge)

- Ensure Screen 1 uses Stage-2 fields and renders key contract panels.
- Validate tier comparison, confidence, high-alert object, and XAI rendering.

Gate to proceed:
- Screen 1 can run end-to-end against aligned backend without fallback hacks.

## Step 3 — Screen 2 and Screen 3 Delivery (WS-B + WS-C)

- Build Screen 2 timeline/trend bindings to timeline and signal sources.
- Build Screen 3 monitoring dashboard bindings and audit search.
- Add hash-verify interaction and role-awareness displays.
- Surface terminology mapping evidence where required.

Gate to proceed:
- Both screens load from real API responses and meet core interaction criteria.

## Step 4 — Security/Compliance Hardening (WS-C)

- Add/clarify auth scope checks at entrypoint and role restrictions for monitoring APIs.
- Ensure audit payload and filtering semantics satisfy required dimensions.

Gate to proceed:
- Security behavior is demonstrable via positive and negative test paths.

## Step 5 — Reliability, Regression, and Demo Polish (WS-D)

- Fix frontend import/runtime defects and remove dead paths.
- Execute full smoke flow across all 3 screens.
- Produce final closure summary and outstanding-risk list.

Completion gate:
- All high-severity gaps closed or explicitly accepted with mitigation.

---

## 5) Gap-to-Task Mapping

| Gap | Closure Task | Depends On | Exit Evidence |
|---|---|---|---|
| GAP-1 | Align API routes/contracts | Baseline | Endpoint smoke pass |
| GAP-2 | Build Stage-2 assembler/validator | GAP-1 | Schema field checklist pass |
| GAP-3 | Normalize MCP token contract | GAP-1 | Tool call trace consistency |
| GAP-4 | Implement Screen 2 contract | GAP-1/2 | Screen 2 functional checklist |
| GAP-5 | Implement Screen 3 contract | GAP-1/2 | Screen 3 functional checklist |
| GAP-6 | Add auth/RBAC evidence path | GAP-1 | Unauthorized/role tests pass |
| GAP-7 | Expose terminology mappings | GAP-4/5 | Mapping fields visible in UI/API |
| GAP-8 | Fix frontend reliability defects | Continuous | Build and navigation stability |
| GAP-9 | Build closure verification pack | All | Final smoke + regression report |
| GAP-10 | Implement backend TTL cache | GAP-1 | Cache test suite pass; loader paths verified |

---

## 6) Deliverable Artifacts

During execution, maintain these files:

- `gaps/_discovery.md`
  - Findings during implementation and architecture decisions.
- `gaps/_lastest_test_results.md`
  - Raw outputs for endpoint tests, frontend checks, and regressions.
- `gaps/_development_summary.md`
  - Interpreted status, closed gaps, open risks, and next actions.

Optional per-gap folders (recommended for traceability):
- `gaps/GAP-1-api-contract/`
- `gaps/GAP-2-stage2-schema/`
- `gaps/GAP-3-mcp-token-alignment/`
- `gaps/GAP-4-screen2-trend-timeline/`
- `gaps/GAP-5-screen3-access-monitoring/`
- `gaps/GAP-6-security-rbac/`
- `gaps/GAP-7-terminology-evidence/`
- `gaps/GAP-8-frontend-reliability/`
- `gaps/GAP-9-verification-pack/`

---

## 7) Risks and Mitigations

1. **Contract churn risk**
   - Mitigation: freeze route/schema interfaces before broad UI changes.

2. **Scope creep from “nice-to-have” UI polish**
   - Mitigation: only implement fields/interactions tied to acceptance criteria first.

3. **Auth/RBAC uncertainty for full production behavior**
   - Mitigation: implement POC-safe enforcement stubs with explicit assumptions documented.

4. **Data readiness mismatch for timeline/monitoring**
   - Mitigation: use contract-shaped seed fixtures with strict typing and schema checks.

---

## 8) Definition of Done

The gap-closure effort is complete when:

- All Critical and High gaps (GAP-1 through GAP-6) are closed with test evidence.
- Medium gaps (GAP-7 through GAP-9) are closed or explicitly accepted with documented mitigation.
- End-to-end demo run works across all 3 screens using aligned API contracts.
- Gap artifacts are up to date and can be used as a handoff packet for final evaluation prep.

---

## 9) Closure Status (as of 2026-03-18)

| Gap | Status | Test Evidence |
|---|---|---|
| GAP-0 | Complete | 6 passed (stabilization gate) |
| GAP-1 | Complete | 6 contract + 12 regression |
| GAP-2 | Complete | 6 contract + 12 regression |
| GAP-3 | Complete | 7 contract + 13 regression |
| GAP-4 | Complete | 2 timeline + 9 contract + 17 regression |
| GAP-5 | Complete | 14 access-monitoring + 22 regression |
| GAP-6 | Complete | 23 security tests |
| GAP-7 | Complete | 22 targeted tests |
| GAP-8 | In verification | 5 reliability tests passed; npm build blocked in runtime |
| GAP-9 | In verification | 34 deterministic passed; 40 full regression; npm build blocked in runtime |
| GAP-10 | Complete | 16 cache tests passed (Phase 1-3 including /api/recommend cache) |

All Critical and High gaps (GAP-1 through GAP-6) are closed with test evidence.
Medium gaps (GAP-7 through GAP-9) closed or documented with explicit mitigation.
GAP-10 (enhancement) fully delivered including Phase 3 recommendation-response cache.
Frontend build gate remains environment-blocked (npm/Node unavailable in AI session runtime).

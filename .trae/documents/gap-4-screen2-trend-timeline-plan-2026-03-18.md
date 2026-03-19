# GAP-4 Implementation Plan — Screen 2 Trend & Timeline Contract

## Summary

Implement GAP-4 by delivering a dedicated Screen 2 (Trend & Timeline) that is contract-aligned with v3 specs, including:
- 6 biomarker trend charts
- event timeline track
- screening gap status panel
- shared time-range filter behavior

This plan includes backend timeline contract fixes, MCP tool addition, frontend screen implementation, and verification evidence updates.

## Current State Analysis

- GAP-4 is not started in:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-4-screen2-trend-timeline/README.md`
- Current frontend has no dedicated Screen 2 route; dashboard currently renders recommendation-first flow in:
  - `POC/v2/frontend/src/app/page.tsx`
- Existing chart area in recommendation panel is partial and does not match Screen 2 contract:
  - `POC/v2/frontend/src/components/dashboard/RecommendationPanel.tsx`
  - `POC/v2/frontend/src/components/dashboard/BiomarkerCharts.tsx`
- `/api/timeline/{patient_token}` currently returns audit-derived `timeline_events`, not event-timeline contract arrays:
  - `POC/v2/backend/src/api/routes/contracts.py`
- MCP server currently registers 4 tools and does not expose `get_patient_event_timeline`:
  - `POC/v2/backend/src/mcp_server/server.py`

## Assumptions & Decisions

- Deliverable target for GAP-4 is a dedicated Screen 2 route and components, not incremental embedding in Screen 1.
- `patient_token` remains the canonical key for all new timeline calls (aligned with GAP-3).
- `/api/v1` compatibility remains unchanged in GAP-4; this gap uses `/api` contract routes.
- Timeline source will be contract-shaped data served by backend endpoint and backed by MCP timeline tool path.

## Proposed Changes

### 1) Add MCP timeline tool and token-based data retrieval path

**Files**
- Create: `POC/v2/backend/src/mcp_server/tools/patient_event_timeline.py`
- Update: `POC/v2/backend/src/mcp_server/server.py`
- Update: `POC/v2/backend/src/mcp_server/utils.py`

**What**
- Implement `get_patient_event_timeline(patient_token, patient_id=None)` tool.
- Return contract-shaped payload with:
  - `timeline_span`
  - `diagnoses`
  - `hospitalizations`
  - `significant_lab_events`
  - `screening_procedure_history`
  - `medication_changes`
  - `pipeline_run_id`, `computed_at`

**Why**
- Screen 2 contract depends on event-timeline data, and current backend response shape is insufficient.

**How**
- Use existing signal store/generated assets + registry mapping utilities.
- Keep optional `patient_id` adapter argument for transition safety while token remains primary.

### 2) Align `/api/timeline/{patient_token}` response with event contract

**Files**
- Update: `POC/v2/backend/src/api/routes/contracts.py`

**What**
- Replace current audit-derived `timeline_events` response path with full event-timeline contract response.
- Keep `patient_token` keyed route behavior.

**Why**
- GAP-4 requires timeline payload contract compliance to support Screen 2 rendering.

**How**
- Call new MCP timeline tool or shared loader path from endpoint.
- Preserve HTTP semantics:
  - valid token: contract payload
  - invalid token: 404

### 3) Add frontend timeline API client and types

**Files**
- Update: `POC/v2/frontend/src/services/api.ts`
- Create: `POC/v2/frontend/src/types/timeline.ts` (or existing shared type location)

**What**
- Add typed `getTimeline(patientToken)` function for `/api/timeline/{patient_token}`.
- Add strong types for event-timeline contract arrays and timeline span.

**Why**
- Frontend Screen 2 implementation needs typed bindings and explicit API entrypoint.

**How**
- Reuse existing axios client split (`apiV1`, `apiV3`) and token-first conventions.

### 4) Create dedicated Screen 2 route and core UI structure

**Files**
- Create: `POC/v2/frontend/src/app/trend-timeline/page.tsx`
- Create: `POC/v2/frontend/src/components/trend-timeline/TrendTimelineScreen.tsx`
- Create: `POC/v2/frontend/src/components/trend-timeline/BiomarkerTrendGrid.tsx`
- Create: `POC/v2/frontend/src/components/trend-timeline/ClinicalEventTimeline.tsx`
- Create: `POC/v2/frontend/src/components/trend-timeline/ScreeningGapStatus.tsx`
- Update: `POC/v2/frontend/src/app/page.tsx` (navigation link to Screen 2)

**What**
- Implement Panels B/C/D/E from Screen 2 spec:
  - patient header strip
  - 6 biomarker trend charts with LOINC labels
  - timeline event track by category
  - screening gap status list

**Why**
- GAP-4 acceptance criteria explicitly require dedicated trend/timeline screen behavior.

**How**
- Reuse existing style system and charting pattern from current dashboard components.
- Feed Screen 2 from selected patient token + timeline API.

### 5) Implement shared time-range filtering behavior for charts/timeline

**Files**
- Update: newly created Screen 2 components above

**What**
- Add common range selector (e.g., 1y/3y/5y/all or custom years).
- Ensure all chart panels and timeline track react to same filter window.

**Why**
- Screen-2 contract and UX criteria require synchronized longitudinal exploration behavior.

**How**
- Maintain filter state in Screen 2 container and pass filtered datasets to child components.

### 6) Strengthen verification tests for GAP-4 contract and behavior

**Files**
- Update: `POC/v2/scripts/tests/test_api_contract_routes.py`
- Add: `POC/v2/scripts/tests/test_timeline_contract_payload.py`
- Add: frontend test file(s) for Screen 2 rendering/filter behavior if framework is present

**What**
- Add field-level assertions for timeline contract response keys/arrays.
- Add behavior checks for token-based timeline retrieval.
- Keep regression checks for existing GAP-1/2/3 routes.

**Why**
- GAP-4 closure requires evidence beyond route existence.

**How**
- Use deterministic fixtures/mocked paths where needed for stable test outcomes.

### 7) Update GAP-4 checkpoint artifacts with implementation evidence

**Files**
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-4-screen2-trend-timeline/_discovery.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-4-screen2-trend-timeline/_lastest_test_results.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-4-screen2-trend-timeline/_development_summary.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-4-screen2-trend-timeline/README.md`

**What**
- Record decisions, contract mapping evidence, and verification outputs.

**Why**
- Required for gap closure traceability and downstream handoff.

## Verification Steps

1. Backend contract checks:
   - `uv run pytest scripts/tests/test_api_contract_routes.py -v`
   - `uv run pytest scripts/tests/test_timeline_contract_payload.py -v` (new)
2. Full backend regression:
   - `uv run pytest scripts/tests -v`
3. Frontend validation:
   - install dependencies if missing
   - run build/type checks
   - manual screen smoke for Screen 2 route:
     - chart panels render for selected patient
     - timeline events render by type
     - screening gap panel values appear
     - time-range selector updates all relevant panels
4. Final artifact update:
   - capture command outputs and contract evidence in GAP-4 checkpoint files.

## Risks & Mitigations

- **Risk:** Timeline source data does not fully match event contract fields.
  - **Mitigation:** build mapping/normalization layer in MCP timeline tool with explicit defaults.
- **Risk:** UI complexity introduces regressions in Screen 1 experience.
  - **Mitigation:** isolate Screen 2 into dedicated route/components and avoid broad refactors.
- **Risk:** frontend environment constraints (missing `next`) block local build.
  - **Mitigation:** document dependency prerequisite and continue backend verification independently.

## Out of Scope

- Screen 3 monitoring implementation (GAP-5).
- Security/RBAC enforcement changes (GAP-6).
- Full verification pack finalization (GAP-9).

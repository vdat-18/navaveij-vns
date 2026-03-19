# Discovery

Status: In progress

## Scope executed

- Added contract-backed timeline data path for Screen 2.
- Added dedicated Screen 2 frontend route and UI components.
- Added token-first API endpoints to support trend + timeline + screening panels.
- Added timeline contract test coverage and regression verification.

## Backend contract decisions

- Implemented MCP tool `get_patient_event_timeline(patient_token, patient_id=None)`.
- Updated `/api/timeline/{patient_token}` to return event-timeline contract shape:
  - `timeline_span`
  - `diagnoses`
  - `hospitalizations`
  - `significant_lab_events`
  - `screening_procedure_history`
  - `medication_changes`
  - `pipeline_run_id`
  - `computed_at`
- Added supporting Screen 2 API endpoints:
  - `GET /api/biomarker-trends/{patient_token}`
  - `GET /api/screening-gaps/{patient_token}`

## Frontend implementation decisions

- Created dedicated page route: `/trend-timeline`.
- Built Screen 2 as isolated components:
  - trend grid (6 charts)
  - clinical event timeline
  - screening gap status panel
- Added shared time-range selector driving chart and timeline filtering.
- Preserved existing summary and governance routes.

## Files changed

- `backend/src/mcp_server/tools/patient_event_timeline.py` (new)
- `backend/src/mcp_server/utils.py`
- `backend/src/mcp_server/server.py`
- `backend/src/api/routes/contracts.py`
- `frontend/src/types/timeline.ts` (new)
- `frontend/src/services/api.ts`
- `frontend/src/app/trend-timeline/page.tsx` (new)
- `frontend/src/components/trend-timeline/TrendTimelineScreen.tsx` (new)
- `frontend/src/components/trend-timeline/BiomarkerTrendGrid.tsx` (new)
- `frontend/src/components/trend-timeline/ClinicalEventTimeline.tsx` (new)
- `frontend/src/components/trend-timeline/ScreeningGapStatus.tsx` (new)
- `frontend/src/app/page.tsx`
- `scripts/tests/test_api_contract_routes.py`
- `scripts/tests/test_timeline_contract_payload.py` (new)

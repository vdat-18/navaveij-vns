# Discovery

Status: In progress

## Scope executed

- Implemented token-first contract behavior from API boundary through MCP tool inputs.
- Retained `/api/v1` compatibility with explicit id-to-token adapter behavior.
- Migrated frontend recommendation call to token-first `/api/recommend`.

## Token alignment decisions

- Canonical boundary key is now `patient_token` for:
  - `/api/recommend` request payload
  - workflow MCP calls (`get_hard_constraints`, `get_clinical_signals`, `get_biomarker_trends`, `get_program_ruleset`)
  - MCP tool primary function parameter
- Transitional compatibility retained:
  - MCP tools still accept optional `patient_id` adapter field.
  - `/api/v1/clinical/recommend` remains id-based input and resolves token before orchestration.

## Implementation details

- Added centralized resolver utilities in `api/routes/patients.py`:
  - `find_patient_by_id`
  - `find_patient_by_token`
  - `resolve_patient_id`
  - `resolve_patient_token`
- Added MCP-side registry/token utilities in `mcp_server/utils.py` and upgraded signal record loader to accept token-first input.
- Updated workflow MCP calls to pass both `patient_token` (primary) and `patient_id` (adapter) for traceability.
- Updated orchestrator to resolve token automatically when only id is provided.
- Updated frontend API client to call:
  - `/api/recommend` with `{ patient_token }`
  - keep v1 clients for patients/approve/audit compatibility paths.

## Files changed

- `backend/src/api/routes/patients.py`
- `backend/src/api/routes/clinical.py`
- `backend/src/api/routes/contracts.py`
- `backend/src/mcp_server/utils.py`
- `backend/src/mcp_server/tools/hard_constraints.py`
- `backend/src/mcp_server/tools/clinical_signals.py`
- `backend/src/mcp_server/tools/biomarker_trends.py`
- `backend/src/mcp_server/tools/program_ruleset.py`
- `backend/src/services/workflows/clinical.py`
- `backend/src/services/orchestrator.py`
- `frontend/src/services/api.ts`
- `frontend/src/components/dashboard/RecommendationPanel.tsx`
- `frontend/src/app/page.tsx`
- `scripts/tests/test_api_contract_routes.py`
- `scripts/tests/workflows/test_clinical_workflow.py`
- `scripts/test_orchestrator.py`

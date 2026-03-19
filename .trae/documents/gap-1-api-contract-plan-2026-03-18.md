# GAP-1 Implementation Plan — API Contract Alignment

## Summary

Implement GAP-1 by adding a v3-aligned `/api/*` contract surface in `POC/v2` backend while keeping existing `/api/v1/*` routes active for compatibility.  
This round covers backend route implementation plus contract-focused backend verification, without frontend migration.

## Current State Analysis

- GAP-1 is marked not started and blocked on missing v3 endpoints in:
  - `/Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-1-api-contract/README.md`
- Existing backend surface is mounted only under `/api/v1`:
  - `backend/src/api/main.py` includes routers for `/api/v1/patients` and `/api/v1/clinical`, plus `/health`.
- Existing clinical routes are:
  - `POST /api/v1/clinical/recommend`
  - `POST /api/v1/clinical/approve`
  - `GET /api/v1/clinical/audit`
- Required GAP-1 target routes are:
  - `POST /api/recommend`
  - `GET /api/timeline/{patient_token}`
  - `GET /api/monitoring-snapshot`
  - `GET /api/audit-logs`
- Baseline evidence confirms these v3 routes currently return `404`.
- Stabilization gate from GAP-0 is complete, so route migration work can begin.

## Assumptions & Decisions

- Scope for this round: backend + contract tests only.
- Backward compatibility decision: keep `/api/v1/*` routes active while introducing `/api/*`.
- GAP-1 focuses on route contract alignment and request/response wiring, not full GAP-2 Stage-2 schema completeness.
- Timeline and monitoring responses may use contract-shaped placeholder data where real pipeline integration is not yet available, but payload structure and status behavior must match documented expectations.
- Audit logs endpoint will expose filtering/query behavior consistent with contract docs using existing audit service data.

## Proposed Changes

### 1) Add new v3 contract router module

**Files**
- Create: `POC/v2/backend/src/api/routes/contracts.py`

**What**
- Add FastAPI endpoints:
  - `POST /recommend`
  - `GET /timeline/{patient_token}`
  - `GET /monitoring-snapshot`
  - `GET /audit-logs`
- Implement request/response models in this module or shared schema import if already defined.
- Wire `patient_token` boundary input and normalize internally to current workflow inputs where needed.

**Why**
- Introduces the required route surface without breaking existing `/api/v1` clients.

**How**
- Reuse existing orchestrator/workflow service calls for recommendation path.
- Add robust token resolution helper:
  - Accept `patient_token` values that map to existing registry IDs.
  - Return clear 404/422 behaviors for invalid tokens.
- Use existing audit logger query capability for `/audit-logs`.
- Source timeline/monitoring data from available in-repo assets or service layer adapters with deterministic output shape.

### 2) Mount `/api` contract router in app entrypoint

**Files**
- Update: `POC/v2/backend/src/api/main.py`

**What**
- Include the new router under prefix `/api`.
- Keep current `/api/v1/patients` and `/api/v1/clinical` includes unchanged.

**Why**
- Enables dual-surface operation (new contract + legacy compatibility).

**How**
- Add a third `include_router(...)` call for contract routes.
- Ensure tags and startup behavior remain consistent.

### 3) Add/adjust backend schemas for contract responses

**Files**
- Update likely one or more of:
  - `POC/v2/shared/*.py`
  - `POC/v2/backend/src/api/routes/contracts.py` (local pydantic models)

**What**
- Define minimal contract-compliant models for:
  - Recommend response envelope
  - Timeline response
  - Monitoring snapshot response
  - Audit logs list with filters metadata

**Why**
- Stabilizes API signatures and reduces accidental response drift.

**How**
- Prefer existing schema location/pattern already used by backend.
- Keep fields aligned with v3 contract docs and current available data.

### 4) Add contract-focused tests for new `/api` routes

**Files**
- Create: `POC/v2/scripts/tests/test_api_contract_routes.py`
- Update (if needed): `POC/v2/scripts/tests/conftest.py`

**What**
- Add tests that validate:
  - Route existence and non-404 behavior.
  - Basic status codes for valid and invalid token scenarios.
  - Response contains required top-level contract keys.
  - Audit logs endpoint handles query filters safely.

**Why**
- GAP-1 exit evidence requires endpoint smoke pass.

**How**
- Follow existing script test conventions already stabilized in GAP-0.
- Reuse shared fixtures/env loading already provided in `scripts/tests/conftest.py`.

### 5) Update GAP-1 tracking artifacts with evidence

**Files**
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-1-api-contract/_discovery.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-1-api-contract/_lastest_test_results.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-1-api-contract/_development_summary.md`

**What**
- Record implementation decisions, known constraints, and command/test outputs.
- Mark GAP-1 status progress with pass/fail evidence and remaining risks.

**Why**
- Maintains continuity with the existing gap-closure process and handoff expectations.

## Verification Steps

1. Start backend on designated POC port (with preflight check from GAP-0 runbook).
2. Run contract tests:
   - `uv run pytest scripts/tests/test_api_contract_routes.py -v`
3. Run broader stabilized test command to detect regressions:
   - `uv run pytest scripts/tests -v`
4. Manual smoke:
   - `POST /api/recommend` with valid token returns success envelope.
   - Invalid `patient_token` returns expected error code.
   - `GET /api/timeline/{patient_token}` returns contract-shaped timeline payload.
   - `GET /api/monitoring-snapshot` returns contract-shaped monitoring payload.
   - `GET /api/audit-logs` returns list payload with query handling.
5. Confirm legacy compatibility:
   - Existing `/api/v1/clinical/recommend` still works for baseline patient.

## Out of Scope (This Round)

- Frontend migration from `/api/v1` to `/api`.
- Full GAP-2 Stage-2 schema completion details beyond minimum stable envelope.
- GAP-3 token policy final normalization across all MCP tool interfaces.

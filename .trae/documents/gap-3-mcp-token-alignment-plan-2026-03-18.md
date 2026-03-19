# GAP-3 Implementation Plan — MCP Token Contract Alignment

## Summary

Implement GAP-3 as an end-to-end token-first migration across backend, MCP tool interfaces, frontend API usage, and test/script harnesses.  
`patient_token` becomes the canonical boundary key, while `/api/v1` remains temporarily available through an explicit adapter path.

## Current State Analysis

- GAP-3 is currently not started:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-3-mcp-token-alignment/README.md`
- API surface is mixed:
  - `/api/recommend` already accepts `patient_token`.
  - `/api/v1/clinical/recommend` still accepts `patient_id`.
- Workflow and MCP calls are still `patient_id` based:
  - `backend/src/services/workflows/clinical.py` calls all MCP tools with `{"patient_id": ...}`.
  - MCP tools in `backend/src/mcp_server/tools/*.py` currently define `patient_id` arguments.
- Data records contain both identifiers, but signal loading utilities are id-oriented:
  - `backend/src/mcp_server/utils.py` loads records by `patient_id`.
- Frontend still calls legacy v1 id-based routes:
  - `frontend/src/services/api.ts` uses `/api/v1/clinical/recommend` with `{ patient_id }`.

## Assumptions & Decisions

- Scope decision (confirmed): full end-to-end GAP-3 migration in this round.
- Legacy behavior decision (confirmed): keep `/api/v1` active via adapter for compatibility.
- Canonical contract policy:
  - External/API/MCP boundaries use `patient_token`.
  - Internal compatibility mapping (`patient_token` ↔ `patient_id`) is centralized.
- No removal of `/api/v1` in this gap; deprecation notes will be recorded in GAP-3 artifacts.

## Proposed Changes

### 1) Add centralized token/id resolver utilities

**Files**
- Update: `POC/v2/backend/src/api/routes/patients.py`
- (Optional helper placement if needed): `POC/v2/backend/src/api/routes/contracts.py`

**What**
- Add reusable lookup helpers:
  - resolve patient by `patient_token`
  - resolve patient by `patient_id`
  - get mapped counterpart (`token -> id`, `id -> token`)

**Why**
- Avoid duplicated mapping logic and ensure deterministic contract behavior across routes/workflows/tools.

**How**
- Reuse `assets/patient_registry.json` loading already present.
- Raise clear 404 behavior for unresolved identifiers.

### 2) Make MCP tools token-first with compatibility adapters

**Files**
- Update: `POC/v2/backend/src/mcp_server/tools/hard_constraints.py`
- Update: `POC/v2/backend/src/mcp_server/tools/clinical_signals.py`
- Update: `POC/v2/backend/src/mcp_server/tools/biomarker_trends.py`
- Update: `POC/v2/backend/src/mcp_server/tools/program_ruleset.py`
- Update: `POC/v2/backend/src/mcp_server/utils.py`

**What**
- Change MCP tool primary input to `patient_token` and map to underlying record lookup.
- Maintain temporary acceptance of `patient_id` via explicit adapter path where needed.

**Why**
- GAP-3 requires token consistency from API boundary through MCP tool calls.

**How**
- Introduce utility-level conversion so tool logic remains minimal.
- Ensure output payloads include token-consistent fields expected by v3 contracts.

### 3) Update workflow/orchestrator call chain to token-first

**Files**
- Update: `POC/v2/backend/src/services/workflows/clinical.py`
- Update: `POC/v2/backend/src/services/orchestrator.py`
- Update (if needed): `POC/v2/backend/src/services/workflows/base.py`

**What**
- Pass `patient_token` through workflow execution as the primary MCP call key.
- Keep internal `patient_id` for compatibility only where required by existing audit/log structures.

**Why**
- Removes current mismatch where token input is accepted but ignored in MCP boundaries.

**How**
- Refactor workflow phase methods to call MCP tools with token argument.
- Ensure returned context still supports GAP-2 Stage-2 assembler and safety/audit flow.

### 4) Preserve `/api/v1` through adapter behavior

**Files**
- Update: `POC/v2/backend/src/api/routes/clinical.py`
- Update: `POC/v2/backend/src/api/routes/contracts.py` (if adapter helper reused)

**What**
- Keep `/api/v1/clinical/recommend` operational by mapping incoming `patient_id` to `patient_token` before invoking token-first path.

**Why**
- User requested legacy compatibility retention during GAP-3.

**How**
- Add explicit conversion and documentation comments in GAP artifact files (not code comments).
- Keep response semantics stable for existing callers.

### 5) Migrate frontend service contract to token-first `/api` route

**Files**
- Update: `POC/v2/frontend/src/services/api.ts`
- Update: `POC/v2/frontend/src/components/dashboard/PatientList.tsx` (if payload bindings require token field use)
- Update: `POC/v2/frontend/src/app/page.tsx` (if selected patient object currently flows id-only)

**What**
- Switch recommendation request call to `/api/recommend` with `{ patient_token }`.

**Why**
- End-to-end token migration is part of confirmed scope.

**How**
- Use selected patient’s token from registry-backed list.
- Preserve compatibility for existing UI state while changing API payload key.

### 6) Update tests/scripts for token continuity evidence

**Files**
- Update: `POC/v2/scripts/tests/test_api_contract_routes.py`
- Update: `POC/v2/scripts/tests/test_end_to_end.py` (if route/path assumptions require token)
- Update: `POC/v2/scripts/test_orchestrator.py` (if explicit id assumptions conflict)
- Add (if needed): `POC/v2/scripts/tests/test_token_alignment_flow.py`

**What**
- Add assertions that validate token continuity:
  - route input token
  - workflow/MCP tool calls using token
  - audit/API response includes token-consistent shape
- Keep a compatibility test proving `/api/v1` adapter behavior still works.

**Why**
- GAP-3 exit evidence requires traceable and consistent token handling.

**How**
- Mock MCP/session boundaries where needed for deterministic checks.
- Preserve existing GAP-1/GAP-2 test coverage.

### 7) Update GAP-3 checkpoint artifacts

**Files**
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-3-mcp-token-alignment/_discovery.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-3-mcp-token-alignment/_lastest_test_results.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-3-mcp-token-alignment/_development_summary.md`

**What**
- Record migration decisions, compatibility policy, and verification evidence.

**Why**
- Required for gap traceability and downstream execution integrity.

## Verification Steps

1. Run targeted GAP-3 tests:
   - `uv run pytest scripts/tests/test_api_contract_routes.py -v`
   - `uv run pytest scripts/tests/test_token_alignment_flow.py -v` (if created)
2. Run full scripts test suite:
   - `uv run pytest scripts/tests -v`
3. Backend smoke checks:
   - `POST /api/recommend` with valid `patient_token` succeeds.
   - invalid token returns expected error.
   - `/api/v1/clinical/recommend` still works via adapter path.
4. Frontend smoke checks:
   - recommendation request from UI sends token payload and renders response.
5. Contract trace evidence:
   - capture proof that MCP tools are invoked with token-first arguments.

## Risks & Mitigations

- **Risk:** Broad migration causes regressions in existing tests.
  - **Mitigation:** Keep adapter compatibility and add targeted token-flow tests before full-suite run.
- **Risk:** Mixed id/token fields in audit path create ambiguity.
  - **Mitigation:** keep explicit conversion utilities and assert token presence in response-facing payloads.
- **Risk:** Frontend assumptions on id-only payloads break.
  - **Mitigation:** migrate service call first, then adjust component state mapping with minimal changes.

## Out of Scope

- Removal of `/api/v1` routes.
- GAP-4/5 UI contract delivery beyond token request wiring.
- Security/RBAC policy additions outside token contract normalization.

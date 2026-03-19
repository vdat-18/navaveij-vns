## GAP-0 — Baseline Run

- Setup: `uv sync` OK, BAML generation OK, `.env` added.
- Test 1 — API startup: success on port 8010 (port 8000 in use).
- Test 2 — Health check: `GET /health` → 200.
- Test 3 — Patient list: `GET /api/v1/patients/` → 23 patients.
- Test 4 — Recommendation valid ID: `POST /api/v1/clinical/recommend` (id_1aa1b504) → 200 after `.env` update.
- Test 5 — Invalid ID: → 404.
- Test 6 — Approve flow: → 200.
- Test 7 — Audit retrieval: → audit records returned.
- Test 8 — Automated tests: initial PYTHONPATH failure resolved; final run: `6 passed`.
- Test 9 — v3 endpoint smoke: all 4 v3 routes → 404 (expected, pre-GAP-1).

## GAP-1 — API Contract Alignment

- `uv run pytest scripts/tests/test_api_contract_routes.py -v` → `6 passed`
  - POST /api/recommend (valid token), POST /api/recommend (invalid token → 404),
    GET /api/timeline/{patient_token}, GET /api/monitoring-snapshot, GET /api/audit-logs (filter behavior),
    GET /api/v1/clinical/audit (legacy compatibility).
- `uv run pytest scripts/tests -v` → `12 passed`

## GAP-2 — Stage-2 Schema Completion

- `uv run pytest scripts/tests/test_api_contract_routes.py -v` → `6 passed`
  - Includes Stage-2 assertions: top-level fields, communication_script.opening, add-on enrichment, metadata presence.
- `uv run pytest scripts/tests -v` → `12 passed`

## GAP-3 — MCP Token Alignment

- `uv run pytest scripts/tests/test_api_contract_routes.py -v` → `7 passed`
  - Includes: /api/recommend token-first behavior, /api/v1/clinical/recommend legacy adapter path.
- `uv run pytest scripts/tests -v` → `13 passed`
- `npm run build` → `next: command not found` (missing local node_modules; not a TypeScript error).

## GAP-4 — Screen 2 Trend & Timeline

- `uv run pytest scripts/tests/test_timeline_contract_payload.py -v` → `2 passed`
- `uv run pytest scripts/tests/test_api_contract_routes.py -v` → `9 passed`
- `uv run pytest scripts/tests -v` → `17 passed`
- `npm install && npm run dev -- --port 3001` → dev server started; Screen 2 accessible at http://localhost:3001/trend-timeline.
- `npm run build` → failed on pre-existing `src/app/audit/page.tsx` import issue (tracked GAP-8).

## GAP-5 — Screen 3 Access Monitoring

- `uv run pytest scripts/tests/test_access_monitoring_contract.py scripts/tests/test_api_contract_routes.py -v` → `14 passed`
- `uv run pytest scripts/tests -v` → `22 passed`
- `npm run build` (frontend) → success, routes include `/access-monitoring`

## GAP-7 — Terminology Evidence

- Targeted verification:
  - `uv run pytest scripts/tests/test_timeline_contract_payload.py scripts/tests/test_access_monitoring_contract.py scripts/tests/test_api_contract_routes.py scripts/tests/test_frontend_terminology_visibility.py -v`
  - Result: `22 passed`
- Regression context:
  - `uv run pytest scripts/tests -v` → `33 passed, 1 failed`
  - Remaining failure is external-service-dependent in `test_end_to_end` (`503 Service Unavailable`), not GAP-7 terminology contract scope.

## GAP-6 — Security RBAC

- Targeted GAP-6 suite:
  - `uv run pytest scripts/tests/test_security_rbac_contract.py scripts/tests/test_access_monitoring_contract.py scripts/tests/test_api_contract_routes.py -v`
  - Result: `23 passed`
- Attempted frontend verification:
  - `npm run build`
- Execution environment issue remains for frontend command in this session (`npm` unavailable in runtime path).
- Static diagnostics check returned no code diagnostics after GAP-6 edits.

## GAP-8 — Frontend Reliability

- Targeted frontend reliability checks:
  - `uv run pytest scripts/tests/test_frontend_reliability_contract.py scripts/tests/test_frontend_terminology_visibility.py -v`
  - Result: `5 passed`
- Frontend build verification:
  - `npm run build` in `POC/v2/frontend`
  - Result in this runtime: `zsh: command not found: npm`
- Runtime check:
  - `uv run python -c "import shutil; print(shutil.which('npm')); print(shutil.which('node'))"` → `None`, `None`

## GAP-9 — Verification Pack

- Deterministic verification matrix:
  - `uv run pytest scripts/tests/test_gap9_verification_pack.py scripts/tests/test_api_contract_routes.py scripts/tests/test_security_rbac_contract.py scripts/tests/test_timeline_contract_payload.py scripts/tests/test_access_monitoring_contract.py scripts/tests/test_frontend_terminology_visibility.py scripts/tests/test_frontend_reliability_contract.py -v`
  - Result: `34 passed`
- Regression verification:
  - `uv run pytest scripts/tests -v`
  - Result: `40 passed`
- Frontend build gate:
  - `npm run build` in `POC/v2/frontend` → `zsh: command not found: npm`
- Runtime check:
  - `uv run python -c "import shutil; print(shutil.which('npm')); print(shutil.which('node'))"` → `None`, `None`

## GAP-10 — Backend Cache

- Phase 1-3 verification:
  - `uv run pytest /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2/scripts/tests/test_backend_cache_ttl.py /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2/scripts/tests/test_api_contract_routes.py /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2/scripts/tests/test_ruleset_path_resolution.py -v`
  - Result: `16 passed`
- Cache behavior note:
  - `/api/recommend` cache miss/hit behavior and orchestration-skip on hit are covered in contract tests.

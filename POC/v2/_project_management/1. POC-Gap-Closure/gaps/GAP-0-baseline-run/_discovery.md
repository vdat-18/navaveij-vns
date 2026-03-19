# GAP-0 Discovery Notes

## Session Metadata

- Date: 2026-03-18
- Working directory: `/Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2`
- OS:
  - ProductName: macOS
  - ProductVersion: 26.3.1
  - BuildVersion: 25D2128
- Python: `3.12.12`
- UV: `0.10.5`

## Setup Findings

- `uv sync` completed successfully; venv created and dependencies installed.
- `uv run baml-cli generate` completed successfully; `baml_client` files generated.
- `.env` is not present; only `.env.example` exists.
- Because `.env` was not provisioned, required BAML runtime vars (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`) are unset in baseline run.

## Runtime Discovery

- README Test 1 starts server on `:8000`, but local machine already has an active listener on `127.0.0.1:8000` from another process:
  - `/Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/.venv/bin/uvicorn src.api.main:app --port 8000`
- This creates misleading baseline observations when probing `localhost:8000`.
- To isolate `POC/v2`, baseline API checks were re-run on `:8010`:
  - `PYTHONPATH=.:./backend uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8010`

## API/Contract Discovery

- `POC/v2` routes are mounted under:
  - `/health`
  - `/api/v1/patients/*`
  - `/api/v1/clinical/*`
- v3-style endpoints are missing in baseline:
  - `POST /api/recommend`
  - `GET /api/timeline/{patient_token}`
  - `GET /api/monitoring-snapshot`
  - `GET /api/audit-logs`

## Data/Workflow Discovery

- Registry patient IDs are not in `P001` format; examples include:
  - `id_1aa1b504`
  - `id_33cc44dd`
- Therefore, README sample `{"patient_id":"P001"}` returns `404 Patient not found` in current dataset.
- With a valid patient ID, recommendation flow reaches workflow execution but fails due missing runtime configuration:
  - BAML error: missing `LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY`.
- Additional missing sample ruleset files are logged:
  - `sample_ruleset_tier_config.json`
  - `sample_add_on_items.json`
  - `sample_package_resolution.json`

## Test Harness Discovery

- `uv run pytest scripts/tests -v` fails collection without `PYTHONPATH` setup (`ModuleNotFoundError: shared`, `baml_client`).
- `PYTHONPATH=.:./backend uv run pytest scripts/tests -v` runs tests, but 2 async E2E tests fail with async execution/plugin issue.
- `scripts/test_api.py` is not an internal API verification script; it calls external LLM endpoint and prints a generic explanation.

## Deviations from GAP-0 README assumptions

- Port isolation is required in this environment to avoid cross-project listener conflict on `:8000`.
- README sample patient ID (`P001`) is stale relative to actual `assets/patient_registry.json`.
- Environment prerequisite is currently unmet (`.env` absent), which blocks meaningful recommendation-path baseline for success criteria.

## Rerun Discovery (after `.env` update)

- `.env` is now present and includes required LLM runtime variables.
- API recommendation path now succeeds for a valid registry patient ID (`id_1aa1b504`) with HTTP 200.
- v3 contract endpoints are still absent (`/api/recommend`, `/api/timeline/*`, `/api/monitoring-snapshot`, `/api/audit-logs` still 404).
- `scripts/test_orchestrator.py` now succeeds because it explicitly calls `load_dotenv()`.
- `scripts/tests/test_end_to_end.py` still reports missing `LLM_*` env vars because it does not load `.env`.

## Stabilization Gate Update (Step 0.5)

- Added environment/path bootstrap for tests via `scripts/tests/conftest.py`:
  - project + backend paths injected for imports
  - `.env` loaded from project root
- Updated `scripts/tests/test_end_to_end.py`:
  - now loads `.env` explicitly
  - now marks async tests with `pytest.mark.asyncio`
  - now uses real registry patient IDs (`id_*`) instead of `pt-*`
  - now supports direct script execution by path bootstrapping
- Updated `scripts/test_orchestrator.py`:
  - now supports direct script execution without manual `PYTHONPATH`
  - now uses first registry patient ID dynamically
- Replaced `scripts/test_api.py` external credential usage with local `/health` smoke check.
- Updated GAP-0 README commands to use dynamic registry patient IDs for recommendation and approve tests.
- Port 8000 is now used as canonical baseline port after preflight confirmed no active listener.

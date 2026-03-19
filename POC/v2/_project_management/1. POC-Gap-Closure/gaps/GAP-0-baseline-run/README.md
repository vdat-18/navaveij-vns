# GAP-0 — Baseline Run: POC v2 As-Is

**Severity:** N/A — observation only, no code changes  
**Execution order:** Step 0 — before any gap-closure implementation  
**Category:** Baseline / Diagnostics

---

## Purpose

Run `POC/v2` in the current state, capture exactly what works and what fails, and lock a baseline for measurable progress in later gaps.

All findings for this step must be written into:
- `_discovery.md`
- `_lastest_test_results.md`
- `_development_summary.md`

---

## Dependencies

- **Depends on:** nothing
- **Unblocks:** GAP-1 through GAP-9

---

## Context Discovery (Read First)

Review these files before running tests:

| File | Why |
|---|---|
| `POC/v2/README.md` | Setup and local run instructions |
| `POC/v2/.env.example` | Required environment variables |
| `POC/v2/pyproject.toml` | Python and dependency configuration |
| `POC/v2/backend/src/api/main.py` | API entrypoint and mounted routes |
| `POC/v2/backend/src/api/routes/clinical.py` | Clinical endpoints in current contract |
| `POC/v2/backend/src/services/orchestrator.py` | Runtime recommendation orchestration path |
| `POC/v2/backend/src/services/workflows/clinical.py` | MCP/LLM workflow behavior |
| `POC/v2/_project_management/POC-Gap-Closure/gap-discovery.md` | Expected gaps and risk areas |

---

## Setup Instructions

### 1) Install backend dependencies

```bash
cd /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2
uv sync
```

### 2) Configure environment

```bash
cp .env.example .env
```

Set required keys in `.env` based on the selected model provider.

### 3) Generate BAML client

```bash
cd /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2
baml-cli generate
```

---

## What to Run and Capture

Copy full outputs and logs into `_lastest_test_results.md`, labeled Test 1..10.

### Test 1 — Start API server

```bash
cd /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2
PORT=8000
lsof -nP -iTCP:${PORT} -sTCP:LISTEN
PYTHONPATH=.:./backend uv run python -m src.api.main
```

Record:
- startup success/failure
- import errors/warnings
- bound host/port

### Test 2 — Health check endpoint

```bash
curl -i http://localhost:8000/health
```

Expected: HTTP 200 with healthy status payload.

### Test 3 — List patients

```bash
curl -i http://localhost:8000/api/v1/patients/
```

Expected: HTTP 200 with patient list.

### Test 4 — Recommendation with known patient ID from registry

```bash
PATIENT_ID=$(curl -s http://localhost:8000/api/v1/patients/ | uv run python -c 'import json,sys; print(json.load(sys.stdin)[0]["patient_id"])')
curl -i -X POST http://localhost:8000/api/v1/clinical/recommend \
  -H "Content-Type: application/json" \
  -d "{\"patient_id\":\"${PATIENT_ID}\"}"
```

Record:
- status code
- full response JSON
- whether response includes core fields: `ai_recommended_tier`, `reasoning_trace`, `add_ons`

### Test 5 — Recommendation with invalid patient ID

```bash
curl -i -X POST http://localhost:8000/api/v1/clinical/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"DOES_NOT_EXIST"}'
```

Expected: graceful non-200 response (not server crash).

### Test 6 — Approve flow API

```bash
curl -i -X POST http://localhost:8000/api/v1/clinical/approve \
  -H "Content-Type: application/json" \
  -d "{\"patient_id\":\"${PATIENT_ID}\",\"recommendation_hash\":\"baseline-hash\",\"decision\":\"Approve\",\"physician_id\":\"dr-baseline\",\"notes\":\"baseline check\"}"
```

Record whether decision logging path is functional.

### Test 7 — Audit retrieval API

```bash
curl -i http://localhost:8000/api/v1/clinical/audit
```

Record response size and top-level field structure of returned entries.

### Test 8 — Run automated tests

```bash
cd /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2
uv run pytest scripts/tests -v 2>&1
```

Record full test output, pass/fail/error counts.

### Test 9 — Run integration scripts

```bash
cd /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2
uv run python scripts/test_orchestrator.py 2>&1
uv run python scripts/test_api.py 2>&1
uv run python scripts/tests/test_end_to_end.py 2>&1
```

Record all outputs and stack traces if any.

### Test 10 — Validate missing v3 endpoints (contract-gap evidence)

```bash
curl -i -X POST http://localhost:8000/api/recommend -H "Content-Type: application/json" -d '{"patient_token":"tok_hmac_56291047"}'
curl -i http://localhost:8000/api/timeline/tok_hmac_56291047
curl -i http://localhost:8000/api/monitoring-snapshot
curl -i http://localhost:8000/api/audit-logs
```

Expected baseline evidence: these routes are absent or contract-misaligned in current POC.

---

## What to Record in Each Checkpoint File

### `_discovery.md`
- machine/OS info and Python version
- dependency installation results
- environment setup notes
- BAML generation status
- deviations from README/setup assumptions

### `_lastest_test_results.md`
- raw command output for Tests 1–10
- HTTP status codes and payloads
- server/runtime error logs
- pytest output without summarization loss

### `_development_summary.md`
- what works reliably in baseline
- what fails and why (map to GAP-1..GAP-9)
- surprises vs expected from `gap-discovery.md`
- readiness implications for next execution order

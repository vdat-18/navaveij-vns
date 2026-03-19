# GAP-0 — Baseline Run: POC as-is

**Severity:** N/A — observation only, no code changes
**Execution order:** Step 0 — before any gap-closure work begins
**Estimated effort:** 30–60 minutes
**Category:** Baseline / Diagnostics

---

## Purpose

Run the POC in its current state, capture what works and what breaks, and record the baseline so that every subsequent gap closure can be verified as a measurable improvement against this starting point.

This step produces no code changes. All output goes into the three checkpoint files in this folder:
- `_discovery.md` — environment setup notes, what was tried, what the codebase looks like on first contact
- `_lastest_test_results.md` — raw output from every test run in this step
- `_development_summary.md` — interpreted summary: what passes, what fails, and why

---

## Dependencies

- **Depends on:** Nothing — this is the starting point
- **Unblocks:** All gap-closure steps (establishes the baseline they improve from)

---

## Context Discovery

Before running anything, read these files to understand the system:

| File | What to look for |
|---|---|
| `POC/README.md` | How to set up and run the POC — follow these instructions first |
| `POC/.env.example` | Required environment variables — copy to `.env` and fill in your API key |
| `POC/pyproject.toml` | Python version and dependency list |
| `POC/src/api/main.py` | The only API endpoint: `POST /recommend` |
| `POC/src/orchestrator/core/manager.py` | The canonical execution path called by the API |
| `POC/src/orchestrator/agents/orchestrator.py` | A second, richer orchestrator — note it is **not** called by the API |
| `POC/test_orchestrator.py` | Root-level integration test script |
| `project_management/POC-Gap-Closure/gap-discovery.md` | The full gap analysis — read this to know what to expect to fail |

---

## Setup Instructions

### 1. Install dependencies

```bash
cd POC
uv sync          # or: pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a working LLM key. Two options:

**Option A — Google Gemini (recommended for first run):**
```
GOOGLE_API_KEY=<your_google_ai_studio_key>
LLM_MODEL=gemini-1.5-flash
```

**Option B — Local LLM via LM Studio:**
```
LLM_API_KEY=
LLM_BASE_URL=http://127.0.0.1:1234/v1/
LLM_MODEL=<your-local-model-name>
```

> Note: `baml_src/clients.baml` uses `provider google-ai` and reads `GOOGLE_API_KEY`. Option A is the path of least resistance for a first run. Option B requires updating `clients.baml` (which is GAP-9 work — skip for now).

### 3. Generate BAML client (if `baml_client/` is absent or stale)

```bash
baml-cli generate
```

---

## What to Run and Capture

Run each of the following. Copy all output verbatim into `_lastest_test_results.md`.

### Test 1 — Start the API server

```bash
cd POC
uv run uvicorn src.api.main:app --reload --port 8000
```

Record: Does it start cleanly? Any import errors? Any warnings on startup?

### Test 2 — Health check

```bash
curl http://localhost:8000/
```

Expected: `{"status": "ok"}` or similar. Record actual response.

### Test 3 — Recommend with the canonical demo patient token

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "tok_hmac_56291047"}'
```

> Note: the endpoint is `/recommend` (not `/api/recommend`) and accepts `patient_id` (not `patient_token`) in the current state.

Record: full JSON response, HTTP status code, any server-side errors from the uvicorn log.

**Expected failures** (per gap-discovery.md):
- Response will not contain `confidence_score`, `confidence_tier`, `rule_preliminary_tier`, `resolved_package`, add-on `label`/`price` fields → GAP-2
- Response may contain UUID tokens instead of patient name/DOB → GAP-2 (PIIRehydrator not wired)
- `patient_high_alert` will be a boolean instead of an object → GAP-2

### Test 4 — Recommend with a known-bad patient token

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "tok_hmac_DOESNOTEXIST"}'
```

Record: does the server return an error gracefully or crash?

### Test 5 — Safety validator (mammogram test)

This is hard to trigger directly without injecting into the AI output. Instead, just inspect whether `mammogram` is absent from the response for Somchai W. (Test 3) — it should be absent because the AI was given constraints, but this is not deterministic.

Note in `_lastest_test_results.md` whether `mammogram` appears anywhere in the Test 3 response.

### Test 6 — Check audit log output

```bash
cat POC/logs/audit.jsonl | tail -1 | python -m json.tool
```

Record the full pretty-printed JSON. Note which top-level keys are present (`who`, `when`, `where`, `what`, `why`, `how`, `timestamp`, etc.) — this captures the GAP-4 baseline.

### Test 7 — Run the existing test suite

```bash
cd POC
uv run pytest tests/ -v 2>&1
```

Record: full pytest output — which tests pass, which fail, any errors.

### Test 8 — Run `test_orchestrator.py`

```bash
cd POC
uv run python test_orchestrator.py 2>&1
```

Record: does it run? Does it crash (expected — it calls the deprecated `get_patient_context` MCP tool)? Full traceback if it errors.

### Test 9 — Check for security issues

```bash
grep -r "AIzaSy" POC/
grep "secret-salt" POC/src/shared/settings.py
```

Record: the matching lines (expected to find both per GAP-1).

### Test 10 — Verify missing endpoints

```bash
curl http://localhost:8000/api/timeline/tok_hmac_56291047
curl http://localhost:8000/api/monitoring-snapshot
curl "http://localhost:8000/api/audit-logs"
```

Record: all three should return 404 (per GAP-6).

---

## What to Record in Each Checkpoint File

### `_discovery.md`
- Python version used (`python --version`)
- `uv sync` / install outcome — any dependency conflicts?
- BAML generation outcome (`baml-cli generate`)
- Notes on first contact with the codebase: anything surprising, anything that differs from what `gap-discovery.md` predicted
- Any setup steps that required deviation from the README

### `_lastest_test_results.md`
- Raw output from Tests 1–10 above, labelled by test number
- HTTP status codes and full response bodies
- Server logs for any errors
- Pytest output verbatim

### `_development_summary.md`
- **What works:** list each test that passed as expected
- **What fails:** list each test that failed, with a one-line diagnosis pointing to the relevant GAP-N
- **Surprises:** anything that behaved differently from what `gap-discovery.md` predicted
- **Environment notes:** OS, Python version, LLM provider used
- **Readiness assessment:** based on this run, confirm or update the execution order for GAP-1 through GAP-10

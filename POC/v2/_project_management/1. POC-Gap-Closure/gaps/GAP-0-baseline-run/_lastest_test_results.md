# GAP-0 Latest Test Results

## Setup

### Setup 1 — Dependency install

```bash
uv sync
```

Result: success. Virtual environment created and dependencies installed.

### Setup 2 — BAML generation

```bash
uv run baml-cli generate
```

Result: success. `baml_client` generated.

### Setup 3 — Environment file

```bash
ls -la .env .env.example
```

Result: `.env` missing; `.env.example` present.

---

## Test 1 — Start API server

### Attempt A (README path on port 8000)

```bash
PYTHONPATH=.:./backend uv run python -m src.api.main
```

Result: process starts, but `localhost:8000` responses are contaminated by another listener.

Evidence:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

Includes another process:

```text
/Users/.../POC/.venv/bin/uvicorn src.api.main:app --port 8000 --log-level info
```

### Attempt B (isolated port 8010)

```bash
PYTHONPATH=.:./backend uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8010 --log-level info
```

Result: success; baseline API tests executed against `localhost:8010`.

---

## Test 2 — Health check

```bash
curl -i http://localhost:8010/health
```

Observed:

```http
HTTP/1.1 200 OK
{"status":"healthy","version":"1.0.0"}
```

---

## Test 3 — List patients

```bash
curl -i http://localhost:8010/api/v1/patients/
```

Observed summary:

```text
HTTP/1.1 200 OK
body size: 2845 bytes
sample ids: id_1aa1b504, id_33cc44dd, ...
```

---

## Test 4 — Recommendation with known patient ID (README sample)

```bash
curl -i -X POST http://localhost:8010/api/v1/clinical/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"P001"}'
```

Observed:

```http
HTTP/1.1 404 Not Found
{"detail":"Patient not found"}
```

Additional probe with registry ID:

```bash
curl -i -X POST http://localhost:8010/api/v1/clinical/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"id_1aa1b504"}'
```

Observed:

```http
HTTP/1.1 500 Internal Server Error
{"detail":"unhandled errors in a TaskGroup (1 sub-exception)"}
```

Server log excerpt:

```text
BAML ERROR: LLM client 'NavaveijClient' requires environment variable 'LLM_BASE_URL' to be set but it is not
```

---

## Test 5 — Recommendation with invalid patient ID

```bash
curl -i -X POST http://localhost:8010/api/v1/clinical/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"DOES_NOT_EXIST"}'
```

Observed:

```http
HTTP/1.1 404 Not Found
{"detail":"Patient not found"}
```

---

## Test 6 — Approve flow API

```bash
curl -i -X POST http://localhost:8010/api/v1/clinical/approve \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"P001","recommendation_hash":"baseline-hash","decision":"Approve","physician_id":"dr-baseline","notes":"baseline check"}'
```

Observed:

```http
HTTP/1.1 200 OK
{"status":"success","decision_hash":"1955a6...73abc8","patient_id":"P001","decision":"Approve"}
```

---

## Test 7 — Audit retrieval API

```bash
curl -i http://localhost:8010/api/v1/clinical/audit
```

Observed:

```http
HTTP/1.1 200 OK
[{"timestamp":"...","who":{"patient_id":"P001","physician_id":"dr-baseline"},...,"current_hash":"1423a9..."}]
```

---

## Test 8 — Automated tests

### As written in README

```bash
uv run pytest scripts/tests -v
```

Observed summary:

```text
collected 0 items / 4 errors
ModuleNotFoundError: shared
ModuleNotFoundError: shared.settings
ModuleNotFoundError: baml_client
```

### With explicit PYTHONPATH

```bash
PYTHONPATH=.:./backend uv run pytest scripts/tests -v
```

Observed summary:

```text
6 collected
4 passed
2 failed (scripts/tests/test_end_to_end.py async execution issue)
```

---

## Test 9 — Integration scripts

### `scripts/test_orchestrator.py`

```bash
PYTHONPATH=.:./backend uv run python scripts/test_orchestrator.py
```

Observed:

```text
fails; BAML runtime missing LLM_BASE_URL (and other LLM env vars)
```

### `scripts/test_api.py`

```bash
PYTHONPATH=.:./backend uv run python scripts/test_api.py
```

Observed:

```text
prints generic "Explain LLMs in simple terms" response from external model API
```

### `scripts/tests/test_end_to_end.py`

```bash
PYTHONPATH=.:./backend uv run python scripts/tests/test_end_to_end.py
```

Observed:

```text
fails scenario execution; missing LLM_API_KEY and test patient IDs (pt-001/pt-002) not found in Signal Store
```

---

## Test 10 — Missing v3 endpoints (contract-gap evidence)

```bash
curl -i -X POST http://localhost:8010/api/recommend -H "Content-Type: application/json" -d '{"patient_token":"tok_hmac_56291047"}'
curl -i http://localhost:8010/api/timeline/tok_hmac_56291047
curl -i http://localhost:8010/api/monitoring-snapshot
curl -i http://localhost:8010/api/audit-logs
```

Observed for all 4:

```http
HTTP/1.1 404 Not Found
{"detail":"Not Found"}
```

---

## Rerun (after `.env` update)

### API checks

```bash
curl -sS -D /tmp/retry_health.h -o /tmp/retry_health.b http://localhost:8010/health
curl -sS -D /tmp/retry_patients.h -o /tmp/retry_patients.b http://localhost:8010/api/v1/patients/
curl -sS -D /tmp/retry_recommend.h -o /tmp/retry_recommend.b \
  -X POST http://localhost:8010/api/v1/clinical/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"id_1aa1b504"}'
```

Observed:

```text
/health => HTTP/1.1 200 OK
/api/v1/patients/ => HTTP/1.1 200 OK (patients_count=23)
/api/v1/clinical/recommend (id_1aa1b504) => HTTP/1.1 200 OK
```

### Contract-gap check (unchanged)

```bash
curl -sS -D /tmp/retry_v3.h -o /tmp/retry_v3.b \
  -X POST http://localhost:8010/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_token":"tok_hmac_56291047"}'
```

Observed:

```http
HTTP/1.1 404 Not Found
{"detail":"Not Found"}
```

### Test harness rerun

```bash
PYTHONPATH=.:./backend uv run pytest scripts/tests -v
PYTHONPATH=.:./backend uv run python scripts/test_orchestrator.py
PYTHONPATH=.:./backend uv run python scripts/tests/test_end_to_end.py
```

Observed summary:

```text
pytest: 4 passed, 2 failed (async test execution issue remains)
test_orchestrator.py: success (full orchestration path returned output)
test_end_to_end.py: still fails; logs report missing LLM_* and pt-001/pt-002 data mismatch
```

---

## Stabilization Rerun (Step 0.5 complete)

### API baseline on canonical port 8000

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
PYTHONPATH=.:./backend uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --log-level info
```

Observed:

```text
preflight: no existing listener on 8000
server start: success on http://0.0.0.0:8000
```

```bash
PATIENT_ID=$(curl -s http://localhost:8000/api/v1/patients/ | uv run python -c 'import json,sys; print(json.load(sys.stdin)[0]["patient_id"])')
curl -i http://localhost:8000/health
curl -i -X POST http://localhost:8000/api/v1/clinical/recommend -H "Content-Type: application/json" -d "{\"patient_id\":\"${PATIENT_ID}\"}"
curl -i -X POST http://localhost:8000/api/v1/clinical/recommend -H "Content-Type: application/json" -d '{"patient_id":"DOES_NOT_EXIST"}'
curl -i -X POST http://localhost:8000/api/v1/clinical/approve -H "Content-Type: application/json" -d "{\"patient_id\":\"${PATIENT_ID}\",\"recommendation_hash\":\"baseline-hash\",\"decision\":\"Approve\",\"physician_id\":\"dr-baseline\",\"notes\":\"baseline check\"}"
curl -i -X POST http://localhost:8000/api/recommend -H "Content-Type: application/json" -d '{"patient_token":"tok_hmac_56291047"}'
```

Observed summary:

```text
PATIENT_ID=id_1aa1b504
/health => 200
/api/v1/clinical/recommend valid => 200
/api/v1/clinical/recommend invalid => 404
/api/v1/clinical/approve => 200
/api/recommend => 404
```

### Stabilized test harness

```bash
uv run pytest scripts/tests -v
uv run python scripts/test_orchestrator.py
uv run python scripts/tests/test_end_to_end.py
uv run python scripts/test_api.py
```

Observed summary:

```text
pytest: 6 passed
test_orchestrator.py: exit 0
test_end_to_end.py: exit 0
test_api.py: {'status': 'healthy', 'version': '1.0.0'}
```

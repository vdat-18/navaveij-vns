# GAP-0 — Latest Test Results

**Date:** 2026-03-17
**LLM Provider:** TrollLLM proxy (`https://chat.trollllm.xyz/v1`, model: `claude-sonnet-4.6`)
**Server start method:** `uv run uvicorn src.api.main:app --port 8000` (from `POC/` directory, with `baml_client/` symlinked from repo root, `audit.jsonl` cleared)

---

## Test 1 — Start the API server

**Command:**
```bash
cd POC/
uv run uvicorn src.api.main:app --port 8000
```

**First attempt output (FAILED — without workarounds):**
```
ModuleNotFoundError: No module named 'baml_client'
```
→ Root cause: `baml_client/` not in `sys.path` when running from `POC/`.

**Second attempt (after symlink, FAILED — audit log bug):**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  File "...audit.py", line 41, in _get_last_hash
    last_line = json.loads(lines[-1])
```
→ Root cause: `_get_last_hash()` reads only last 8KB; last audit entry is 24KB. Server cannot start with existing `audit.jsonl`.

**Third attempt (after clearing audit.jsonl, ✅ PASSED):**
```
INFO:     Started server process [49127]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## Test 2 — Health check

**Command:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{"status":"online","engine":"Navaveij Clinical Orchestrator"}
```
**HTTP Status:** 200 ✅

---

## Test 3a — Recommend: existing patient `pt-001`

**Command:**
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "pt-001"}'
```

**Response:**
```
Internal Server Error
```
**HTTP Status:** 500

**Server-side error (from uvicorn log):**
```
baml_py.internal_monkeypatch.BamlClientHttpError: BamlClientHttpError(
  client_name=NavaveijClient,
  message=Request failed with status code: 400 Bad Request.
  {"error":{"message":"Request failed. Please try again.","type":"api_error","code":400}},
  status_code=400,
  detailed_message=LLM client "NavaveijClient" failed with status code: Unspecified error code: 400
)
```

**Root cause under investigation:** BAML's OpenAI provider sends a request format (possibly `json_schema` response_format or tool-use) that the TrollLLM proxy returns a 400 for. The direct `curl` call to the same endpoint works correctly. This blocks the full recommendation flow.

**Full traceback chain:**
```
GET /recommend
  → OrchestrationManager.generate_recommendation("pt-001")
  → MCPClientFactory.get_client() — MCP server starts OK
  → ClinicalReasoningWorkflow.execute("pt-001")
  → workflow._generate_recommendation()
  → b.GenerateRecommendation(hard_constraints, clinical_signals, biomarker_trends, program_ruleset)
  → BamlClientHttpError: 400 Bad Request from TrollLLM proxy
```

---

## Test 3b — Recommend: canonical demo patient `tok_hmac_56291047` (Somchai W.)

**Command:**
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "tok_hmac_56291047"}'
```

**Response:**
```
Internal Server Error
```
**HTTP Status:** 500 (not a 404 — error is unhandled exception, not a graceful "not found")

**Note:** Server hits the same BAML 400 error before it can even check for the missing record. The "Record not found" error (GAP-8) cannot be observed until the BAML LLM issue is resolved.

---

## Test 4 — Recommend: unknown token `tok_hmac_DOESNOTEXIST`

**Command:**
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "tok_hmac_DOESNOTEXIST"}'
```

**Response:**
```
Internal Server Error
```
**HTTP Status:** 500

**Note:** Same BAML 400 error as Test 3a. No graceful error handling — all unknown/missing patients return 500 with no descriptive message.

---

## Test 5 — Safety validator: mammogram check

**Status:** ⚠️ Cannot be evaluated — blocked by Test 3a failure (no AI output produced).

---

## Test 6 — Audit log structure (pre-baseline snapshot)

**Command:**
```bash
tail -1 POC/logs/audit_baseline_backup.jsonl | python3 -m json.tool
```
*(Note: Using the archived backup of the original audit.jsonl)*

**Top-level keys found:**
```
['timestamp', 'who', 'what', 'why', 'how', 'confidence', 'metadata', 'previous_hash', 'current_hash']
```

**5-Dimension Compliance Check:**

| Dimension | Key Expected | Key Found | Status |
|---|---|---|---|
| **Who** | `who` | `who` (contains only `patient_id`) | ⚠️ Partial — `patient_id` present but spec requires `user_id + role + SMART token` |
| **When** | `when` | ❌ absent — uses `timestamp` instead | ❌ Non-compliant |
| **Where** | `where` | ❌ entirely absent | ❌ Non-compliant (GAP-4) |
| **What** | `what` | `what` (contains only `input_context_snapshot`) | ⚠️ Partial — missing `model_id`, `template_version`, `latency`, `safety_result`, `confidence_score` |
| **Why** | `why` | `why` (contains `reasoning_trace`, `decision`) | ✅ Present |

**Additional non-compliant top-level keys:**
- `how`: `{"model_provider": "local", "model_id": "meta-llama-3.1-8b-instruct"}` — should be inside `what`, not standalone
- `confidence`: top-level orphan (was `null` in last entry) — should be inside `what`
- `timestamp`: present (should be named `when`)

**Hash chain status:** ✅ Intact — each entry's `previous_hash` matches prior entry's `current_hash`. Genesis entry has `previous_hash = "0" * 64`.

**Last pre-baseline entry (entry #8, 2026-03-16):**
```json
{
  "timestamp": "2026-03-16T03:59:46.683102+00:00",
  "who": { "patient_id": "pt-001" },
  "what": { "input_context_snapshot": { ... } },
  "why": { "reasoning_trace": "...", "decision": "Advanced" },
  "how": { "model_provider": "local", "model_id": "meta-llama-3.1-8b-instruct" },
  "confidence": null,
  "metadata": { "environment": "dev" },
  "previous_hash": "bd5d5cfd...",
  "current_hash": "10020ac1..."
}
```

---

## Test 7 — pytest test suite

**Command:**
```bash
cd POC/
PYTHONPATH=/navaveij:/navaveij/POC uv run pytest tests/ -v
```

**Output:**
```
platform darwin -- Python 3.12.12, pytest-9.0.2, pluggy-1.6.0
asyncio: mode=Mode.STRICT

collected 6 items

tests/infrastructure/test_mcp_factory.py::test_mcp_factory_lifecycle     PASSED
tests/shared/test_exceptions.py::test_exception_hierarchy                 PASSED
tests/shared/test_exceptions.py::test_exception_metadata                  PASSED
tests/test_end_to_end.py::test_with_synthesized_data                      FAILED
tests/test_end_to_end.py::test_multiple_scenarios                         FAILED
tests/workflows/test_clinical_workflow.py::test_clinical_workflow_execution PASSED

FAILURES:
  test_with_synthesized_data — "async def functions are not natively supported"
  test_multiple_scenarios    — "async def functions are not natively supported"

4 passed, 2 failed
```

**Failure root cause:** The two end-to-end tests are defined as `async def` but have no `@pytest.mark.asyncio` decorator. `pytest-asyncio` in `Mode.STRICT` requires explicit decoration — without it, pytest treats them as sync functions and fails immediately. This is a test configuration bug, not a production code bug.

---

## Test 8 — test_orchestrator.py (expected crash)

**Command:**
```bash
cd POC/
PYTHONPATH=/navaveij:/navaveij/POC uv run python test_orchestrator.py
```

**Output:**
```
INFO  | Starting integration test for OrchestrationManager
Traceback (most recent call last):
  File "test_orchestrator.py", line 28, in <module>
    asyncio.run(test_full_orchestration())
  File "test_orchestrator.py", line 15, in test_full_orchestration
    orchestrator = OrchestrationManager()
  File "...manager.py", line 26, in __init__
    self.audit_logger = AuditLogger()
  File "...audit.py", line 23, in __init__
    self.last_hash = self._get_last_hash()
  File "...audit.py", line 41, in _get_last_hash
    last_line = json.loads(lines[-1])
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Actual vs. predicted failure:**
- **Predicted (gap-discovery.md):** Crash on deprecated `get_patient_context` MCP tool
- **Actual:** Crash at `OrchestrationManager.__init__()` → `AuditLogger._get_last_hash()` — never reaches the deprecated tool
- **Reason:** The oversized audit entry (24KB > 8KB buffer) causes a `JSONDecodeError` **before any MCP tools are invoked**

---

## Test 9 — Security checks

**Command:**
```bash
grep -r "AIzaSy" POC/
grep "secret-salt" POC/src/shared/settings.py
```

**Output:**
```
=== grep AIzaSy ===
POC/.env:# LLM_API_KEY=AIzaSy... (Get from Google AI Studio)                ← comment in .env template
POC/scripts/test_api.py:    # api_key="AIzaSyBWKGlVTGseZFyfgzjeuo4-...",   ← ROTATED key (commented out)
POC/scripts/test_api.py:    api_key="AIzaSyAcgGGUvybk7xww0Yuk1uoiiKcU0MfQwW0",  ← LIVE key (active!)

=== grep secret-salt ===
    patient_token_secret_salt: str = "navavej-clinical-recommendation-engine-secret-salt-2026"
```

**Security findings confirmed:**
1. ✅ **GAP-1 confirmed:** `POC/scripts/test_api.py` contains an active Google AI Studio API key in source code. A previously rotated key is also present as a comment — both are in git history.
2. ✅ **GAP-1 confirmed:** HMAC secret salt hardcoded as a default value in `settings.py`. Anyone with the source can derive patient tokens for any known `patient_id`.

---

## Test 10 — Missing API endpoints

**Commands:**
```bash
curl -i http://localhost:8000/api/timeline/tok_hmac_56291047
curl -i http://localhost:8000/api/monitoring-snapshot
curl -i "http://localhost:8000/api/audit-logs"
```

**Results:**

| Endpoint | HTTP Status | Body |
|---|---|---|
| `GET /api/timeline/tok_hmac_56291047` | **404** | `{"detail":"Not Found"}` |
| `GET /api/monitoring-snapshot` | **404** | `{"detail":"Not Found"}` |
| `GET /api/audit-logs` | **404** | `{"detail":"Not Found"}` |

✅ All three return 404 as expected (GAP-6 confirmed).

---

## LLM Direct Connectivity Test (Additional — BAML 400 diagnosis)

**Direct curl to TrollLLM (✅ works):**
```bash
curl -X POST "https://chat.trollllm.xyz/v1/chat/completions" \
  -H "Authorization: Bearer sk-trollllm-..." \
  -d '{"model": "claude-sonnet-4.6", "messages": [{"role": "user", "content": "Say 1"}], "max_tokens": 5}'

→ {"choices":[{"message":{"content":"1"}}], "model":"Claude Sonnet 4.6"}
```

**BAML GenerateRecommendation() call (❌ fails with 400):**
```
baml_py.BamlClientHttpError: Request failed with status code: 400 Bad Request.
{"error":{"message":"Request failed. Please try again.","type":"api_error","code":400}}
```

**Hypothesis:** BAML's OpenAI provider may be sending a `response_format: json_schema` or structured tool-use payload that the TrollLLM proxy does not support. Investigation pending with development colleague.

---

## Re-run — Tests 3a, 3b, 5 after `provider anthropic` fix (2026-03-17)

**Fix applied:** `clients.baml` changed from `provider openai` → `provider anthropic` (TrollLLM is a Claude/Anthropic-format proxy). `baml_client/` regenerated. `main.py` load_dotenv() order corrected. `LLM_BASE_URL` updated to `https://chat.trollllm.xyz` (no `/v1` suffix — BAML anthropic provider appends path automatically).

**Server:** `python3 (PID 68450)` from earlier session, port 8000, `audit.jsonl` cleared before run (backed up as `audit_run2_backup.jsonl`).

---

### Re-run Test 3a — `POST /recommend` with `pt-001`

**Command:**
```bash
curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "pt-001"}'
```

**HTTP Status:** 200 ✅

**Response (summary):**
```json
{
  "ai_recommended_tier": "Standard",
  "tier_deviation_justification": null,
  "add_ons": [],
  "supporting_signals": [],
  "missing_signals": [],
  "reasoning_trace": "TIER DETERMINATION: The rule-based Clinical Signal Engine assigned a preliminary tier of 'Standard' under applied rule 'STANDARD_DEFAULT' with an overall risk level of 'Low'. [... full trace, see server log ...]",
  "communication_script": { "opening": "Welcome ...", "health_summary": "...", "recommendation_explanation": "...", "add_on_highlights": [], "next_steps": "..." },
  "safety_check": {
    "is_safe": true,
    "critic_score": 0.91,
    "findings": ["No clinical contradictions detected ...", "DATA COMPLETENESS WARNING: all biomarker objects are empty, patient demographics (age, gender, ethnicity) are null ..."],
    "suggested_correction": "Verify pipeline integrity and capture patient demographics before finalizing recommendation."
  }
}
```

**BAML 400 error:** ✅ RESOLVED — full structured recommendation returned.

**Server-side log (relevant):**
```
INFO  | Engaging BAML Clinical Safety Critic
INFO  | Recording audit log
INFO  | Dual audit log written for patient: pt-001
INFO  | 127.0.0.1 - "POST /recommend HTTP/1.1" 200 OK
```

---

### Re-run Test 3b — `POST /recommend` with `tok_hmac_56291047` (Somchai W.)

**HTTP Status:** 200 ✅ (unexpected — was predicted to be 500 "Record not found")

**Response (summary):**
```json
{
  "ai_recommended_tier": "Standard",
  "tier_deviation_justification": null,
  "add_ons": [],
  "safety_check": { "is_safe": true, "critic_score": 0.82 }
}
```

**GAP-8 observation (revised):** The MCP Signal Store does NOT raise "record not found" for `tok_hmac_56291047`. Instead it returns a skeleton record with all fields null/empty (patient_demographics: `{}`, age: null, gender: null, all biomarker trends empty). The server completes the full pipeline and returns Standard tier based on absence-of-signals logic.

This changes the GAP-8 description: the issue is not a missing record but an *empty* record for Somchai W. GAP-8 work must **populate** the existing skeleton fixture with realistic demographic and clinical data, not create a new record.

**Audit log:** `who.patient_id = "tok_hmac_56291047"` ✅ written successfully.

---

### Re-run Test 5 — Mammogram safety check

**Result:** ✅ `mammogram` is absent from both Test 3a and Test 3b responses.

**Caveat:** The safety validator cannot be meaningfully stress-tested for the mammogram-for-male rule because neither patient has a non-null `gender` field. The rule fires only when gender = Male AND a mammogram appears in recommendations. With null gender, the LLM correctly defers rather than fabricating recommendations. A proper Test 5 evaluation requires Somchai W.'s fixture to have `gender: Male` populated (GAP-8).

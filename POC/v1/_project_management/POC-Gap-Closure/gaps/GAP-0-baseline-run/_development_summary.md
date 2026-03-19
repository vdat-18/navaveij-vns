# GAP-0 — Development Summary

**Date:** 2026-03-17 (re-run: 2026-03-17 11:45–11:46 UTC+7)
**Author:** Architecture Review
**Environment:** macOS arm64, Python 3.12.12 (uv venv), TrollLLM proxy (`claude-sonnet-4.6`)
**BAML provider:** `anthropic` (confirmed working — see Surprise 6 below)

---

## What Works

| Test | Result | Notes |
|---|---|---|
| **Test 1** — Server startup | ✅ After workarounds | Requires: `baml_client/` in POC dir, empty `audit.jsonl`, `baml-py==0.220.0` installed |
| **Test 2** — Health check `GET /` | ✅ 200 | Returns `{"status":"online","engine":"Navaveij Clinical Orchestrator"}` |
| **Test 3a** — `POST /recommend` `pt-001` | ✅ 200 | **RESOLVED** — `provider anthropic` fix. Returns full structured recommendation (`ai_recommended_tier`, `add_ons`, `safety_check` with `critic_score: 0.91`). |
| **Test 3b** — `POST /recommend` `tok_hmac_56291047` | ✅ 200 | Unexpected pass — MCP returns empty skeleton record, not "record not found". See Surprise 6. |
| **Test 5** — Mammogram absent | ✅ Absent | Correct — gender null on all patients so sex-specific rules not triggered. Full stress-test requires GAP-8 (populated Somchai W. fixture). |
| **Test 7** — pytest (4/6 tests) | ✅ 4 pass | `test_mcp_factory_lifecycle`, `test_exception_hierarchy`, `test_exception_metadata`, `test_clinical_workflow_execution` |
| **Test 9** — Security grep | ✅ Both issues confirmed | Hardcoded key and salt found exactly where predicted |
| **Test 10** — Missing endpoints | ✅ All 404 | All 3 missing endpoints return 404 as expected |
| **Audit hash chain** | ✅ Intact | Pre-baseline SHA-256 chain verified across all 8 entries |

---

## What Fails

| Test | Failure | Root GAP | Notes |
|---|---|---|---|
| **Test 1** — Server startup (first run) | `ModuleNotFoundError: No module named 'baml_client'` | New unlisted gap | `baml_client/` generated at repo root, not in `POC/` import path |
| **Test 1** — Server startup (second run) | `JSONDecodeError` in `AuditLogger._get_last_hash()` | **🆕 UNLISTED BUG** | 8KB tail-read buffer too small for 24KB audit entry — blocks startup |
| **Test 3a** — `POST /recommend` with `pt-001` | ✅ **RESOLVED** (200) | 🆕 Fixed | `provider openai` → `provider anthropic`; TrollLLM is Anthropic-format proxy |
| **Test 3b** — `POST /recommend` with `tok_hmac_56291047` | ✅ 200 (unexpected) | GAP-8 revised | MCP returns empty skeleton, not "record not found" — GAP-8 is a populate, not create |
| **Test 4** — Unknown token | 500 (no graceful error) | GAP-6 (no error handling) | All unknown patients return 500 with no descriptive message |
| **Test 5** — Mammogram safety check | ⚠️ Partial — absent confirmed, full stress-test blocked | GAP-3 + GAP-8 | Mammogram absent ✅. Full determinism test requires non-null gender in Somchai W. fixture |
| **Test 6** — Audit log 5-dimension | ⚠️ Non-compliant structure | GAP-4 | `where` absent; uses `timestamp` not `when`; `how`/`confidence` are orphan top-level keys |
| **Test 7** — pytest (2/6 tests) | `async def functions not natively supported` | Minor test bug | `@pytest.mark.asyncio` missing on 2 end-to-end tests in `Mode.STRICT` |
| **Test 8** — `test_orchestrator.py` | `JSONDecodeError` (NOT the predicted crash) | 🆕 UNLISTED BUG | Crashes at `AuditLogger.__init__()` before ever reaching the deprecated MCP tool |

---

## Surprises (Deviations from gap-discovery.md Predictions)

### 🐛 Surprise 1 — `AuditLogger._get_last_hash()` buffer overflow bug (CRITICAL)

**Predicted:** Server starts normally.
**Actual:** Server cannot start if `audit.jsonl` has a large entry (last entry was 24,495 bytes; buffer is 8,192 bytes).

**Root cause:** `audit.py:_get_last_hash()` reads only the last 8KB via `f.seek(file_size - read_size)`. When a single log entry exceeds 8KB, the tail read returns a truncated JSON fragment. Parsing it raises `JSONDecodeError`, which crashes `AuditLogger.__init__()`, which is called at module-level (`manager = OrchestrationManager()` in `main.py`), preventing server startup.

**Impact:** This is a **production blocker**. Any real run with large context windows (full Signal Store records) will produce entries well over 8KB. The server will permanently fail to restart after the first real recommendation. This needs to be added to the gap list (suggest GAP-11 or folded into GAP-4 as it's in `audit.py`).

**Fix:** Replace the 8KB tail-read approach with `lines = [l.strip() for l in f if l.strip()]` and take `lines[-1]` — the existing `line.strip()` filter already handles empty lines.

---

### ✅ Surprise 2 — BAML 400 error from TrollLLM proxy (RESOLVED)

**Predicted:** `POST /recommend` with `pt-001` returns a 200 with raw unenriched output.
**Initial actual (first run):** Returns 500. The BAML `openai` provider gets a 400 from the TrollLLM proxy.

**Root cause:** BAML's `openai` provider sends `response_format: {"type": "json_schema", ...}` or tool-calling payloads that TrollLLM rejects.

**Fix applied:** Changed `clients.baml` from `provider openai` → `provider anthropic`. TrollLLM is a Claude/Anthropic-format proxy — it accepts the native Anthropic API request format (`/v1/messages`). BAML's `anthropic` provider does not use `json_schema` or tool-calls; it sends plain Anthropic-format messages and parses structured output from the response text using `{{ ctx.output_format }}` in the prompt.

**`LLM_BASE_URL` correction:** Updated from `https://chat.trollllm.xyz/v1` to `https://chat.trollllm.xyz` (BAML's anthropic provider appends the `/v1/messages` path automatically; the `/v1` suffix caused a double-path issue).

**Re-run result (2026-03-17):** `POST /recommend` with `pt-001` → HTTP 200, full structured `RecommendationOutput` with `ai_recommended_tier`, `add_ons`, `reasoning_trace`, `safety_check`. ✅ Confirmed resolved.

**For GAP-9 (multi-client):** The `anthropic` client should be `NavaveijAnthropicClient`; `openai` client (`NavaveijOpenAIClient`) should be preserved for true OpenAI-spec endpoints, not for TrollLLM.

---

### Surprise 3 — Test 8 crash is different from prediction

**Predicted:** `test_orchestrator.py` crashes on deprecated `get_patient_context` MCP tool.
**Actual:** Crashes at `OrchestrationManager()` instantiation — specifically `AuditLogger._get_last_hash()` (the buffer overflow bug above). The deprecated tool is never reached.

---

### Surprise 4 — Missing dependencies not declared in pyproject.toml

**Predicted:** `uv sync` installs all required packages.
**Actual:** `baml-py==0.220.0` is not listed in `pyproject.toml`. It must be added manually. Any fresh checkout will fail to import `baml_client` until this is added.

---

### Surprise 5 — `baml_client/` path not accessible from POC/

**Predicted:** Not mentioned in gap-discovery.md.
**Actual:** `baml_client/` is generated at the repo root (`navaveij/baml_client/`), but `POC/src/` imports it as `from baml_client.xxx`. Running uvicorn from `POC/` results in `ModuleNotFoundError`. The workaround used was a symlink; the correct long-term fix is to either add a path configuration to `pyproject.toml` or set `PYTHONPATH` in an `.env` or run script.

---

### Surprise 6 — GAP-8 behavior: empty skeleton record, not "Record not found" (re-run 2026-03-17)

**Predicted:** `POST /recommend` with `tok_hmac_56291047` returns 500 — "Record not found" for Somchai W.
**Actual (after BAML fix):** Returns HTTP 200. The MCP Signal Store returns a skeleton record for this token with all clinical fields null/empty (`age: null`, `gender: null`, all biomarker trends empty objects). The pipeline completes and returns a Standard-tier recommendation based on absence-of-signals.

**GAP-8 scope revision:** The Somchai W. fixture is not *missing* — it exists as an empty shell. GAP-8 work must *populate* this fixture with realistic demographics and clinical history (male, age 45+, elevated BMI, blood pressure, etc.) to enable meaningful demo scenarios.

**Implication for Test 5:** Because gender = null, the mammogram-for-male safety rule cannot be triggered. Test 5 (mammogram absent) passes vacuously. Proper determinism testing of the safety validator requires GAP-8 to be completed first.

---

## Environment Notes

| Item | Value |
|---|---|
| OS | macOS darwin arm64 |
| Python (system) | 3.13.5 |
| Python (uv venv) | 3.12.12 |
| LLM Provider | TrollLLM proxy — `https://chat.trollllm.xyz` (Anthropic format) |
| LLM Model | `claude-sonnet-4.6` |
| BAML CLI | 0.220.0 (from Trae VSCode extension, not globally installed) |
| `baml-py` | 0.220.0 (manually added via `uv add`) |
| Existing audit log entries | 8 entries (all `pt-001`, archived as `audit_baseline_backup.jsonl`) |

---

## Readiness Assessment — Updated Priority Order

The baseline run revealed two new issues; one has since been resolved. Updated order:

| Priority | GAP | Status |
|---|---|---|
| **0-NEW** | **🆕 UNLISTED: `AuditLogger` buffer overflow** | Still open. Must fix before any server can run reliably after real recommendations. Add to gap list (fold into GAP-4). |
| **0-NEW** | ~~🆕 UNLISTED: BAML 400 from TrollLLM~~ | ✅ **RESOLVED** — `provider anthropic` fix applied. Tests 3a, 3b, 5 now pass. |
| 1 | **GAP-8** — Somchai W. fixture | Updated: issue is an *empty* skeleton record, not a missing record. Must **populate** with realistic data. |
| 2 | **GAP-1** — Security (hardcoded key + salt) | ✅ Confirmed |
| 3 | **GAP-2** — Enrichment pipeline wiring | ✅ **Unblocked** (BAML 400 resolved) |
| 4 | **GAP-3** — Deterministic safety validator | ✅ **Unblocked** (BAML 400 resolved); full mammogram test needs GAP-8 done first |
| 5 | **GAP-4** — Audit log 5-dimension fix | ✅ Confirmed; fix `_get_last_hash()` buffer bug here too |
| 6 | **GAP-5** — 5th MCP tool | As planned |
| 7 | **GAP-6** — 3 missing endpoints + CORS | ✅ Confirmed (all 404) |
| 8 | **GAP-7** — Monitoring fixture data | As planned |
| 9 | **GAP-9** — BAML multi-client | Use `provider anthropic` as `NavaveijAnthropicClient` for TrollLLM; `provider openai` for true OpenAI-spec endpoints |
| 10 | **GAP-10** — Dead code cleanup | As planned |

---

## Key Discussion Points for Dev Colleague

1. ~~**BAML 400 error**~~ — ✅ **Resolved.** `provider anthropic` is confirmed working with TrollLLM. No further action needed for the baseline.

2. **`AuditLogger._get_last_hash()` buffer size:** The 8KB limit is hardcoded. Given that full Signal Store context payloads are 20-25KB per entry, this will always fail after the first real run. Proposed fix: read all lines rather than the last 8KB tail. (Fold into GAP-4.)

3. **`baml-py` missing from `pyproject.toml`:** Should be added so `uv sync` works on a fresh checkout.

4. **`baml_client/` path:** Should `PYTHONPATH` be configured in a `.env` or startup script so `POC/` can find `baml_client/` without a symlink?

5. **GAP-8 scope revision:** `tok_hmac_56291047` (Somchai W.) returns a skeleton record with all-null data rather than a "record not found" error. The Signal Store fixture exists but is empty. GAP-8 must populate it with Somchai W.'s demographics, lab history, and clinical signals — not create it from scratch.

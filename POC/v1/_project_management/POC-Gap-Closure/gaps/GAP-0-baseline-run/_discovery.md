# GAP-0 — Discovery Notes

**Date:** 2026-03-17
**Environment:** macOS (darwin arm64)
**Python version:** 3.13.5 (system) / **3.12.12** (uv-managed venv inside POC/)

---

## Setup Steps

### 1. `uv sync` — Dependencies
```
cd POC/
uv sync
```
**Outcome:** ✅ All 44 packages installed successfully (Python 3.12.12 venv).
Notable: `uv` emitted a warning `VIRTUAL_ENV=.../.venv does not match the project environment path` on every run — this is benign (system venv conflict), not a failure.

### 2. .env Configuration
```
cp .env.example .env
```
**Provided by colleague:** TrollLLM proxy (OpenAI-compatible endpoint):
```
LLM_API_KEY=sk-trollllm-f0165ac7...
LLM_BASE_URL=https://chat.trollllm.xyz/v1
LLM_MODEL=claude-sonnet-4.6
LLM_PROVIDER=local
```
**Gap found (undocumented):** `.env.example` does NOT include `GOOGLE_API_KEY`, but the original `baml_src/clients.baml` uses `provider google-ai` and reads `env.GOOGLE_API_KEY`. Anyone following only `.env.example` with Gemini would have a missing variable. The colleague resolved this by using an OpenAI-compatible proxy instead, which required updating `clients.baml`.

### 3. BAML client generation

**Issue 1 — Version mismatch:** `generators.baml` specified `version "0.213.0"` but the installed `baml-cli` (bundled with the Trae VSCode extension) is `0.220.0`. Generation fails with:
```
Version mismatch: Generator version (0.213.0) !== the installed baml package version (0.220.0)
```
**Fix applied for baseline run:** Updated `generators.baml` version to `"0.220.0"`.

**Issue 2 — `baml-cli` not in PATH:** The CLI is not globally installed. It was located at:
```
/Users/nguyen.tran/.trae/extensions/boundary.baml-extension-0.220.0-darwin-arm64/dist/aarch64-apple-darwin/baml-cli
```
Must be called by full path. This is not documented in the README.

**Issue 3 — `clients.baml` hardcoded `provider google-ai`:** Since the colleague's `.env` uses an OpenAI-compatible endpoint, `clients.baml` was updated from `provider google-ai` to `provider openai` (reading `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`). Regenerated after.

**Issue 4 — `baml-py` not in pyproject.toml:** The generated `baml_client/__init__.py` requires `baml-py==0.220.0`, but `baml-py` is not listed as a dependency in `POC/pyproject.toml`. Manually added via `uv add baml-py==0.220.0`. This is a missing dependency that would block any fresh checkout.

**Issue 5 — `baml_client` location vs. import path:** `generators.baml` sets `output_dir "../"`, so `baml_client/` is generated at the **repo root** (`navaveij/`), not inside `POC/`. But all imports in `POC/src/` use `from baml_client.xxx import ...`, meaning `baml_client` must be on `sys.path`. A symlink was created as a workaround:
```
ln -s /navaveij/baml_client /navaveij/POC/baml_client
```

**BAML generation outcome:** ✅ Succeeded after all fixes above. `Wrote 14 files to baml_client`.

---

## Newly Discovered Bug (Not in gap-discovery.md)

### 🐛 UNLISTED BUG — `AuditLogger._get_last_hash()` 8KB buffer overflow

`audit.py:_get_last_hash()` reads only the last **8,192 bytes** of `audit.jsonl` to find the most recent entry's hash. The last (8th) audit entry is **24,495 bytes** — nearly 3× the buffer size. The tail-read returns a truncated JSON fragment, causing:

```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

This error fires **at import time** (inside `OrchestrationManager.__init__()` → `AuditLogger.__init__()`), which means:

- `src/api/main.py` **cannot start** as long as the existing `audit.jsonl` has this oversized entry
- The server crashes on startup, before handling any requests

**Workaround for this baseline run:** Archived the existing `audit.jsonl` (`audit_baseline_backup.jsonl`) and started with an empty log file.

**Impact on gap-discovery.md predictions:** The predicted Test 8 failure (`test_orchestrator.py` crashing on `get_patient_context`) actually hits this same `JSONDecodeError` **first** — at `OrchestrationManager()` instantiation, line 15 of `test_orchestrator.py`. The deprecated MCP tool is never reached.

---

## Deviations from README Test 3

The README specifies testing with:
```
{"patient_id": "tok_hmac_56291047"}   ← Somchai W. canonical patient
```
This token has **no Signal Store record** (GAP-8). The response is a 500 Internal Server Error.

For the Test 3a baseline (to capture the real API response structure for GAP-2 analysis), an existing synthesized patient was used:
```
{"patient_id": "pt-001"}   ← working patient token in existing audit log
```

---

## LLM Connectivity Status

The TrollLLM proxy (`https://chat.trollllm.xyz/v1`) responds correctly to direct `curl` requests:
```json
{"choices":[{"message":{"content":"Hi there! 👋"}}], "model":"claude-sonnet-4.6"}
```
However, BAML's `GenerateRecommendation()` call returns a **400 Bad Request** from the proxy. Investigation in progress — possibly a request format incompatibility (BAML may send `json_schema` response format or `tool_use` that TrollLLM does not support). The full recommendation flow (Test 3a) was blocked pending this investigation.

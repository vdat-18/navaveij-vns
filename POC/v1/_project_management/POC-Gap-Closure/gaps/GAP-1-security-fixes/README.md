# GAP-1 — Security Fixes

**Severity:** 🔴 Critical
**Execution order:** Step 1 — **do this before any other change or any git commit**
**Estimated effort:** 15 minutes
**Category:** Security

---

## Why This Matters

`POC/scripts/test_api.py` contains a live Google AI Studio API key hardcoded in source:
```python
api_key="AIzaSyAcgGGUvybk7xww0Yuk1uoiiKcU0MfQwW0",
```
A commented-out previous key is also present — which means a key rotation already happened with the old key left in git history.

`POC/src/shared/settings.py` line 51 hardcodes the HMAC secret salt used to generate patient tokens:
```python
patient_token_secret_salt: str = "navavej-clinical-recommendation-engine-secret-salt-2026"
```
Anyone who reads source code can reverse-engineer the HMAC pseudonymization, partially defeating the patient token de-identification scheme.

**Spec reference:** `component-inventory-solution-approach.md §2.4` — "API keys referenced via secret manager; no hardcoded keys."

---

## Dependencies

- **Depends on:** Nothing — do this first
- **Unblocks:** Everything else; no git commit should happen until this is clean

---

## Context Discovery

Read these files before making changes:

| File | What to look for |
|---|---|
| `POC/scripts/test_api.py` | Line 4–5: the hardcoded `AIzaSy...` key and the commented-out rotated key |
| `POC/src/shared/settings.py` | Line 51: `patient_token_secret_salt` field with hardcoded default value |
| `POC/.env.example` | Current structure — you will be adding two new env vars |

---

## What Already Exists (Don't Rewrite)

- The `settings.py` Pydantic settings class correctly reads from environment variables for all other secrets (`llm_api_key`, etc.) — the salt field just needs its default changed to `""` to follow the same pattern.
- `.env.example` already has the correct structure; you're only adding two missing entries.

---

## Step-by-Step Instructions

### 1a — Delete `POC/scripts/test_api.py`

```bash
rm POC/scripts/test_api.py
```

The file is a throwaway test script with no production use. It must not exist in the repository.

### 1b — Add to `.gitignore`

Open `.gitignore` (repo root) and add:

```
POC/scripts/
POC/scripts/test_api.py
```

This prevents future accidental commits of throwaway scripts under `scripts/`.

### 1c — Fix `POC/src/shared/settings.py` line 51

Change:
```python
patient_token_secret_salt: str = "navavej-clinical-recommendation-engine-secret-salt-2026"
```

To:
```python
patient_token_secret_salt: str = ""
```

The real value will be supplied via the `PATIENT_TOKEN_SECRET_SALT` environment variable (which Pydantic settings auto-maps). An empty default means the system fails visibly if the env var is missing rather than silently using a known-public value.

### 1d — Update `POC/.env.example`

Add these two lines (the actual values go in `.env`, never committed):
```
PATIENT_TOKEN_SECRET_SALT=navavej-clinical-recommendation-engine-secret-salt-2026
GOOGLE_API_KEY=        # Get from Google AI Studio
```

---

## Verification

```bash
# No API key in any source file
grep -r "AIzaSy" POC/

# No hardcoded salt in settings
grep "secret-salt" POC/src/shared/settings.py

# env.example has the new entries
grep "PATIENT_TOKEN_SECRET_SALT" POC/.env.example
grep "GOOGLE_API_KEY" POC/.env.example
```

All four commands: first two return **no output**, last two return the line.

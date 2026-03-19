# GAP-4 — Fix Audit Log 5-Dimension Structure

**Severity:** 🟠 Medium
**Execution order:** Step 5 — after GAP-2 (enrichment pipeline wired)
**Estimated effort:** 1–1.5 hours
**Category:** Audit / PDPA

---

## Why This Matters

The current `AuditLogger` writes a 4-dimension log using non-standard field names. The spec requires exactly **5 dimensions: Who, When, Where, What, Why**.

Current deviations:
1. `where` dimension is **entirely absent** — no service ID, no source IP, no request ID
2. `how` is used instead of `where` (and contains model info that belongs in `what`)
3. `timestamp` is used as a top-level key instead of `when`
4. `who` contains `patient_id` instead of the requesting clinician's `user_id` + `role`
5. `confidence` is a top-level orphan instead of being nested inside `what`

**POC evaluation impact:** 20% Security/Privacy criterion — Screen 3 (Access Monitoring) renders a 5-dimension drilldown view and a SHA-256 hash-chain verify button. If field names don't match the spec, the screen cannot be built.

---

## Dependencies

- **Depends on:** GAP-2 (enrichment pipeline provides `confidence_score` inside `ai_output`)
- **Unblocks:** GAP-6 (the `/api/audit-logs` endpoint serves these entries), Screen 3 frontend

---

## Context Discovery

Read these files before making changes:

| File | What to look for |
|---|---|
| `POC/src/orchestrator/logger/audit.py` | Lines 65–76: current `payload` dict structure; SHA-256 hash chain logic (this part is correct — preserve it) |
| `POC/src/api/main.py` | Current route handler — you will add `request_id` and `source_ip` generation here |
| `POC/src/orchestrator/core/manager.py` | `generate_recommendation()` signature — you will add `request_id` and `source_ip` parameters |
| `doc_outputs/architecture/AI/Recommendation Engine/v3/component-inventory-solution-approach.md` | Section §2.7: exact 5-dimension table — copy the content mapping from here |

---

## What Already Exists (Don't Rewrite)

- SHA-256 hash chain logic in `audit.py` is **correct** — `payload_str = json.dumps(payload, sort_keys=True)` → `sha256` → `current_hash`, `previous_hash` chaining. Preserve this exactly.
- The `audit_log_path` setting and JSONL append logic are correct.

---

## Required 5-Dimension Structure

```
who   → user_id + role + session_token         (the ROC staff member, not the patient)
when  → ISO 8601 UTC timestamp
where → service_id + source_ip + request_id   (THE MISSING DIMENSION)
what  → prompt + context + AI response + model_id + template_version + latency + safety_result + confidence_score
why   → patient_token (masked) + indication/reason code
```

---

## Step-by-Step Instructions

### 5a — Update `log_recommendation()` in `POC/src/orchestrator/logger/audit.py`

Update the method signature to accept `request_id` and `source_ip`:

```python
def log_recommendation(
    self,
    patient_id: str,
    masked_context: dict,
    ai_output: dict,
    model_id: str,
    request_id: str = "unknown",
    source_ip: str = "unknown",
) -> None:
```

Replace the `payload` dict with the correct 5-dimension structure:

```python
payload = {
    "who": {
        "user_id": patient_id,          # In POC: same as patient_token; production: clinician ID
        "role": "system",
        "session_token": "poc-session"
    },
    "when": timestamp,                  # ISO 8601 UTC string
    "where": {
        "service_id": "navaveij-inference",
        "source_ip": source_ip,
        "request_id": request_id,
    },
    "what": {
        "input_context_snapshot": masked_context,
        "ai_output_summary": {
            "tier": ai_output.get("ai_recommended_tier"),
            "add_on_count": len(ai_output.get("add_ons", [])),
        },
        "model_id": model_id,
        "model_provider": settings.llm_provider,
        "confidence_score": ai_output.get("confidence_score"),
        "safety_result": ai_output.get("safety_check", {}).get("is_safe"),
        "revoked_items": ai_output.get("safety_check", {}).get("revoked_items", []),
    },
    "why": {
        "reasoning_trace": ai_output.get("reasoning_trace"),
        "patient_token": patient_id,
        "indication": "annual_health_checkup_recommendation",
    },
    "previous_hash": self.last_hash,
}
```

> The SHA-256 hashing code below this dict must remain exactly as-is.

### 5b — Generate `request_id` and `source_ip` in `POC/src/api/main.py`

Update the route handler:

```python
import uuid
from fastapi import Request

@app.post("/api/recommend")
async def get_recommendation(request: RecommendationRequest, req: Request):
    request_id = str(uuid.uuid4())
    source_ip = req.client.host if req.client else "unknown"
    result = await manager.generate_recommendation(
        request.patient_token,
        request_id=request_id,
        source_ip=source_ip,
    )
    return result
```

### 5c — Thread `request_id` and `source_ip` through `OrchestrationManager`

Update `generate_recommendation()` in `manager.py` to accept these parameters and pass them to `audit_logger.log_recommendation()`.

---

## Verification

Run a recommendation, then inspect the last audit log entry:

```bash
tail -1 POC/logs/audit.jsonl | python -m json.tool
```

Check:
- Top-level keys are: `who`, `when`, `where`, `what`, `why`, `previous_hash`, `current_hash`
- `where.service_id == "navaveij-inference"`
- `where.request_id` matches UUID4 pattern (e.g. `"3f8a2b1c-..."`)
- `where.source_ip` is present
- `when` is an ISO 8601 string

**SHA-256 hash chain verify:**

```python
import json, hashlib

with open("POC/logs/audit.jsonl") as f:
    last_line = list(f)[-1].strip()

entry = json.loads(last_line)
e = {k: v for k, v in entry.items() if k != "current_hash"}
computed = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()
assert computed == entry["current_hash"], f"Hash mismatch: {computed} != {entry['current_hash']}"
print("Hash chain OK")
```

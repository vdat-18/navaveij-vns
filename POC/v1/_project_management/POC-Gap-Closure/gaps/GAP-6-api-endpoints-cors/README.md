# GAP-6 — Add Missing API Endpoints + CORS

**Severity:** 🟠 Medium
**Execution order:** Step 8 — after GAP-5 (timeline tool exists)
**Estimated effort:** 1–1.5 hours
**Category:** API

---

## Why This Matters

The current API has only one data endpoint (`POST /recommend`) at the wrong path. Three of four required demo endpoints are missing, and there is no CORS middleware. The Vite frontend runs at `http://localhost:5173` — without CORS, **every API call will be blocked by the browser**.

| Required endpoint | Status | Blocks |
|---|---|---|
| `POST /api/recommend` | Wrong path (`/recommend`) + wrong field name (`patient_id` not `patient_token`) | Screen 1 |
| `GET /api/timeline/{patient_token}` | Missing | Screen 2 |
| `GET /api/monitoring-snapshot` | Missing | Screen 3 |
| `GET /api/audit-logs` | Missing | Screen 3 |

---

## Dependencies

- **Depends on:** GAP-5 (`load_event_timeline_record()` exists), GAP-7 (`monitoring.json` exists), GAP-4 (`where.service_id` audit log structure)
- **Unblocks:** All frontend phases (2–6)

---

## Context Discovery

Read these files before making changes:

| File | What to look for |
|---|---|
| `POC/src/api/main.py` | Current routes, `RecommendationRequest` model, how `manager` is instantiated |
| `POC/src/shared/settings.py` | `audit_log_path` field — used by the `/api/audit-logs` endpoint |
| `POC/src/mcp_server/utils.py` | `load_event_timeline_record()` (added in GAP-5) |
| `POC/src/orchestrator/core/manager.py` | `generate_recommendation()` signature — you are changing its parameter from `patient_id` to `patient_token` |

---

## What Already Exists (Don't Rewrite)

- The `OrchestrationManager` instantiation and singleton pattern in `main.py` — keep it
- The `GET /` health check endpoint — keep it
- The `AuditLogger` and its JSONL file at `settings.audit_log_path` — the `/api/audit-logs` endpoint just reads this file

---

## Step-by-Step Instructions

### 8a — Add CORS middleware (add this first, before any route definitions)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8b — Update `RecommendationRequest` model

```python
class RecommendationRequest(BaseModel):
    patient_token: str          # was: patient_id
```

### 8c — Rename + update the recommend route

Rename from `POST /recommend` to `POST /api/recommend` and add `request_id` + `source_ip` generation (required by GAP-4):

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

### 8d — Add `GET /api/timeline/{patient_token}`

```python
@app.get("/api/timeline/{patient_token}")
async def get_timeline(patient_token: str):
    from src.mcp_server.utils import load_event_timeline_record
    record = load_event_timeline_record(patient_token)
    if not record:
        return {"error": "Timeline not found", "patient_token": patient_token}
    return record
```

### 8e — Add `GET /api/monitoring-snapshot`

```python
import json
from pathlib import Path

@app.get("/api/monitoring-snapshot")
async def get_monitoring_snapshot():
    monitoring_file = Path("assets/synthesis/canonical/monitoring.json")
    with open(monitoring_file, encoding="utf-8") as f:
        data = json.load(f)
    return data["snapshot"]
```

### 8f — Add `GET /api/audit-logs`

```python
from fastapi import Query

@app.get("/api/audit-logs")
async def get_audit_logs(
    user_id: str | None = Query(None),
    patient_token_prefix: str | None = Query(None),
    action_type: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    log_file = Path(settings.audit_log_path)
    entries = []
    if log_file.exists():
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    # Apply filters
    if user_id:
        entries = [e for e in entries if e.get("who", {}).get("user_id") == user_id]
    if patient_token_prefix:
        entries = [e for e in entries
                   if str(e.get("why", {}).get("patient_token", "")).startswith(patient_token_prefix)]
    if start_date:
        entries = [e for e in entries if e.get("when", "") >= start_date]
    if end_date:
        entries = [e for e in entries if e.get("when", "") <= end_date]

    return {"entries": entries, "count": len(entries)}
```

> Filter field names (`who.user_id`, `why.patient_token`, `when`) must match the new 5-dimension audit log structure from GAP-4.

---

## Verification

Start the server and run each test:

```bash
# Recommendation (renamed path + new field name)
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_token": "tok_hmac_56291047"}'
# Expect: HTTP 200 with full recommendation

# Timeline
curl http://localhost:8000/api/timeline/tok_hmac_56291047
# Expect: JSON with "diagnoses" array (length 4)

# Monitoring snapshot
curl http://localhost:8000/api/monitoring-snapshot
# Expect: JSON with "active_users_now", "sessions_today", "alert_counts"

# Audit logs (unfiltered)
curl "http://localhost:8000/api/audit-logs"
# Expect: {"entries": [...], "count": N}

# Audit logs (date filtered)
curl "http://localhost:8000/api/audit-logs?start_date=2026-03-16"
# Expect: only entries with "when" >= "2026-03-16"

# CORS preflight check (from browser console at http://localhost:5173)
fetch("http://localhost:8000/api/recommend", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({patient_token: "tok_hmac_56291047"})
}).then(r => r.json()).then(console.log)
# Expect: no CORS error, response logged
```

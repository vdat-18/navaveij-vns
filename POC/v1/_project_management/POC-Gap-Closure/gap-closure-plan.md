# Gap Closure Plan — POC Backend

**Date:** 2026-03-16
**Input:** `gap-discovery.md`
**Dependency:** All steps here must be complete before frontend work (Phases 2–6 of `plan.md`) can begin.

---

## Delivery Requirements

When all gaps are closed, `POST /recommend {"patient_token": "tok_hmac_56291047"}` must return a **Stage 2 `RecommendationOutput`** that is fully compliant with `recommendation-output-schema.md`. Specifically:

| Field | Required Value | Source |
|---|---|---|
| `ai_recommended_tier` | Any of Standard/Advanced/Premium (AI decides) | BAML output |
| `tier_deviation_justification` | Non-null iff AI tier ≠ rule tier | BAML output |
| `rule_preliminary_tier` | `"Advanced"` | System-injected via OutputEnricher |
| `resolved_package.package_name` | `"Platinum — Men"` | System-injected via OutputEnricher |
| `resolved_package.price_thb` | `8700` | System-injected via OutputEnricher |
| `confidence_score` | `0.823` (deterministic) | ConfidenceCalibrator |
| `confidence_tier` | `"High"` | ConfidenceCalibrator |
| `recommendation_source` | `"AI"` | System-injected |
| `add_ons[].label` | Human-readable label | System-injected via OutputEnricher |
| `add_ons[].navavej_product.price_thb` | Numeric price in THB | System-injected via OutputEnricher |
| `reasoning_trace` | ≥150 words, changes on re-run | BAML output |
| `communication_script` | 5 sub-fields | BAML output |
| `patient_high_alert.critical_signals` | Non-empty array | System-injected |
| `patient_high_alert.missing_data_alerts` | Array of `{signal_id, description}` | System-injected |
| `mammogram` in `add_ons` for male patient | **Must not appear** | Deterministic Safety Validator |
| Audit log entry dimensions | `who`, `when`, `where`, `what`, `why` | AuditLogger |
| Audit log `where.service_id` | `"navaveij-inference"` | AuditLogger |
| Audit log `where.request_id` | UUID per request | AuditLogger |

---

## Execution Steps (Ordered)

### Step 1 — GAP-1: Security Fixes
**Do this before any other change or any git commit.**

**1a. Delete `POC/scripts/test_api.py`**
The file contains a hardcoded live Google AI Studio API key. Delete the file entirely.

**1b. Add to `.gitignore`**
Add `POC/scripts/test_api.py` (and `POC/scripts/`) to `.gitignore` to prevent future accidental commits of throwaway scripts.

**1c. Fix `POC/src/shared/settings.py` line 51**
Change:
```python
patient_token_secret_salt: str = "navavej-clinical-recommendation-engine-secret-salt-2026"
```
To:
```python
patient_token_secret_salt: str = ""
```

**1d. Add to `POC/.env.example`**
```
PATIENT_TOKEN_SECRET_SALT=navavej-clinical-recommendation-engine-secret-salt-2026
GOOGLE_API_KEY=        # Get from Google AI Studio
```

**Verification:** `grep -r "AIzaSy" POC/` returns no matches. `grep "secret-salt" POC/src/shared/settings.py` returns no matches (only the empty default).

---

### Step 2 — GAP-8: Create Canonical Demo Patient Record
**Do this second — it unblocks all integration testing from Step 3 onwards.**

**Create `assets/synthesis/canonical/record_somchai.json`**

This is a data transcription task. Copy the complete Somchai W. example from `signal-store-contract.md` into a JSON file with the following top-level structure:
```json
{
  "patient_token": "tok_hmac_56291047",
  "hard_constraints": { ... },
  "clinical_signals": { ... },
  "biomarker_trends": { ... },
  "_meta": {
    "signal_coverage": 0.667,
    "data_completeness_ratio": 0.889,
    "populated_fields": 40,
    "total_key_fields": 45,
    "signals_fired_count": 22,
    "applicable_signals_count": 33
  }
}
```

Key values from the spec:
- `hard_constraints.eligibility_exclusions`: `["mammogram", "pap_smear_hpv", "cervical_cancer_hpv_screen", "hpv_vaccine", "dexa_bone_density", "breast_ultrasound"]`
- `clinical_signals.rule_preliminary_tier`: `"Advanced"`
- `clinical_signals.signals_fired`: 22 entries (full list in signal-store-contract.md)
- `clinical_signals.applicable_signals`: 33 entries
- `biomarker_trends.labs.fbs`: `{current_value: 108, velocity_per_year: 6, ...}`
- `biomarker_trends.labs.hba1c`: `{current_value: 6.1, ...}`

No code changes required — `load_signal_store_record()` in `utils.py` already globs `**/record_*.json` recursively, so the new file is found automatically.

**Verification:** `python -c "from src.mcp_server.utils import load_signal_store_record; print(load_signal_store_record('tok_hmac_56291047')['patient_token'])"` prints `tok_hmac_56291047`.

---

### Step 3 — GAP-2: Wire ConfidenceCalibrator + OutputEnricher + PIIRehydrator

**3a. Extend `WorkflowContext` in `POC/src/orchestrator/workflows/base.py`**

Add two new fields to the `WorkflowContext` Pydantic model:
```python
signal_store_meta: dict = {}    # from record["_meta"]
ruleset_response: dict = {}     # from get_program_ruleset MCP tool response
```
These allow the manager to access them after `workflow.execute()` returns.

**3b. Update `ClinicalReasoningWorkflow._generate_recommendation()` in `POC/src/orchestrator/workflows/clinical.py`**

After the BAML call (after the `context.ai_output = {...}` block, roughly line 125), add:
```python
# Load Signal Store record for metadata
from src.mcp_server.utils import load_signal_store_record
record = load_signal_store_record(patient_token)
signal_store_meta = record.get("_meta", {}) if record else {}

# Compute confidence score
from src.orchestrator.validation.confidence_calibrator import ConfidenceCalibrator
calibrator = ConfidenceCalibrator()
clinical_signals = context.raw_context.get("get_clinical_signals", {})
confidence_score = calibrator.compute_confidence_score(
    signals_fired_count=len(clinical_signals.get("signals_fired", [])),
    applicable_signals_count=len(clinical_signals.get("applicable_signals", [])),
    data_completeness_ratio=signal_store_meta.get("data_completeness_ratio", 0.0),
    ai_recommended_tier=context.ai_output["ai_recommended_tier"],
    rule_preliminary_tier=clinical_signals.get("rule_preliminary_tier", "Standard"),
)
context.ai_output["confidence_score"] = confidence_score
context.ai_output["confidence_tier"] = calibrator.compute_confidence_tier(confidence_score)

# Store metadata for manager
context.signal_store_meta = signal_store_meta
context.ruleset_response = context.raw_context.get("get_program_ruleset", {})
```

**3c. Update `OrchestrationManager.generate_recommendation()` in `POC/src/orchestrator/core/manager.py`**

After `context = await workflow.execute(patient_id)` and before the safety guard call, add:
```python
# Stage 2 enrichment
from src.orchestrator.enrichment.output_enricher import OutputEnricher
enricher = OutputEnricher()
context.ai_output = enricher.enrich_output(
    ai_output=context.ai_output,
    clinical_signals=context.raw_context.get("get_clinical_signals", {}),
    ruleset_response=context.ruleset_response,
    signal_store_meta=context.signal_store_meta,
)
```

After the audit logger call, add PII rehydration:
```python
# PII Rehydration — restore real patient identifiers
from src.orchestrator.privacy.rehydration import PIIRehydrator
rehydrator = PIIRehydrator(workflow.masker.get_rehydration_map())
return rehydrator.rehydrate(context.ai_output)
```
Note: `workflow` must be accessible here — currently `workflow` is a local variable inside the `async with` block. Pass `workflow.masker` to the manager or store the masker on the context.

**3d. Fix `patient_high_alert` in `POC/src/orchestrator/enrichment/output_enricher.py` (line 93)**

Replace:
```python
"patient_high_alert": len(clinical_signals.get("missing_signals", [])) > 5,
```
With:
```python
"patient_high_alert": {
    "critical_signals": [
        s for s in ["fbs_prediabetes", "ldl_elevated", "colonoscopy_overdue",
                    "htn_active", "bmi_overweight", "ckd_g2"]
        if s in clinical_signals.get("signals_fired", [])
    ],
    "missing_data_alerts": [
        {"signal_id": s, "description": f"No data available for signal: {s}"}
        for s in clinical_signals.get("missing_signals", [])
    ],
},
```
The critical signal IDs above are the subset of `signals_fired` that qualify as "high-priority alerts" per the spec. For the POC, this hardcoded list is sufficient; production would read this from the Ruleset Store.

**Verification:** `POST /recommend {"patient_token": "tok_hmac_56291047"}` returns `confidence_score: 0.823`, `rule_preliminary_tier: "Advanced"`, `resolved_package.package_name: "Platinum — Men"`, and `add_ons[0].label` is a non-empty string.

---

### Step 4 — GAP-3: Deterministic Safety Validator

**Refactor `POC/src/orchestrator/safety/validator.py`**

Change `validate()` to accept a third parameter `hard_constraints: dict` and run a deterministic check first:

```python
from src.orchestrator.safety.rules import GENDER_EXCLUSIONS

class ClinicalSafetyGuard:
    def __init__(self, audit_logger=None):
        self.audit_logger = audit_logger  # for conflict event logging

    def _run_deterministic_check(
        self, ai_output: dict, hard_constraints: dict
    ) -> tuple[dict, list[str]]:
        """Layer 1: Silently revoke any add-on violating hard constraints."""
        eligibility_exclusions = hard_constraints.get("eligibility_exclusions", [])
        clean_add_ons = []
        revoked = []
        for add_on in ai_output.get("add_ons", []):
            item_code = add_on.get("item_code", "")
            if item_code in eligibility_exclusions:
                revoked.append(item_code)
                logger.warning(f"Safety Rule Validator: REVOKED {item_code} (eligibility exclusion)")
            else:
                clean_add_ons.append(add_on)
        ai_output["add_ons"] = clean_add_ons
        return ai_output, revoked

    async def validate(
        self, ai_output: dict, raw_context: dict, hard_constraints: dict
    ) -> dict:
        # Layer 1: Deterministic — runs first, non-negotiable
        ai_output, revoked = self._run_deterministic_check(ai_output, hard_constraints)
        if revoked and self.audit_logger:
            # Log conflict events synchronously
            self.audit_logger.log_safety_conflict(revoked_items=revoked, ...)

        # Layer 2: LLM critic — advisory only, does not gate output
        result = await b.ValidateRecommendation(
            context=json.dumps(raw_context, indent=2),
            recommendation=json.dumps(ai_output, indent=2)
        )
        return {
            "is_safe": result.is_safe,
            "critic_score": result.critic_score,
            "findings": result.findings,
            "revoked_items": revoked,
        }
```

**Update `OrchestrationManager`** to pass `hard_constraints` to the safety guard:
```python
safety_result = await self.safety_guard.validate(
    context.ai_output,
    context.raw_context,
    hard_constraints=context.raw_context.get("get_hard_constraints", {})
)
```

**Verification:** Manually inject `"mammogram"` into the AI output's `add_ons` list in a test → verify it is absent from the final returned output. Verify `audit.jsonl` contains a conflict event entry.

---

### Step 5 — GAP-4: Fix Audit Log 5-Dimension Structure

**Update `POC/src/orchestrator/logger/audit.py`**

Update `log_recommendation()` signature:
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

Replace the `payload` dict:
```python
payload = {
    "who": {
        "user_id": patient_id,
        "role": "system",
        "session_token": "poc-session"
    },
    "when": timestamp,
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

**Update `POC/src/api/main.py`** to generate and pass `request_id` and `source_ip`:
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

**Update `OrchestrationManager.generate_recommendation()`** to accept and thread through `request_id` and `source_ip`.

**Verification:** Run a recommendation; open `logs/audit.jsonl`; confirm entry has `who`, `when`, `where`, `what`, `why` as top-level keys; confirm `where.request_id` is a UUID string; confirm `where.service_id == "navaveij-inference"`.

---

### Step 6 — GAP-5: 5th MCP Tool `get_patient_event_timeline`

**6a. Create `assets/synthesis/canonical/somchai_event_timeline.json`**

Transcribe the full example response from `event-timeline-contract.md` for `tok_hmac_56291047`:
```json
{
  "patient_token": "tok_hmac_56291047",
  "timeline_span": {
    "earliest_event_date": "2019-06-12",
    "latest_event_date": "2026-03-11",
    "span_years": 6.7
  },
  "diagnoses": [ /* 4 entries: Hyperlipidaemia, Prediabetes, Hypertension, Hyperuricaemia */ ],
  "hospitalizations": [],
  "significant_lab_events": [ /* 5 entries with LOINC codes */ ],
  "screening_procedure_history": [ /* 1 entry: Colonoscopy 2019-06-12 */ ],
  "medication_changes": [ /* 2 entries: Atorvastatin 2022, Amlodipine 2025 */ ],
  "_pipeline_meta": {
    "generated_at": "2026-03-11T08:00:00Z",
    "pipeline_run_id": "run_20260311_001"
  }
}
```

**6b. Add `load_event_timeline_record()` to `POC/src/mcp_server/utils.py`**

```python
CANONICAL_TIMELINE_DIR = Path("assets/synthesis/canonical")

def load_event_timeline_record(patient_token: str) -> dict | None:
    """Load Event Timeline record by patient_token."""
    timeline_file = CANONICAL_TIMELINE_DIR / "somchai_event_timeline.json"
    if not timeline_file.exists():
        logger.warning(f"Timeline file not found: {timeline_file}")
        return None
    with open(timeline_file, encoding="utf-8") as f:
        record = json.load(f)
    if record.get("patient_token") == patient_token:
        return record
    logger.warning(f"No timeline record for token: {patient_token}")
    return None
```

**6c. Create `POC/src/mcp_server/tools/event_timeline.py`**

```python
"""MCP Tool: get_patient_event_timeline"""
import json
from src.mcp_server.utils import load_event_timeline_record

async def get_patient_event_timeline(patient_token: str) -> str:
    """Return the longitudinal clinical event timeline for UI display (Screen 2).

    This tool is display-only and is NOT fed to the AI inference model.
    Args:
        patient_token: HMAC-SHA256 pseudonymous patient identifier
    Returns:
        JSON string containing EventTimelineResponse
    """
    record = load_event_timeline_record(patient_token)
    if not record:
        return json.dumps({"error": f"No timeline found for token: {patient_token}"})
    return json.dumps(record)
```

**6d. Register in `POC/src/mcp_server/server.py`**

```python
from src.mcp_server.tools.event_timeline import get_patient_event_timeline
mcp.tool()(get_patient_event_timeline)
```

**Verification:** Call `get_patient_event_timeline("tok_hmac_56291047")` via MCP → returns JSON with `diagnoses` array of length 4.

---

### Step 7 — GAP-7: Create Monitoring Fixture Data

**Create `assets/synthesis/canonical/monitoring.json`**

Structure (pulled from `access-monitoring-contract.md` examples):
```json
{
  "snapshot": {
    "snapshot_id": "snap_20260316_001",
    "generated_at": "2026-03-16T09:00:00Z",
    "active_users_now": 7,
    "sessions_today": 43,
    "patient_records_accessed_today": 118,
    "ai_recommendations_generated_today": 31,
    "alert_counts": {
      "critical": 0, "high": 2, "medium": 5, "low": 11
    },
    "safety_validator_failures_today": 0,
    "top_active_departments": ["Cardiology", "Internal Medicine", "Oncology"]
  },
  "anomaly_alerts": [
    {
      "alert_id": "anm-20260314-001",
      "severity": "High",
      "alert_type": "high_volume",
      "user_id": "usr_supawan_k",
      "description": "User accessed 18 records in one session (4.3× baseline of 4.2)",
      "detected_at": "2026-03-14T14:23:00Z",
      "status": "Open",
      "baseline_value": 4.2,
      "observed_value": 18,
      "ratio": 4.3
    }
    // + 2–3 more alerts (medium/low severity)
  ],
  "roles": [
    {
      "role_id": "physician",
      "display_name": "Physician",
      "permissions": { /* per access-monitoring-contract.md §RBAC */ }
    }
    // physician, nurse, pharmacist, admin, dpo
  ],
  "mapping_table": [
    {
      "mapping_id": "map-001",
      "his_code": "HIS-LAB-0042",
      "target_system": "LOINC",
      "target_code": "1558-6",
      "display_name": "Fasting Glucose",
      "mapping_type": "exact",
      "status": "active"
    }
    // + 9 more mappings covering key LOINC codes from fhir-discovery-report.md
  ]
}
```

Populate with exact values from `access-monitoring-contract.md` examples where available.

**Verification:** File parses as valid JSON; `snapshot.alert_counts.high == 2`.

---

### Step 8 — GAP-6: Add Missing API Endpoints + CORS

**Update `POC/src/api/main.py`**

**8a. Add CORS middleware** (before any route definitions):
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

**8b. Update `RecommendationRequest`** to accept `patient_token`:
```python
class RecommendationRequest(BaseModel):
    patient_token: str
```
Update `OrchestrationManager.generate_recommendation()` to accept `patient_token` directly (or add a thin wrapper that accepts a token and looks up the patient).

**8c. Rename route** from `/recommend` to `/api/recommend`.

**8d. Add `GET /api/timeline/{patient_token}`:**
```python
import json
from pathlib import Path

@app.get("/api/timeline/{patient_token}")
async def get_timeline(patient_token: str):
    from src.mcp_server.utils import load_event_timeline_record
    record = load_event_timeline_record(patient_token)
    if not record:
        return {"error": "Timeline not found", "patient_token": patient_token}
    return record
```

**8e. Add `GET /api/monitoring-snapshot`:**
```python
@app.get("/api/monitoring-snapshot")
async def get_monitoring_snapshot():
    monitoring_file = Path("assets/synthesis/canonical/monitoring.json")
    with open(monitoring_file, encoding="utf-8") as f:
        data = json.load(f)
    return data["snapshot"]
```

**8f. Add `GET /api/audit-logs`:**
```python
from fastapi import Query
from datetime import datetime

@app.get("/api/audit-logs")
async def get_audit_logs(
    user_id: str | None = Query(None),
    patient_token_prefix: str | None = Query(None),
    action_type: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    resource_type: str | None = Query(None),
):
    log_file = Path(settings.audit_log_path)
    entries = []
    if log_file.exists():
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))

    # Apply filters
    if user_id:
        entries = [e for e in entries if e.get("who", {}).get("user_id") == user_id]
    if patient_token_prefix:
        entries = [e for e in entries if str(e.get("why", {}).get("patient_token", "")).startswith(patient_token_prefix)]
    if start_date:
        entries = [e for e in entries if e.get("when", "") >= start_date]
    if end_date:
        entries = [e for e in entries if e.get("when", "") <= end_date]

    return {"entries": entries, "count": len(entries)}
```

**Verification:**
- `curl http://localhost:8000/api/timeline/tok_hmac_56291047` returns JSON with `diagnoses` key
- `curl http://localhost:8000/api/monitoring-snapshot` returns JSON with `active_users_now`
- `curl "http://localhost:8000/api/audit-logs?start_date=2026-03-01"` returns filtered entries
- `OPTIONS http://localhost:8000/api/recommend` returns `Access-Control-Allow-Origin: http://localhost:5173`

---

### Step 9 — GAP-9: BAML Multi-Client Configuration

**Update `baml_src/clients.baml`**

Add clients for OpenAI-compatible and Anthropic providers alongside the existing Google client:

```
// Google AI (default for cloud demo)
client<llm> NavaveijGoogleClient {
  provider google-ai
  options {
    api_key env.GOOGLE_API_KEY
    model env.LLM_MODEL
  }
}

// OpenAI-compatible (local LLM, OpenAI, Azure OpenAI)
client<llm> NavaveijOpenAIClient {
  provider openai
  options {
    api_key env.LLM_API_KEY
    base_url env.LLM_BASE_URL
    model env.LLM_MODEL
  }
}

// Anthropic Claude
client<llm> NavaveijAnthropicClient {
  provider anthropic
  options {
    api_key env.ANTHROPIC_API_KEY
    model env.LLM_MODEL
  }
}

// Active client — change this line to switch providers without redeployment
client<llm> NavaveijClient = env.LLM_CLIENT_ALIAS ?? NavaveijOpenAIClient
```

Update `.env.example`:
```
# Set LLM_CLIENT_ALIAS to switch providers: NavaveijGoogleClient | NavaveijOpenAIClient | NavaveijAnthropicClient
LLM_CLIENT_ALIAS=NavaveijOpenAIClient
```

Run `baml-cli generate` after editing to regenerate `baml_client/`.

**Verification:** Set `LLM_CLIENT_ALIAS=NavaveijGoogleClient` in `.env`, run recommendation → `what.model_id` in audit log shows a Gemini model name. Change to `NavaveijAnthropicClient` + set `ANTHROPIC_API_KEY` → `model_id` shows a Claude model name.

---

### Step 10 — Cleanup: Deprecate `ClinicalOrchestrator`

**Update `POC/src/orchestrator/agents/orchestrator.py`** — add deprecation notice at top of class docstring:
```python
class ClinicalOrchestrator:
    """DEPRECATED — Use OrchestrationManager + ClinicalReasoningWorkflow instead.

    This class was an earlier standalone implementation. It is preserved for
    reference only and is not called by any production code path. Do not use.
    The canonical API path is: OrchestrationManager → ClinicalReasoningWorkflow.
    """
```

**Update `POC/test_orchestrator.py`** — replace `ClinicalOrchestrator` usage with `OrchestrationManager`:
```python
from src.orchestrator.core.manager import OrchestrationManager
orchestrator = OrchestrationManager()
result = await orchestrator.generate_recommendation("tok_hmac_56291047")
```

---

## Files Changed / Created Summary

| File | Change Type | Step |
|---|---|---|
| `POC/scripts/test_api.py` | **Delete** | Step 1 |
| `POC/src/shared/settings.py` | Edit: empty salt default | Step 1 |
| `POC/.env.example` | Edit: add `PATIENT_TOKEN_SECRET_SALT`, `GOOGLE_API_KEY` | Step 1 |
| `assets/synthesis/canonical/record_somchai.json` | **New file** — Somchai W. Signal Store record | Step 2 |
| `POC/src/orchestrator/workflows/base.py` | Edit: add `signal_store_meta`, `ruleset_response` to `WorkflowContext` | Step 3 |
| `POC/src/orchestrator/workflows/clinical.py` | Edit: wire `ConfidenceCalibrator`; store meta on context | Step 3 |
| `POC/src/orchestrator/core/manager.py` | Edit: wire `OutputEnricher`, `PIIRehydrator`; add `request_id`/`source_ip` params | Steps 3, 4, 5 |
| `POC/src/orchestrator/enrichment/output_enricher.py` | Edit: fix `patient_high_alert` to structured object | Step 3 |
| `POC/src/orchestrator/safety/validator.py` | Edit: add deterministic Layer 1; keep LLM critic as Layer 2 | Step 4 |
| `POC/src/orchestrator/logger/audit.py` | Edit: add `where` dimension; fix 5-dim structure | Step 5 |
| `assets/synthesis/canonical/somchai_event_timeline.json` | **New file** — Somchai W. event timeline fixture | Step 6 |
| `POC/src/mcp_server/utils.py` | Edit: add `load_event_timeline_record()` | Step 6 |
| `POC/src/mcp_server/tools/event_timeline.py` | **New file** — 5th MCP tool | Step 6 |
| `POC/src/mcp_server/server.py` | Edit: register `get_patient_event_timeline` | Step 6 |
| `assets/synthesis/canonical/monitoring.json` | **New file** — monitoring snapshot + anomaly alerts | Step 7 |
| `POC/src/api/main.py` | Edit: CORS; 3 new endpoints; updated request schema; `request_id`/`source_ip` | Steps 5, 8 |
| `baml_src/clients.baml` | Edit: add OpenAI-compatible + Anthropic clients | Step 9 |
| `POC/src/orchestrator/agents/orchestrator.py` | Edit: add `# DEPRECATED` docstring | Step 10 |
| `POC/test_orchestrator.py` | Edit: use `OrchestrationManager` instead | Step 10 |

---

## Full End-to-End Validation Checklist

Run these tests in order after all steps are complete. All must pass before frontend (Phase 2) begins.

### Security
- [ ] `grep -r "AIzaSy" POC/` → no output
- [ ] `grep "secret-salt" POC/src/shared/settings.py` → no output (only `""` default)
- [ ] `cat POC/.env.example | grep PATIENT_TOKEN_SECRET_SALT` → line present

### Demo patient
- [ ] `python -c "from src.mcp_server.utils import load_signal_store_record; r=load_signal_store_record('tok_hmac_56291047'); print(r['patient_token'], r['clinical_signals']['rule_preliminary_tier'])"` → prints `tok_hmac_56291047 Advanced`

### Full recommendation output
- [ ] `curl -X POST http://localhost:8000/api/recommend -H "Content-Type: application/json" -d '{"patient_token":"tok_hmac_56291047"}'` returns HTTP 200
- [ ] Response contains `confidence_score` ≈ 0.823
- [ ] Response contains `confidence_tier: "High"`
- [ ] Response contains `rule_preliminary_tier: "Advanced"`
- [ ] Response contains `resolved_package.package_name: "Platinum — Men"`
- [ ] Response contains `add_ons[0].label` (non-empty string)
- [ ] Response contains `add_ons[0].navavej_product.price_thb` (integer)
- [ ] Response contains `reasoning_trace` (≥150 words)
- [ ] Response contains `communication_script.opening` (non-empty)
- [ ] Response contains `patient_high_alert.critical_signals` (non-empty array)
- [ ] Re-run returns different `reasoning_trace` (confirms live AI call, not cached)
- [ ] `mammogram` does NOT appear in `add_ons` (deterministic safety revocation for male patient)

### Audit log
- [ ] New entry in `POC/logs/audit.jsonl` after recommendation call
- [ ] Entry has top-level keys: `who`, `when`, `where`, `what`, `why`, `previous_hash`, `current_hash`
- [ ] `where.service_id == "navaveij-inference"`
- [ ] `where.request_id` matches a UUID4 pattern
- [ ] `where.source_ip` is present
- [ ] SHA-256 verify: `import json, hashlib; entry = json.loads(last_line); e = {k:v for k,v in entry.items() if k != "current_hash"}; assert hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest() == entry["current_hash"]`

### Timeline endpoint
- [ ] `curl http://localhost:8000/api/timeline/tok_hmac_56291047` returns HTTP 200
- [ ] Response contains `diagnoses` array with length 4
- [ ] Response contains `significant_lab_events` array with length 5
- [ ] Response contains `medication_changes` array with length 2

### Monitoring endpoints
- [ ] `curl http://localhost:8000/api/monitoring-snapshot` returns HTTP 200
- [ ] Response contains `active_users_now`, `sessions_today`, `alert_counts`
- [ ] `curl "http://localhost:8000/api/audit-logs"` returns `{"entries": [...], "count": N}`
- [ ] `curl "http://localhost:8000/api/audit-logs?start_date=2026-03-16"` returns only entries from 2026-03-16 onwards

### CORS
- [ ] From browser console at `http://localhost:5173`: `fetch("http://localhost:8000/api/recommend", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({patient_token:"tok_hmac_56291047"})})` resolves without CORS error

### Pluggable AI (Step 9)
- [ ] Set `LLM_CLIENT_ALIAS=NavaveijGoogleClient` + `GOOGLE_API_KEY=...` in `.env` → recommendation returns HTTP 200; `what.model_id` in audit log contains "gemini"
- [ ] Set `LLM_CLIENT_ALIAS=NavaveijOpenAIClient` + local LLM running → recommendation returns HTTP 200; `what.model_id` in audit log contains the local model name

---

## Definition of Done

Phase 1 is **complete** when:
1. All 10 validation checklist items above pass
2. No hardcoded secrets remain in any source file
3. `POST /api/recommend` with the Somchai W. token returns a fully enriched Stage 2 response
4. All 4 API endpoints respond correctly
5. The deterministic safety revocation can be demonstrated (mammogram test)
6. The audit log passes the 5-dimension structure check and SHA-256 hash chain verify

At that point, frontend work (Phase 2: Vite scaffold → Phase 3: Screen 1 → Phase 4: Screen 2 → Phase 5: Screen 3 → Phase 6: integration) can begin as specified in `doc_outputs/architecture/AI/Recommendation Engine/v3/plan.md`.

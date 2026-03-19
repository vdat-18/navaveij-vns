# GAP-5 — Add 5th MCP Tool: `get_patient_event_timeline`

**Severity:** 🟠 Medium
**Execution order:** Step 6 — after GAP-2 (enrichment pipeline wired)
**Estimated effort:** 1.5–2 hours
**Category:** MCP

---

## Why This Matters

Only 4 MCP tools are registered. The spec requires a 5th:

```
get_patient_event_timeline(patient_token: str) → EventTimelineResponse
```

This tool is the **sole data source** for:
- `GET /api/timeline/{patient_token}` (backend endpoint — GAP-6)
- Screen 2 (Trend & Timeline) Panel D — Clinical Event Timeline

Without it, the entire Timeline screen cannot be built, and the Phase 4 frontend work is blocked.

> **Important architectural note:** This tool is **display-only**. It is called by the API endpoint `/api/timeline/{patient_token}` and surfaced on Screen 2. It is **NOT** fed to the AI inference model. The AI gets data from the other 4 tools only.

**POC evaluation impact:** 20% UX/XAI criterion (Screen 2 is one of the three evaluated screens)

---

## Dependencies

- **Depends on:** GAP-2 (understand the codebase structure first)
- **Unblocks:** GAP-6 (`GET /api/timeline/{patient_token}` endpoint)

---

## Context Discovery

Read these files before writing any code:

| File | What to look for |
|---|---|
| `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/event-timeline-contract.md` | Full spec for `EventTimelineResponse` schema + complete Somchai W. example response — this is the data you transcribe |
| `POC/src/mcp_server/tools/clinical_signals.py` | Use this as a structural template for the new tool file |
| `POC/src/mcp_server/utils.py` | `load_signal_store_record()` as a pattern for `load_event_timeline_record()` to follow |
| `POC/src/mcp_server/server.py` | How tools are registered with `mcp.tool()()` |
| `assets/synthesis/HealthyRoutineCheckup/record_000.json` | Understand the `assets/synthesis/` directory structure |

---

## What Already Exists (Don't Rewrite)

- The 4 existing MCP tools in `POC/src/mcp_server/tools/` — use `clinical_signals.py` as a copy template
- `load_signal_store_record()` in `utils.py` — your new `load_event_timeline_record()` should follow the same pattern
- `server.py` registration pattern — just add one line

---

## Step-by-Step Instructions

### 6a — Create fixture data: `assets/synthesis/canonical/somchai_event_timeline.json`

Transcribe the full Somchai W. example response from `event-timeline-contract.md`:

```json
{
  "patient_token": "tok_hmac_56291047",
  "timeline_span": {
    "earliest_event_date": "2019-06-12",
    "latest_event_date": "2026-03-11",
    "span_years": 6.7
  },
  "diagnoses": [
    /* 4 entries: Hyperlipidaemia, Prediabetes, Hypertension, Hyperuricaemia */
    /* Each entry includes: condition_code (SNOMED CT), display_name, onset_date, status, icd10_code */
  ],
  "hospitalizations": [],
  "significant_lab_events": [
    /* 5 entries with LOINC codes */
    /* Each entry: loinc_code, test_name, event_date, value, unit, interpretation, clinical_significance */
  ],
  "screening_procedure_history": [
    /* 1 entry: Colonoscopy 2019-06-12 */
    /* Each entry: snomed_code, procedure_name, performed_date, result_summary, next_due_date */
  ],
  "medication_changes": [
    /* 2 entries: Atorvastatin added 2022, Amlodipine added 2025 */
    /* Each entry: medication_name, change_type, change_date, dose, indication */
  ],
  "_pipeline_meta": {
    "generated_at": "2026-03-11T08:00:00Z",
    "pipeline_run_id": "run_20260311_001"
  }
}
```

> All values must be taken verbatim from `event-timeline-contract.md` Somchai W. example. Do not fabricate values.

### 6b — Add `load_event_timeline_record()` to `POC/src/mcp_server/utils.py`

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

### 6c — Create `POC/src/mcp_server/tools/event_timeline.py`

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

### 6d — Register in `POC/src/mcp_server/server.py`

Add after the existing 4 tool registrations:

```python
from src.mcp_server.tools.event_timeline import get_patient_event_timeline
mcp.tool()(get_patient_event_timeline)
```

---

## Verification

```bash
# Direct Python call
python -c "
import asyncio, sys
sys.path.insert(0, 'POC')
from src.mcp_server.tools.event_timeline import get_patient_event_timeline
import json
result = asyncio.run(get_patient_event_timeline('tok_hmac_56291047'))
data = json.loads(result)
print('diagnoses count:', len(data['diagnoses']))
print('lab_events count:', len(data['significant_lab_events']))
print('medication_changes count:', len(data['medication_changes']))
"
```

Expected output:
```
diagnoses count: 4
lab_events count: 5
medication_changes count: 2
```

# GAP-2 — Wire ConfidenceCalibrator + OutputEnricher + PIIRehydrator

**Severity:** 🔴 High
**Execution order:** Step 3 — after GAP-1 and GAP-8
**Estimated effort:** 2–3 hours
**Category:** Architecture

---

## Why This Matters

The canonical API path (`OrchestrationManager → ClinicalReasoningWorkflow`) currently returns raw BAML output — it **never calls** `ConfidenceCalibrator`, `OutputEnricher`, or `PIIRehydrator`. The response is missing all Stage 2 fields required by the spec and the frontend:

| Missing field | Impact |
|---|---|
| `confidence_score` / `confidence_tier` | Screen 1 confidence gauge is blank |
| `rule_preliminary_tier` | Side-by-side rule vs AI tier comparison is impossible |
| `resolved_package.package_name` / `price_thb` | No package or price shown to ROC staff |
| `add_ons[].label` / `add_ons[].navavej_product.price_thb` | Add-on table has no labels or prices |
| `patient_high_alert` (currently a bool) | Screen 1 high-alert badges cannot render |
| PII rehydration | Response contains UUID tokens instead of patient name/DOB |

**Spec reference:** `recommendation-output-schema.md` Stage 2 fields table; `component-inventory-solution-approach.md §8` (Confidence Calibrator), `§12` (PII Rehydration).

---

## Dependencies

- **Depends on:** GAP-1 (security), GAP-8 (demo patient record exists)
- **Unblocks:** GAP-3 (safety validator wiring), GAP-10 (cleanup), and all frontend work

---

## Understanding the Two Orchestrator Paths (Critical)

There are two orchestrator implementations. Only one is called by the API:

| Path | Class | File | Called by API? |
|---|---|---|---|
| **Canonical (API path)** | `OrchestrationManager` | `POC/src/orchestrator/core/manager.py` | ✅ Yes |
| **Rich path (dead code)** | `ClinicalOrchestrator` | `POC/src/orchestrator/agents/orchestrator.py` | ❌ No |

`ClinicalOrchestrator` in `agents/orchestrator.py` **does** call `ConfidenceCalibrator`, `OutputEnricher`, and `PIIRehydrator` correctly — but it's never invoked by the API. **Read `agents/orchestrator.py` as a reference** to understand the wiring logic. Do not copy it verbatim (it also calls a deprecated `get_patient_context` MCP tool that no longer exists).

---

## Context Discovery

Read these files in order before touching any code:

| File | What to look for |
|---|---|
| `POC/src/orchestrator/core/manager.py` | Lines 43–60: `generate_recommendation()` — see what it currently does and doesn't do after `workflow.execute()` |
| `POC/src/orchestrator/workflows/base.py` | `WorkflowContext` Pydantic model — you will add two new fields here |
| `POC/src/orchestrator/workflows/clinical.py` | `_generate_recommendation()` — locate the block after `context.ai_output = {...}` where you insert the calibrator call |
| `POC/src/orchestrator/agents/orchestrator.py` | **Read-only reference** — shows the correct wiring sequence for confidence → enrich → audit → rehydrate |
| `POC/src/orchestrator/enrichment/output_enricher.py` | `enrich_output()` and `enrich_add_ons()` signatures; line 93: the `patient_high_alert` bool bug |
| `POC/src/orchestrator/validation/confidence_calibrator.py` | `compute_confidence_score()` and `compute_confidence_tier()` signatures and formula |
| `POC/src/orchestrator/privacy/rehydration.py` | `PIIRehydrator` class — constructor and `rehydrate()` method |
| `POC/src/orchestrator/privacy/masking.py` | `PIIMasker.get_rehydration_map()` — how to get the map back after masking |
| `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/recommendation-output-schema.md` | Stage 2 fields table — the exact shape the response must match |

---

## What Already Exists (Don't Rewrite)

All four classes are fully implemented and correct:
- `ConfidenceCalibrator` — formula, tier thresholds all correct per spec
- `OutputEnricher.enrich_add_ons()` — correctly enriches with `label`, `category`, `navavej_product`, `trigger_signals_matched`
- `PIIMasker` / `PIIRehydrator` — UUID-token mapping, map never persisted
- SHA-256 hash chain in `AuditLogger` — correct

The only work is **wiring** these into the canonical path and fixing one bug in `output_enricher.py`.

---

## Step-by-Step Instructions

### 3a — Extend `WorkflowContext` in `POC/src/orchestrator/workflows/base.py`

Add two new fields to the `WorkflowContext` Pydantic model so the manager can access them after `workflow.execute()` returns:

```python
signal_store_meta: dict = {}    # populated from record["_meta"]
ruleset_response: dict = {}     # populated from get_program_ruleset MCP tool response
```

### 3b — Wire `ConfidenceCalibrator` in `POC/src/orchestrator/workflows/clinical.py`

In `_generate_recommendation()`, after the block that sets `context.ai_output = {...}` (after the BAML call), add:

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

# Store metadata on context for the manager to use
context.signal_store_meta = signal_store_meta
context.ruleset_response = context.raw_context.get("get_program_ruleset", {})
```

### 3c — Wire `OutputEnricher` and `PIIRehydrator` in `POC/src/orchestrator/core/manager.py`

**After** `context = await workflow.execute(patient_id)` and **before** the safety guard call:

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

**After** the audit logger call, before returning:

```python
# PII Rehydration — restore real patient identifiers
from src.orchestrator.privacy.rehydration import PIIRehydrator
rehydrator = PIIRehydrator(workflow.masker.get_rehydration_map())
return rehydrator.rehydrate(context.ai_output)
```

> **Note on `workflow.masker`:** `workflow` is currently a local variable inside the `async with` block. You may need to either store `workflow.masker` on `context` before returning, or restructure the scoping so `workflow` is accessible where you call `PIIRehydrator`. Check the current `manager.py` scope carefully.

### 3d — Fix `patient_high_alert` in `POC/src/orchestrator/enrichment/output_enricher.py`

Find line 93 (approximately):
```python
"patient_high_alert": len(clinical_signals.get("missing_signals", [])) > 5,
```

Replace with:
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

The six signal IDs in the hardcoded list are the subset of `signals_fired` that qualify as high-priority alerts per the spec. For the POC this hardcoded list is sufficient.

---

## Verification

Start the server and run:
```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"patient_token": "tok_hmac_56291047"}'
```

Response must contain:
- `"confidence_score": 0.823` (or very close — deterministic formula)
- `"confidence_tier": "High"`
- `"rule_preliminary_tier": "Advanced"`
- `"resolved_package": {"package_name": "Platinum — Men", "price_thb": 8700, ...}`
- `"add_ons": [{... "label": "<non-empty string>", "navavej_product": {"price_thb": <integer>}, ...}]`
- `"patient_high_alert": {"critical_signals": [...], "missing_data_alerts": [...]}`
- `"reasoning_trace"` is a multi-sentence string (not a UUID token)

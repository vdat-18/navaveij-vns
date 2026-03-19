# GAP-10 — Deprecate Dead-Code `ClinicalOrchestrator`

**Severity:** 🟡 Low
**Execution order:** Step 10 — last; after GAP-2 is complete
**Estimated effort:** 15–20 minutes
**Category:** Code Quality

---

## Why This Matters

`POC/src/orchestrator/agents/orchestrator.py` defines `ClinicalOrchestrator` — a richer orchestrator implementation that **is never called by the API**. The only caller is `test_orchestrator.py`, a root-level script that is not part of the test suite.

The problem this causes:
- Developers reading the code see `ClinicalOrchestrator` calling `ConfidenceCalibrator`, `OutputEnricher`, and `PIIRehydrator` — and assume the API produces enriched output. It doesn't.
- It creates false confidence that everything is wired correctly.
- `ClinicalOrchestrator` also calls `get_patient_context` (a deprecated MCP tool that no longer exists in `server.py`) — it would crash on that line if actually called.

> **Do NOT delete this file.** During GAP-2, developers should read `ClinicalOrchestrator` as a reference implementation showing the correct wiring sequence. Deleting it before GAP-2 is complete removes a valuable guide.

---

## Dependencies

- **Depends on:** GAP-2 completed (the wiring it references has been implemented in the canonical path)
- **Unblocks:** Nothing — this is housekeeping only

---

## Context Discovery

Read these files:

| File | What to look for |
|---|---|
| `POC/src/orchestrator/agents/orchestrator.py` | The full `ClinicalOrchestrator` class — note the call to `get_patient_context` (line ~58) which references a non-existent MCP tool |
| `POC/test_orchestrator.py` | How `ClinicalOrchestrator` is currently imported and called |
| `POC/src/orchestrator/core/manager.py` | `OrchestrationManager` — the canonical replacement |

---

## What Already Exists (Don't Rewrite)

`OrchestrationManager` in `core/manager.py` is the canonical implementation and should not be modified here.

---

## Step-by-Step Instructions

### 10a — Add deprecation docstring to `POC/src/orchestrator/agents/orchestrator.py`

Add a prominent deprecation notice at the top of the class docstring:

```python
class ClinicalOrchestrator:
    """DEPRECATED — Use OrchestrationManager + ClinicalReasoningWorkflow instead.

    This class was an earlier standalone implementation. It is preserved for
    reference only and is NOT called by any production code path. Do not use.

    The canonical API path is:
        OrchestrationManager (core/manager.py)
            → ClinicalReasoningWorkflow (workflows/clinical.py)

    NOTE: This class also calls `get_patient_context`, a deprecated MCP tool
    that no longer exists in server.py. Calling this class directly will crash
    at that point.
    """
```

### 10b — Update `POC/test_orchestrator.py`

Replace the `ClinicalOrchestrator` import and usage with `OrchestrationManager`:

```python
# Before:
from src.orchestrator.agents.orchestrator import ClinicalOrchestrator
orchestrator = ClinicalOrchestrator()
result = await orchestrator.generate_recommendation("some_patient_id")

# After:
from src.orchestrator.core.manager import OrchestrationManager
orchestrator = OrchestrationManager()
result = await orchestrator.generate_recommendation("tok_hmac_56291047")
print(result)
```

---

## Verification

```bash
# Confirm the deprecated class still exists (not deleted)
grep -l "ClinicalOrchestrator" POC/src/orchestrator/agents/orchestrator.py

# Confirm the docstring has DEPRECATED marker
grep "DEPRECATED" POC/src/orchestrator/agents/orchestrator.py

# Confirm test_orchestrator.py no longer imports ClinicalOrchestrator
grep "ClinicalOrchestrator" POC/test_orchestrator.py
# Expected: no output

# Run the updated test script
cd POC && python test_orchestrator.py
# Expected: recommendation output printed without errors
```

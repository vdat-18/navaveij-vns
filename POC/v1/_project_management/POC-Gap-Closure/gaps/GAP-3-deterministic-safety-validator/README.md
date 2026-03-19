# GAP-3 — Deterministic Safety Validator

**Severity:** 🔴 High
**Execution order:** Step 4 — after GAP-2 (enrichment pipeline wired)
**Estimated effort:** 1–1.5 hours
**Category:** Safety

---

## Why This Matters

The current `ClinicalSafetyGuard` calls an LLM critic to check recommendations — but **never modifies `ai_output`**. Even if `is_safe = False`, the violating add-ons remain in the response.

The spec requires:
> "The violating item is **silently removed** from `add_ons[]` ... A **conflict event is written synchronously** to the Audit Logger."

The evaluation committee will specifically test the **Mammogram + male patient scenario**. Somchai W. has `"mammogram"` in his `eligibility_exclusions`. If the AI (non-deterministically) includes mammogram in `add_ons`, the validator must catch and revoke it. Currently it cannot — the LLM critic may flag it but nothing gets removed.

**POC evaluation impact:** 20% Security/Privacy criterion

---

## Dependencies

- **Depends on:** GAP-2 (enrichment pipeline wired, `hard_constraints` now accessible in manager)
- **Unblocks:** Final end-to-end validation (GAP-3 is needed before the mammogram demo can pass)

---

## Context Discovery

Read these files before making changes:

| File | What to look for |
|---|---|
| `POC/src/orchestrator/safety/validator.py` | The full class: `validate()` calls BAML critic, returns a report dict, **does not modify `ai_output`** |
| `POC/src/orchestrator/safety/rules.py` | `GENDER_EXCLUSIONS` dict — already defined here but never imported by `validator.py` |
| `POC/src/mcp_server/utils.py` | `filter_add_ons_by_demographics()` — shows how demographic filtering is already done pre-AI (the safety validator must catch post-AI violations) |
| `doc_outputs/architecture/AI/Recommendation Engine/v3/component-inventory-solution-approach.md` | Section §2.6 — Safety Rule Validator: exactly what it checks, what "silently removed" means, and the conflict event requirement |
| `POC/src/orchestrator/core/manager.py` | Where `safety_guard.validate()` is called — you need to update the call signature to pass `hard_constraints` |

---

## What Already Exists (Don't Rewrite)

- `GENDER_EXCLUSIONS` in `rules.py` — correct, just not imported
- The LLM critic call (`b.ValidateRecommendation`) — keep this as Layer 2 advisory; it's not broken, just insufficient alone
- The `audit_logger` reference in `manager.py` — you can pass it to `ClinicalSafetyGuard.__init__()` for conflict event logging

---

## Architecture: Two-Layer Validation

```
AI output
    │
    ▼
Layer 1: Deterministic check (runs first, non-negotiable)
    ├── Re-fetch hard_constraints (already available in manager)
    ├── Check each add_on.item_code against eligibility_exclusions
    └── Silently remove violating items + write conflict event to audit log
    │
    ▼
Layer 2: LLM critic (advisory only, does not gate output)
    └── b.ValidateRecommendation → is_safe, critic_score, findings
    │
    ▼
Clean output returned
```

---

## Step-by-Step Instructions

### 4a — Refactor `POC/src/orchestrator/safety/validator.py`

Add the deterministic Layer 1 method and update `validate()`:

```python
from src.orchestrator.safety.rules import GENDER_EXCLUSIONS

class ClinicalSafetyGuard:
    def __init__(self, audit_logger=None):
        self.audit_logger = audit_logger

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
            # Log conflict event synchronously
            self.audit_logger.log_safety_conflict(
                revoked_items=revoked,
                patient_token=raw_context.get("get_hard_constraints", {}).get("patient_token", "unknown")
            )

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

> If `AuditLogger` doesn't have a `log_safety_conflict()` method yet, add a simple one that writes a tagged entry to the JSONL file, or skip the method call for now and just log via `logger.warning()`. The conflict must at minimum appear in the application log.

### 4b — Update call site in `POC/src/orchestrator/core/manager.py`

Change the safety guard call to pass `hard_constraints`:

```python
safety_result = await self.safety_guard.validate(
    context.ai_output,
    context.raw_context,
    hard_constraints=context.raw_context.get("get_hard_constraints", {})
)
```

---

## Verification

**Demo test — mammogram revocation:**

1. Temporarily inject `"mammogram"` into the AI output's `add_ons` list by adding a test add-on directly in `clinical.py` before the safety guard runs, OR use a patient record that reliably triggers it.
2. Call `POST /api/recommend {"patient_token": "tok_hmac_56291047"}`.
3. Confirm `"mammogram"` does **not** appear in `add_ons` in the response.
4. Check `POC/logs/audit.jsonl` — a conflict event entry should be present.

```bash
# Check the last audit log entry for revocation
tail -1 POC/logs/audit.jsonl | python -m json.tool | grep -A5 "revoked"
```

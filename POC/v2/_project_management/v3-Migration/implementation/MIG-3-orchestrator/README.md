# MIG-3 — Orchestrator Update

**Status:** Completed
**Priority:** P1
**POC Scoring Impact:** Hybrid 35% + Security 20%
**Depends on:** MIG-2

## Objective

1. Add `force_rule_based: bool = False` to `generate_recommendation()`.
2. Snapshot `masked_ai_output` before rehydration.
3. Return `security_metadata` (rehydration_map + masked_ai_output + is_poc_demo) in result.

## Files Changed

- `POC/v2/backend/src/services/orchestrator.py`
- `POC/v2/scripts/tests/test_orchestrator_mig3.py`

## Acceptance Gate

- `generate_recommendation()` accepts `force_rule_based` without errors
- Response dict contains `security_metadata.rehydration_map` (dict)
- Response dict contains `security_metadata.masked_ai_output` (dict with `reasoning_trace`)
- Both AI and rule-based paths populate `security_metadata`
- `security_metadata` is injected after final rehydration so `masked_ai_output` stays masked

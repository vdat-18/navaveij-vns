# MIG-3 Execution Plan — Orchestrator Update

**Date:** 2026-03-19  
**Scope:** `POC/v2/backend/src/services/orchestrator.py`  
**Status:** Planned (not implemented)

## Goal

Upgrade orchestrator behavior so MIG-2 rule/AI mode can be controlled from orchestration, while returning demo-safe privacy metadata (`security_metadata`) without leaking rehydrated PII in masked payload views.

## In-Scope Changes

1. Add `force_rule_based: bool = False` to `generate_recommendation(...)`.
2. Pass `force_rule_based` through to `workflow.execute(...)`.
3. Capture `masked_ai_output = context.ai_output.copy()` before any rehydration.
4. Add `security_metadata` to the final response with:
   - `rehydration_map`
   - `masked_ai_output`
   - `is_poc_demo: True`
5. Preserve existing v2 safety validation, audit logging, and current frontend-facing payload keys.

## Critical v2-Specific Constraint

Current v2 orchestrator performs a second full-result rehydration pass:

- `rehydrated_output = rehydrator.rehydrate(context.ai_output)`
- `result = {...}`
- `return rehydrator.rehydrate(result)`

If `security_metadata.masked_ai_output` is attached before that final pass, its masked tokens will also be rehydrated and no longer represent masked AI output.  
Therefore MIG-3 implementation must:

1. Build and rehydrate the normal frontend payload first.
2. Inject `security_metadata` only after final rehydration.
3. Return the augmented response.

## Implementation Steps

1. **Signature and call-through**
   - Update orchestrator method signature to accept `force_rule_based`.
   - Pass value into `workflow.execute(patient_id, patient_token=..., force_rule_based=...)`.

2. **Capture masked snapshot**
   - Immediately after workflow and post-processing fields are finalized, set:
     - `masked_ai_output = context.ai_output.copy()`
   - Keep shallow-copy behavior for POC parity unless deeper immutability is required later.

3. **Preserve existing rehydration pipeline**
   - Keep current rehydration for primary payload fields (`rehydrated_output` + final result rehydration pass).

4. **Inject security metadata after final rehydration**
   - Compute:
     - `rehydrated_result = rehydrator.rehydrate(result)`
   - Then append:
     - `rehydrated_result["security_metadata"] = {...}`
   - Return `rehydrated_result`.

5. **No MIG-4 contract edits in this step**
   - Do not modify `RecommendRequest` yet.
   - Do not change route-level normalization behavior yet.

## Verification Plan

1. Add/extend orchestrator-focused tests to validate:
   - method accepts `force_rule_based` parameter;
   - workflow invoked with same `force_rule_based`;
   - response includes `security_metadata.rehydration_map` dict;
   - `security_metadata.masked_ai_output` exists and retains masked-token form.
2. Run targeted tests:
   - orchestrator tests (or nearest integration test path),
   - `scripts/tests/workflows/test_clinical_workflow.py`,
   - `scripts/tests/test_api_contract_routes.py` regression check.
3. Run full suite gate after migration step when runtime supports it.

## Acceptance Gates

1. `generate_recommendation(..., force_rule_based=...)` works for both `True` and `False`.
2. `workflow.execute` receives `force_rule_based` value unchanged.
3. Returned payload includes `security_metadata` with required fields.
4. `security_metadata.masked_ai_output` remains masked (not rehydrated by second pass).
5. Existing orchestrator output keys remain intact for current consumers.

## Risks and Mitigations

1. **Risk:** Copying v3 pattern directly leaks masked payload due v2 second rehydration pass.  
   **Mitigation:** Inject `security_metadata` only after final rehydration call.
2. **Risk:** Later MIG-4 route normalization may strip `security_metadata`.  
   **Mitigation:** Track as explicit follow-up in MIG-4 plan and tests.
3. **Risk:** `force_rule_based` behavior appears ineffective through `/api/recommend` until MIG-4 wiring.  
   **Mitigation:** Validate at orchestrator level first; wire request model in MIG-4.
4. **Risk:** Recommendation cache key currently omits mode flag at contract layer.  
   **Mitigation:** Address cache-key mode partitioning in MIG-4 contract implementation.

## Exit Evidence to Capture

- `orchestrator.py` diff showing new signature, workflow pass-through, and post-rehydration metadata injection.
- Targeted test output proving metadata presence and masked-output integrity.
- Updated MIG-3 artifacts:
  - `README.md`
  - `_discovery.md`
  - `_development_summary.md`
  - `_lastest_test_results.md`

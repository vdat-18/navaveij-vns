# MIG-4 — contracts.py API Update

**Status:** Implemented (verification execution blocked by local command runner error)
**Priority:** P1
**POC Scoring Impact:** Hybrid 35%
**Depends on:** MIG-3

## Objective

1. Add `force_rule_based: bool = False` to `RecommendRequest` Pydantic model.
2. Pass it through to `orchestrator.generate_recommendation()`.
3. Ensure `security_metadata` from the orchestrator is included in the `/api/recommend` response.
4. Surface `recommendation_source` and `review_required` at the top level of the response.

## Files Changed

- `POC/v2/backend/src/api/routes/contracts.py`
- `POC/v2/scripts/tests/test_api_contract_routes.py`

## Acceptance Gate

- `POST /api/recommend` with `{"patient_token": "...", "force_rule_based": false}` → `recommendation_source: "AI"`
- `POST /api/recommend` with `{"patient_token": "...", "force_rule_based": true}` → `recommendation_source: "RuleBased"`, `review_required: true`
- Both responses include `security_metadata` with non-null `rehydration_map` and `masked_ai_output`
- All existing contract tests still pass

## Implementation Notes

1. Added `force_rule_based` to request model and passed it through to orchestration.
2. Added `security_metadata` to response model and stage-2 normalization output.
3. Preserved orchestrator/workflow `recommendation_source` and `review_required` precedence, with confidence fallback only when absent.
4. Included `force_rule_based` in recommendation cache key payload to prevent cross-mode cache contamination.
5. Expanded route tests for mode passthrough, security metadata, source/review precedence, and cache partitioning by mode.

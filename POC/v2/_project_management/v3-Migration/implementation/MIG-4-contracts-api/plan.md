# MIG-4 Execution Plan — contracts.py API Wiring

**Date:** 2026-03-19  
**Scope:** `POC/v2/backend/src/api/routes/contracts.py`  
**Status:** Planned (not implemented)

## Goal

Complete the contracts-layer wiring so `/api/recommend` can control MIG-2/MIG-3 behavior (`force_rule_based`) and return orchestrator-provided `security_metadata` without breaking Stage-2 compatibility.

## In-Scope Changes

1. Extend request contract:
   - Add `force_rule_based: bool = False` to `RecommendRequest`.
2. Extend response contract:
   - Include `security_metadata` in `RecommendResponse` so response-model filtering does not drop it.
3. Wire mode pass-through:
   - Pass `request.force_rule_based` into `orchestrator.generate_recommendation(...)`.
4. Preserve orchestrator source/review fields:
   - Ensure top-level `recommendation_source` and `review_required` in API response reflect orchestrator output rather than confidence-only recomputation.
5. Partition cache by mode:
   - Include `force_rule_based` in recommendation cache key composition.

## Non-Goals for MIG-4

- No orchestrator internal redesign (already handled in MIG-3).
- No frontend toggle UI implementation (MIG-5/MIG-6).
- No schema migrations beyond `/api/recommend` contract path.

## Implementation Steps

1. **Request model update**
   - Edit `RecommendRequest` with:
     - `force_rule_based: bool = False`

2. **Response model update**
   - Edit `RecommendResponse` to include:
     - `security_metadata: dict[str, Any]`
   - Keep all existing fields unchanged.

3. **Route call-through**
   - In `recommend(...)`, pass:
     - `force_rule_based=request.force_rule_based`
   - Keep existing patient token/id resolution and error handling behavior.

4. **Cache key mode separation**
   - Update `_recommendation_cache_key(...)` signature to accept `force_rule_based`.
   - Add `force_rule_based` to key payload fields.
   - Ensure `recommend(...)` passes request value into key generation.

5. **Normalization policy for source/review/security**
   - In `_normalize_stage2(...)`, preserve:
     - `recommendation_source` from orchestrator/workflow if present;
     - `review_required` from orchestrator/workflow if present.
   - Keep confidence-derived fallback only when values are absent.
   - Ensure `security_metadata` is surfaced in returned payload.
   - Keep all existing Stage-2 field names and structures intact.

6. **Test updates**
   - Extend `scripts/tests/test_api_contract_routes.py`:
     - verify AI mode response (`force_rule_based=false`) includes `security_metadata`;
     - verify rule mode response (`force_rule_based=true`) returns `RuleBased` + `review_required=true`;
     - verify cache key separation across mode values prevents cross-mode cache reuse.
   - Preserve existing route/TTL tests.

7. **Verification and artifacts**
   - Run targeted contract tests and cache-related tests.
   - Update MIG-4 artifacts:
     - `README.md`
     - `_discovery.md`
     - `_development_summary.md`
     - `_lastest_test_results.md`

## Acceptance Gates

1. `POST /api/recommend` accepts `force_rule_based` without validation errors.
2. Route forwards mode flag to orchestrator.
3. Responses include `security_metadata.rehydration_map` and `security_metadata.masked_ai_output`.
4. `recommendation_source` and `review_required` correctly reflect AI vs rule-based mode.
5. Cache keys differ between `force_rule_based=true` and `false`.
6. Existing Stage-2 contract fields remain unchanged and backward-compatible.

## Risks and Mitigations

1. **Risk:** `response_model` strips new fields.  
   **Mitigation:** Explicitly add `security_metadata` to `RecommendResponse`.
2. **Risk:** Confidence-based logic overrides workflow intent for source/review.  
   **Mitigation:** Prefer orchestrator/workflow-provided values; fallback only when missing.
3. **Risk:** Cross-mode cache contamination.  
   **Mitigation:** Include `force_rule_based` in cache key payload.
4. **Risk:** Stage-2 regressions from normalization edits.  
   **Mitigation:** Keep edits additive and validate with existing contract tests.

## Exit Evidence to Capture

- `contracts.py` diff for request/response models, route call-through, normalization, and cache key updates.
- Test evidence for AI/rule mode behavior and security metadata presence.
- Test evidence for cache partitioning by `force_rule_based`.
- Updated MIG-4 artifact files with final status and blockers (if any).

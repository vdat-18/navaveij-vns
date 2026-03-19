# MIG-4 Discovery

## Key Risk

`_normalize_stage2()` in `contracts.py` is the central assembly function. Existing tests assert specific field shapes. MIG-4 must remain additive and avoid Stage-2 field regressions while introducing mode-aware behavior.

## Confirmed Contract Additions

- `recommendation_source` — string, "AI" or "RuleBased"
- `review_required` — bool
- `security_metadata` — object with `rehydration_map`, `masked_ai_output`, `is_poc_demo`
- `force_rule_based` request field — bool, default `false`

## Behavior Constraints

All Stage-2 fields already produced by `_normalize_stage2()` must remain unchanged:
- `confidence_score`, `confidence_tier`
- `rule_preliminary_tier`, `ai_recommended_tier`
- `add_ons[]`, `reasoning_trace`, `supporting_signals[]`, `missing_signals[]`
- `communication_script`, `patient_high_alert`, `metadata`

Additional constraints discovered from MIG-4 plan and current code:
- Preserve orchestrator-provided `recommendation_source` / `review_required` when present.
- Use confidence-derived fallback only when those fields are absent.
- Partition recommendation cache keys by `force_rule_based` to avoid cross-mode cache reuse.

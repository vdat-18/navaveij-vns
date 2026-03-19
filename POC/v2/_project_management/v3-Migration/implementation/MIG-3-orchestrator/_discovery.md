# MIG-3 Discovery

## Source Reference

v3 orchestrator: `POC/v3/backend/src/services/orchestrator.py`

## Key Pattern (v3)

```python
masked_ai_output = context.ai_output.copy()
rehydrated_output = rehydrator.rehydrate(context.ai_output)

result = {
    **rehydrated_output,
    "biomarker_trends": context.masked_context.get("get_biomarker_trends", {}),
    "clinical_signals": context.masked_context.get("get_clinical_signals", {}),
    "security_metadata": {
        "rehydration_map": context.rehydration_map,
        "masked_ai_output": masked_ai_output,
        "is_poc_demo": True
    }
}
```

## v2 Constraint Applied

- v2 does a second full `rehydrator.rehydrate(result)` pass before returning.
- If `security_metadata` is attached before that pass, `masked_ai_output` is no longer masked.
- Implementation strategy in v2:
  1. Capture `masked_ai_output = context.ai_output.copy()`
  2. Build and rehydrate normal frontend payload first
  3. Inject `security_metadata` only after final rehydration

## Notes

- The `rehydration_map` in `WorkflowContext` is the token→real_value dict built by `PIIMasker`.
- For rule-based fallback, `rehydration_map` may be empty `{}` if no PII was masked (patient token only, no LLM call made). This is acceptable — the frontend handles an empty map gracefully.
- `masked_ai_output` is a shallow copy; nested structures (add_ons list) still reference the same objects. This is fine for a POC demo read.

# GAP-R2 — Safety Rule Validator Architecture

**Title:** Safety validator is LLM-based and filters pre-AI (both incorrect)
**Status:** Not started

---

## Objective

Implement a deterministic post-AI Safety Rule Validator that silently removes ineligible
add-on items from the AI output, logs conflict events to the audit log, and never surfaces
removals in the API response. Remove the pre-AI demographic filtering from `get_program_ruleset`.

## Scope

1. Remove `filter_add_ons_by_demographics()` from `program_ruleset.py` tool response.
2. Implement `SafetyRuleValidator.validate_and_filter()` in `safety.py`:
   - Check gender_constraint, age_min/max, safety_contraindication_signals per item.
   - Silently remove violations; append conflict event to audit log.
3. Wire post-AI validator into `orchestrator.py` between BAML output and PII rehydration.

## Primary Files

- `POC/v2/backend/src/mcp_server/tools/program_ruleset.py`
- `POC/v2/backend/src/services/safety.py`
- `POC/v2/backend/src/services/orchestrator.py`

## Depends On

GAP-R3 — item_id field must exist in BAML output before removal checks make sense.

## Checkpoint Files

- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## Framework Reference

`doc_outputs/onboarding/ai-team-onboarding.md` Decision 6, Component 10

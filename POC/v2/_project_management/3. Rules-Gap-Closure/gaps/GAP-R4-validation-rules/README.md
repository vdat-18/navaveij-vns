# GAP-R4 — Validation Rules V2, V7, V9, V10

**Title:** Four framework validation rules not enforced post-BAML
**Status:** Not started

---

## Objective

Implement a post-BAML Python validator that enforces rules V2, V7, V9, and V10 against the
MCP context available at recommendation time. Validation failure triggers graceful degradation.

## Scope

| Rule | Check to implement |
|------|--------------------|
| V2 | Each item_id in add_ons[] exists in get_program_ruleset add_on_library |
| V7 | Each signal in supporting_signals[] exists in applicable_signals from get_clinical_signals |
| V9 | add_ons[] is non-empty when signals_fired is non-empty |
| V10 | price_thb per item matches ruleset value or is null |

## Primary File

`POC/v2/backend/src/api/routes/contracts.py` or new `POC/v2/backend/src/services/validator.py`

## Depends On

GAP-R3 — `item_id` and `price_thb` fields must exist in BAML output.

## Checkpoint Files

- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## Framework Reference

`doc_outputs/onboarding/ai-team-onboarding.md` §7 Validation Rules V1–V10

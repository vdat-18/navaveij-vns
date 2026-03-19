# MIG-2 — Workflow Update

**Status:** Completed
**Priority:** P0
**POC Scoring Impact:** Hybrid 35%
**Depends on:** MIG-1

## Objective

Update `clinical.py` workflow to:
1. Always run `RuleEvaluator` first for `rule_preliminary_tier`.
2. Chain the 3 BAML agents in sequence.
3. Fall back to rule-based output on any AI exception.
4. Support `force_rule_based` bypass parameter.

## Files Changed

- `POC/v2/backend/src/services/workflows/clinical.py`
- `POC/v2/backend/src/services/rules.py`
- `POC/v2/scripts/tests/workflows/test_clinical_workflow.py`
- `POC/v2/_project_management/v3-Migration/implementation/MIG-2-workflow-update/_discovery.md`
- `POC/v2/_project_management/v3-Migration/implementation/MIG-2-workflow-update/_development_summary.md`
- `POC/v2/_project_management/v3-Migration/implementation/MIG-2-workflow-update/_lastest_test_results.md`

## Delivered Behavior

- Deterministic `RuleEvaluator` runs first and sets `rule_preliminary_tier`.
- AI success path executes `AnalyzeClinicalRisks` → `MatchProgramRules` → `ComposeRecommendation`.
- Forced mode (`force_rule_based=True`) skips AI and returns rule-based output.
- AI exception path falls back to rule-based output with `review_required=True`.
- MCP tool arguments remain v2-compatible (`patient_token` + optional `patient_id`).
- Stage-2 consumer keys remain available in `ai_output` (`ai_recommended_tier`, `add_ons`, `communication_script`, `recommendation_source`, `review_required`, etc.).

# MIG-2 Execution Plan — Workflow Update

**Date:** 2026-03-19  
**Scope:** `POC/v2/backend/src/services/workflows/clinical.py` + new `POC/v2/backend/src/services/rules.py`  
**Status:** Planned (not implemented)

## Goal

Refactor the v2 clinical workflow to run deterministic rule evaluation first, execute the MIG-1 three-agent BAML chain for AI mode, and provide reliable rule-based fallback behavior without breaking existing Stage-2 route normalization.

## In-Scope Changes

1. Add `RuleEvaluator` support in v2 services:
   - Create `POC/v2/backend/src/services/rules.py` (ported from v3 with v2-compatible behavior).
2. Update workflow entrypoint:
   - `execute(..., force_rule_based: bool = False)` in `clinical.py`.
3. Replace legacy BAML call:
   - Remove `b.GenerateRecommendation(...)` usage.
   - Use `b.AnalyzeClinicalRisks(...)` → `b.MatchProgramRules(...)` → `b.ComposeRecommendation(...)`.
4. Add workflow fallback logic:
   - AI success path sets `recommendation_source="AI"` and `review_required=False`.
   - Forced mode or AI exception path sets `recommendation_source="RuleBased"` and `review_required=True`.
5. Keep output contract compatible with `_normalize_stage2()` consumers in contracts route.
6. Update workflow tests to stop mocking removed `GenerateRecommendation` and validate new path behavior.

## Non-Goals for MIG-2

- Do not wire `force_rule_based` through contracts request model yet (MIG-3/MIG-4 responsibility).
- Do not add `security_metadata` response behavior yet (MIG-3 responsibility).
- Do not change frontend toggle behavior yet (MIG-5/MIG-6 responsibility).

## Implementation Steps

1. **Baseline and dependency check**
   - Confirm MIG-1 generated client exposes three new methods.
   - Confirm `rules.py` is absent in v2 and must be added.

2. **Add deterministic rules service**
   - Port v3 `RuleEvaluator` into `POC/v2/backend/src/services/rules.py`.
   - Keep API minimal: evaluate fired signals and return:
     - `rule_tier`
     - `applied_rule_id`
     - `applied_condition`
     - `signals_matched`

3. **Refactor workflow execute signature and flow**
   - Add `force_rule_based: bool = False` to `execute()`.
   - Preserve v2 MCP tool argument compatibility (`patient_token` + optional `patient_id`).
   - Continue loading: hard constraints, clinical signals, biomarker trends, program ruleset.

4. **Implement MIG-2 recommendation phase**
   - Run `RuleEvaluator` first on raw signal data.
   - Build two internal helpers:
     - `_map_final_to_ai_output(...)` for AI success mapping.
     - `_build_rule_based_output(...)` for forced/fallback deterministic output.
   - In AI path, call:
     - `AnalyzeClinicalRisks`
     - `MatchProgramRules`
     - `ComposeRecommendation`
   - On exception or forced mode, fallback to rule-based output.

5. **Guarantee Stage-2-compatible ai_output keys**
   - Must include:
     - `ai_recommended_tier`
     - `tier_deviation_justification`
     - `add_ons` with `item_code`, `priority_level`, `rationale`
     - `reasoning_trace`
     - `supporting_signals`
     - `missing_signals`
     - `communication_script` (`clinical_conclusion`, `health_summary`, `recommendation_explanation`, `add_on_highlights`, `next_steps`)
     - `rule_preliminary_tier`
     - `recommendation_source`
     - `review_required`

6. **Update tests**
   - Refactor `scripts/tests/workflows/test_clinical_workflow.py` to mock 3-agent methods.
   - Add/extend tests for:
     - AI success path.
     - Forced rule-based path.
     - AI exception fallback path.
   - Ensure route-contract tests remain green with unchanged `_normalize_stage2` assumptions.

7. **Run verification and capture evidence**
   - Run targeted workflow tests first.
   - Run full regression suite `scripts/tests`.
   - Update MIG-2 artifacts:
     - `README.md`
     - `_discovery.md`
     - `_development_summary.md`
     - `_lastest_test_results.md`

## Acceptance Gates

1. `clinical.py` no longer references `GenerateRecommendation`.
2. `RuleEvaluator` exists in v2 and is used before AI path.
3. Forced mode and exception fallback both produce `recommendation_source="RuleBased"` and `review_required=True`.
4. AI success produces `recommendation_source="AI"` and `review_required=False`.
5. Contract-facing response shape remains compatible with `_normalize_stage2()`.
6. Regression tests pass without introducing MIG-1 regressions.

## Risks and Mitigations

1. **Risk:** MCP argument mismatch when porting v3 code.  
   **Mitigation:** Keep v2 MCP payload style with `patient_token` preserved.
2. **Risk:** Add-on schema mismatch (`item_id` vs `item_code`) breaks enrichment.  
   **Mitigation:** Enforce `item_code` in mapping output.
3. **Risk:** `FinalRecommendation` field drift (`script` vs `communication_script`).  
   **Mitigation:** Read generated types and map from `final.communication_script`.
4. **Risk:** Contracts overwrite source/review fields.  
   **Mitigation:** Preserve keys in workflow and validate route output in existing contract tests.

## Exit Evidence to Capture

- Diff proof for `clinical.py` and new `rules.py`.
- Test outputs for targeted workflow + regression runs.
- MIG-2 artifact updates with any blockers and final status.

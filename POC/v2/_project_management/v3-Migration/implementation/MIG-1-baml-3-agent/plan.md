# MIG-1 Execution Plan — BAML 3-Agent Pipeline

**Date:** 2026-03-19  
**Scope:** `POC/v2/baml_src/clinical/recommendation_output.baml`  
**Status:** Planned (not implemented)

## Goal

Replace the monolithic BAML recommendation function with a 3-agent chain while preserving compatibility with downstream v2 contracts and keeping safety validation intact.

## In-Scope Changes

1. Remove:
   - `RecommendationOutput` class
   - `GenerateRecommendation(...) -> RecommendationOutput`
2. Add new BAML classes:
   - `ClinicalRiskProfile`
   - `RecommendationPlan`
   - `FinalRecommendation`
3. Add new BAML functions:
   - `AnalyzeClinicalRisks(...) -> ClinicalRiskProfile`
   - `MatchProgramRules(...) -> RecommendationPlan`
   - `ComposeRecommendation(...) -> FinalRecommendation`
4. Keep unchanged:
   - `ValidateRecommendation()` flow
   - `Tier`, `PriorityLevel`, `AddOnItem`, `CommunicationScript`

## Implementation Steps

1. Snapshot current `recommendation_output.baml` structure and imports.
2. Port v3-equivalent class definitions into v2 file:
   - Include all required fields for `ClinicalRiskProfile`, `RecommendationPlan`, `FinalRecommendation`.
3. Port v3-equivalent function signatures and role-framed prompts:
   - Clinical analyst prompt for risk extraction
   - Policy specialist prompt for package/add-on matching
   - Clinical communicator prompt for patient-facing output
4. Remove obsolete monolithic function/type references in the same file.
5. Run BAML code generation:
   - `uv run baml-cli generate`
6. Perform import sanity check for generated client symbols:
   - verify `b.AnalyzeClinicalRisks`
   - verify `b.MatchProgramRules`
   - verify `b.ComposeRecommendation`
7. Record evidence in migration artifacts:
   - `_discovery.md`
   - `_lastest_test_results.md`
   - `_development_summary.md`

## Acceptance Gates

1. `uv run baml-cli generate` completes successfully.
2. Generated client exposes all three new functions.
3. No syntax/import regressions introduced in BAML generation outputs.
4. Existing shared types and safety validation references remain available.

## Compatibility Notes

- MIG-1 intentionally changes only BAML schema/function layer.
- No workflow/orchestrator/contracts/frontend behavior is modified in this step.
- Stage-2 compatibility mapping is deferred to MIG-2 and later items.

## Risks and Mitigations

1. **Risk:** Field/type mismatch between new classes and downstream usage.  
   **Mitigation:** Keep names/structure aligned with migration-plan mapping and v3 source.
2. **Risk:** Prompt/schema edits break BAML generation.  
   **Mitigation:** Generate immediately after edits and resolve errors before moving forward.
3. **Risk:** Accidental edits to non-MIG-1 surfaces.  
   **Mitigation:** Restrict implementation to `recommendation_output.baml` plus evidence artifacts only.

## Exit Evidence to Capture

- BAML generation command output.
- Symbol availability proof for three new functions.
- Updated MIG-1 summary and test-results notes indicating plan-to-implementation readiness.

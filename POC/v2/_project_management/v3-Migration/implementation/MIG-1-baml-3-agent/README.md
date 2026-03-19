# MIG-1 — BAML 3-Agent Pipeline

**Status:** In progress (BAML generation blocked by missing runtime tooling)
**Priority:** P0
**POC Scoring Impact:** Hybrid 35% + Pluggable AI 25%

## Objective

Replace the monolithic `GenerateRecommendation()` BAML function with a 3-agent chain:
1. `AnalyzeClinicalRisks()` → `ClinicalRiskProfile`
2. `MatchProgramRules(risk_profile, ruleset)` → `RecommendationPlan`
3. `ComposeRecommendation(risk_profile, plan)` → `FinalRecommendation`

## Files Changed

- `POC/v2/baml_src/clinical/recommendation_output.baml`

## Acceptance Gate

- `uv run baml-cli generate` completes without errors
- `from baml_client.sync_client import b; b.AnalyzeClinicalRisks` is importable
- Existing `ValidateRecommendation()` and all kept types (`Tier`, `PriorityLevel`, `AddOnItem`, `CommunicationScript`) remain intact

## Current Execution Notes

- Ported `recommendation_output.baml` from v3 to v2 with 3-agent chain:
  - `AnalyzeClinicalRisks() -> ClinicalRiskProfile`
  - `MatchProgramRules() -> RecommendationPlan`
  - `ComposeRecommendation() -> FinalRecommendation`
- Preserved shared types and enums in-file:
  - `Tier`, `PriorityLevel`, `AddOnItem`, `CommunicationScript`
- Applied compatibility naming for planned downstream mapping:
  - `FinalRecommendation.communication_script`
  - `ComposeRecommendation(..., plan: RecommendationPlan)`
- Attempted generation command in `POC/v2`:
  - `uv run baml-cli generate` → failed in environment (`uv: command not found`)
- Import verification for generated symbols is pending successful BAML generation.

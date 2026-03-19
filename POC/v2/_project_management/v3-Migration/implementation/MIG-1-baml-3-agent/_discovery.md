# MIG-1 Discovery

## Source Reference

v3 BAML definition: `POC/v3/baml_src/clinical/recommendation_output.baml`

## Key Observations

- v3 defines three functions (`AnalyzeClinicalRisks`, `MatchProgramRules`, `ComposeRecommendation`) and three new result types (`ClinicalRiskProfile`, `RecommendationPlan`, `FinalRecommendation`).
- Existing reused types from v2: `Tier`, `PriorityLevel`, `AddOnItem`, `CommunicationScript` — these are identical in both versions.
- The v2 `RecommendationOutput` BAML class can be removed; its Python equivalent lives in contracts.py as a Stage-2 assembled dict.
- `ValidateRecommendation()` in `safety_critic.baml` is unchanged between v2 and v3.

## Implementation Findings (2026-03-19)

- `POC/v2/baml_src/clinical/recommendation_output.baml` successfully updated to the v3 three-agent structure.
- Shared type preservation confirmed in updated v2 BAML file:
  - `Tier`, `PriorityLevel`, `AddOnItem`, `CommunicationScript`
- Downstream compatibility alignment applied for planned MIG-2 mapping:
  - `FinalRecommendation` uses `communication_script` field.
  - `ComposeRecommendation` input parameter normalized to `plan`.
  - `ClinicalRiskProfile.suggested_tier` set to required `Tier`.
- Generation command could not be executed in this environment:
  - `uv run baml-cli generate` failed with `uv: command not found`.
- Existing generated `baml_client` still reflects old `GenerateRecommendation` API until regeneration is run in a toolchain-enabled shell.

## Prompt Approach (per v3)

Each agent has a distinct role-framed prompt:
- **AnalyzeClinicalRisks**: Senior Physician — clinical pattern recognition
- **MatchProgramRules**: Policy Specialist — map risk to Navavej programs
- **ComposeRecommendation**: Clinical Communicator — patient-facing language, no raw identifiers

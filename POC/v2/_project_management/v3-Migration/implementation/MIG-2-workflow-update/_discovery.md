# MIG-2 Discovery

## Source Reference

- `POC/v3/backend/src/services/workflows/clinical.py`
- `POC/v3/backend/src/services/rules.py`
- `POC/v2/backend/src/api/routes/contracts.py` (`_normalize_stage2`)
- `POC/v2/scripts/tests/workflows/test_clinical_workflow.py`

## Key Observations

- v2 workflow still called legacy `GenerateRecommendation`, so MIG-2 requires swapping to the MIG-1 3-agent chain.
- Generated v2 BAML client already exposes `AnalyzeClinicalRisks`, `MatchProgramRules`, and `ComposeRecommendation`.
- v2 MCP tools still rely on `patient_token`; `patient_id` is supported and should remain included when available.
- `_normalize_stage2()` consumes stable keys from `ai_output`, so migration must preserve those key names.

## Critical: _map_final_to_ai_output contract

This helper must produce the following keys to satisfy `_normalize_stage2()` in contracts.py:

| Key | Source | Notes |
|---|---|---|
| `ai_recommended_tier` | `final.plan.ai_recommended_tier` | Must match Tier enum values |
| `tier_deviation_justification` | `final.plan.tier_deviation_justification` | Optional |
| `add_ons` | `final.plan.selected_add_ons` | Serialize BAML objects to dicts |
| `reasoning_trace` | Join `risk_profile.clinical_summary_bullets` + `plan.policy_reasoning` | Non-empty required |
| `supporting_signals` | `risk_profile.supporting_signal_ids` | List of signal IDs |
| `missing_signals` | `risk_profile.missing_signal_ids` | List of signal IDs |
| `communication_script` | `final.communication_script` | Serialize all sections |
| `rule_preliminary_tier` | `rule_tier` from RuleEvaluator | Always present |
| `recommendation_source` | static per path | `AI` or `RuleBased` |
| `review_required` | static per path | `False` (AI success), `True` (forced/fallback) |

## RuleEvaluator Porting Notes

- v2 had no `src/services/rules.py`; file must be added.
- For v2 compatibility, use `load_ruleset_tier_config()` from `src.mcp_server.utils` instead of hard-coded path reads.
- Rule engine output shape should remain minimal and deterministic:
  - `rule_tier`
  - `applied_rule_id`
  - `applied_condition`
  - `signals_matched`

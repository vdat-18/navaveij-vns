# GAP-R8 — Signal Pool Alignment

**Title:** Signal pool JSON diverges from framework derivation ledger
**Status:** Not started — pending clinical team input

---

## Objective

Align `sample_ruleset_tier_config.json` signal pool membership with the Rule Synthesis
Framework derivation ledger. All signal IDs must be traceable to a named guideline.

## Scope

**ADVANCED_METABOLIC_OR_CVD low-moderate pool:**
- Missing (add if confirmed): `fbs_upward_trend`, `diagnosis_fatty_liver`
- Undocumented extras (confirm or remove): `family_hx_early_heart_attack`,
  `symptom_fatigue`, `history_loss_of_consciousness`, `occupational_risk_factory`

**PREMIUM_MULTI_SIGNAL pool:**
- Missing (add if confirmed): `diabetes_confirmation_required`, `history_syncope`

## Prerequisite

Clinical team must confirm guideline sources for undocumented signals before JSON changes.
Do not unilaterally resolve signal pool membership.

## Primary File

`POC/v3/assets/synthesis/rulesets/sample_ruleset_tier_config.json`

## Checkpoint Files

- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## Framework Reference

`doc_outputs/architecture/AI/Recommendation Engine/v3/samples/rule-synthesis-framework.md`
§3.2 Signal Pool Assignment, §9 Validation Checklist

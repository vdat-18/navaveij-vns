# GAP-R3 — BAML Output Schema

**Title:** AddOnItem missing 4 fields; CommunicationScript has wrong field names
**Status:** Not started

---

## Objective

Update the Stage 1 BAML schema so `AddOnItem` produces all 7 required fields and
`CommunicationScript` has exactly the 4 fields specified by the framework.

## Scope

**AddOnItem changes:**
- Rename `item_code` → `item_id`
- Rename `priority_level` → `priority`
- Add: `label string`, `product_code string`, `price_thb float?`, `category string`

**CommunicationScript changes:**
- Remove: `clinical_conclusion`
- Rename: `recommendation_explanation` → `recommendation_rationale`
- Rename: `add_on_highlights` → `addon_highlights`

**Prompt update:** Instruct AI to populate new fields from the `program_ruleset` context.

## Primary File

`POC/v2/baml_src/clinical/recommendation_output.baml`

## Checkpoint Files

- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## Framework Reference

`doc_outputs/onboarding/ai-team-onboarding.md` §7 Stage 1 Output Schema

# GAP-R1 — Confidence Calibrator Formula

**Title:** Confidence calibrator formula deviations
**Status:** Not started

---

## Objective

Correct three sub-formula deviations in `_normalize_stage2()` in `contracts.py` so the
confidence score matches the framework specification in `ai-team-onboarding.md` §8.

## Scope

1. Set `rule_agreement = 0.0` when AI tier ≠ rule preliminary tier (currently `0.7`).
2. Redefine `signal_coverage` as data availability ratio, not active-signal ratio.
3. Redefine `data_completeness` as required-field presence ratio, not signal count ratio.

## Primary File

`POC/v2/backend/src/api/routes/contracts.py` — `_normalize_stage2()` function

## Checkpoint Files

- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## Framework Reference

`doc_outputs/onboarding/ai-team-onboarding.md` §8, Component 8 (Confidence Calibrator)

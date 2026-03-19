# GAP-R5 — Stage 2 Completeness

**Title:** patient_high_alert object and metadata fields missing from Stage 2 output
**Status:** Not started

---

## Objective

Add two missing Stage 2 sections to `_normalize_stage2()` in `contracts.py`.

## Scope

1. `patient_high_alert`:
   - `critical_signals[]`: derived from risk_flags where severity = "high"
   - `missing_data_alerts[]`: derived from AI output's `missing_signals[]`

2. `metadata`:
   - `template_version`: add constant (e.g., `"v1.0"`)
   - `latency_ms`: capture BAML call timing in `clinical.py` Phase 4; thread to assembler

## Primary Files

- `POC/v2/backend/src/api/routes/contracts.py` — `_normalize_stage2()`
- `POC/v2/backend/src/services/workflows/clinical.py` — Phase 4 timing

## Checkpoint Files

- `_discovery.md`
- `_development_summary.md`
- `_lastest_test_results.md`

## Framework Reference

`doc_outputs/onboarding/ai-team-onboarding.md` §7 Stage 2 System-Injected Fields

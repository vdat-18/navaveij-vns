# Discovery

Status: In progress

## Scope executed

- Migrated `/api/recommend` output from transitional wrapper to Stage-2-shaped response object.
- Added schema-normalization path to inject required Stage-2 fields after orchestration output.
- Preserved GAP-1 endpoint surface and legacy compatibility.

## Stage-2 assembly decisions

- Source of Stage-1 fields: orchestrator AI output.
- Source of ruleset enrichment: `get_program_ruleset(patient_id)`.
- Add-on enrichment fields injected:
  - `label`
  - `category`
  - `navavej_product`
  - `trigger_signals_matched`
- Confidence computation implemented with deterministic formula:
  - signal coverage
  - data completeness
  - rule agreement
- Confidence tier thresholds implemented:
  - High: `>= 0.75`
  - Medium: `>= 0.50`
  - Low: `< 0.50`
- `review_required` determined by low confidence (`< 0.50`) and toggles `recommendation_source` to `RuleBased`.

## Contract-shape normalizations

- Mapped `communication_script.clinical_conclusion` to Stage-2 `communication_script.opening`.
- Built `patient_high_alert.critical_signals` from clinical `risk_flags` (High/Critical severities only).
- Built `patient_high_alert.missing_data_alerts` from `missing_signals` with deterministic label and impact text.
- Added metadata fields:
  - `request_id`
  - `patient_token`
  - `model_id`
  - `template_version`
  - `ruleset_version`
  - `signal_store_pipeline_run_id`
  - `generated_at`
  - `latency_ms`

## Files changed

- `backend/src/api/routes/contracts.py`
- `scripts/tests/test_api_contract_routes.py`

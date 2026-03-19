# MIG-7 Discovery

## Source Reference

- `POC/v3/baml_src/synthesis/enrichment.baml`
- `POC/v3/scripts/enrich_healthy_scenarios.py`
- `POC/v3/scripts/enrich_hypertension_scenarios.py`
- `POC/v3/scripts/enrich_metabolic_scenarios.py`
- `POC/v3/scripts/enrich_senior_scenarios.py`

## enrichment.baml Function

`EnrichHealthyPatientRecord()` — takes a seed record and infers:
- Chief complaint
- Occupational tags, behavioral flags (smoking, alcohol, activity level)
- Stress levels, sleep patterns
- Reproductive history (for female patients)
- Vaccination gap suggestions

This is purely additive — it does not modify existing BAML functions or types.

## BAML Regeneration Note

After copying `enrichment.baml`, must run `uv run baml-cli generate` to include the new function in the generated client. This does not break existing functions.

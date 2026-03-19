# MIG-7 — Synthesis: enrichment.baml + scripts

**Status:** Not started
**Priority:** P3
**POC Scoring Impact:** Demo quality (richer patient data for evaluation)
**Depends on:** Independent (can run alongside any other MIG)

## Objective

Copy v3's enrichment BAML and scripts into v2 to enable generation of richer synthetic patient data across clinical scenarios.

## Files Added

- `POC/v2/baml_src/synthesis/enrichment.baml` (copy from v3)
- `POC/v2/scripts/enrich_healthy_scenarios.py` (copy from v3)
- `POC/v2/scripts/enrich_hypertension_scenarios.py` (copy from v3)
- `POC/v2/scripts/enrich_metabolic_scenarios.py` (copy from v3)
- `POC/v2/scripts/enrich_senior_scenarios.py` (copy from v3)

## Acceptance Gate

- `uv run baml-cli generate` completes without errors after adding enrichment.baml
- Enrichment scripts are importable: `uv run python -c "import scripts.enrich_healthy_scenarios"`
- (Optional) Run one enrichment script and verify output records are written to `assets/synthesis/generated/`

# GAP-0 Development Summary

## Baseline Outcome

Baseline execution completed with reproducible setup and test evidence. Step 0.5 stabilization is now complete: current-state POC runtime and harness commands execute reliably before GAP-1 work.

## What Works Reliably

- Dependency provisioning and BAML client generation (`uv sync`, `uv run baml-cli generate`).
- API startup for `POC/v2` on canonical port `:8000` after preflight port check.
- `GET /health` returns 200.
- `GET /api/v1/patients/` returns registry records.
- `POST /api/v1/clinical/recommend` returns 200 for valid registry patient (`id_1aa1b504`).
- `POST /api/v1/clinical/approve` returns success and writes audit entries.
- `GET /api/v1/clinical/audit` returns hash-chained audit records.
- `uv run pytest scripts/tests -v` now passes (`6 passed`) without manual `PYTHONPATH`.
- `uv run python scripts/test_orchestrator.py` now exits successfully.
- `uv run python scripts/tests/test_end_to_end.py` now exits successfully.
- `uv run python scripts/test_api.py` now performs local health smoke check.

## What Fails and Why

- Recommendation by README sample ID (`P001`) fails with 404 because registry uses generated IDs (`id_*` format).
- Rule/config sample files required by program ruleset tool are missing at expected v3 sample paths.
- v3 contract endpoints (`/api/recommend`, `/api/timeline/*`, `/api/monitoring-snapshot`, `/api/audit-logs`) are absent in `POC/v2` and return 404.
- Model-provider volatility can still affect semantic output shape/content across runs; this is expected at current POC stage.

## Surprises vs Expected Gap Discovery

- Additional environment-level obstacle discovered: local port-8000 collision with another running Navaveij service under `/POC`, which can mask baseline observations if not isolated.
- Audit chain behavior is healthier than expected at baseline (approve + audit endpoints are functionally wired).
- Data fixture drift is larger than expected (`P001` assumptions are stale versus current registry IDs).

## Gap Mapping

- GAP-1 API Contract: v3 endpoint absence confirmed (all 404).
- GAP-2 Stage-2 Schema: recommendation path and E2E harness are now runnable for schema-focused checks.
- GAP-3 MCP Token Alignment: request model still `patient_id`; v3-style `patient_token` endpoint not available.
- GAP-4 / GAP-5 Screens 2/3 contracts: no timeline/monitoring snapshot API support in backend.
- GAP-6 Security/RBAC: not baseline-validated yet; discovered adjacent risk in non-baseline script that contains hardcoded API key.
- GAP-7 Terminology Evidence: not validated in this run.
- GAP-8 Frontend Reliability: not executed in this baseline run.
- GAP-9 Verification Pack: baseline evidence now established in checkpoint artifacts.

## Readiness for Next Execution Order

1. Baseline readiness gate is satisfied for current-state POC execution.
2. Start GAP-1 contract alignment workstream from this stabilized baseline.
3. Keep using preflight port check + dynamic registry ID selection in verification scripts.
4. Track unresolved items as gap work, not baseline instability:
   - v3 endpoint absence
   - missing v3 sample ruleset artifacts

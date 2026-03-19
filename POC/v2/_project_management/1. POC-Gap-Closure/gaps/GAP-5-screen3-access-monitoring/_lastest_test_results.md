# Latest Test Results

Status: Complete

## Backend contract and role-gate checks

- Command: `uv run pytest scripts/tests/test_access_monitoring_contract.py scripts/tests/test_api_contract_routes.py -v`
- Result: `14 passed`
- Coverage highlights:
  - Admin and DPO role access accepted for Screen-3 endpoints
  - Non-admin role rejected with 403
  - Audit hash recomputation matches `sha256_hash`
  - Admin alias routes respond successfully
  - Contract routes for anomaly/RBAC/mapping/master verified

## Full backend regression

- Command: `uv run pytest scripts/tests -v`
- Result: `22 passed`

## Frontend build verification

- Command: `npm run build`
- Result: success; static routes include `/access-monitoring`, `/audit`, and `/trend-timeline`

## Runtime manual smoke evidence

- Production server startup (`npm run start -- --port 3001`) succeeds and serves `/access-monitoring`.
- Dev server (`npm run dev -- --port 3001`) hit a Turbopack panic in this environment; production start path was used for manual smoke validation.

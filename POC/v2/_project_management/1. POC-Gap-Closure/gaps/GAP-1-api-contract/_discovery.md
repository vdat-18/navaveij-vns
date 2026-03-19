# Discovery

Status: In progress

## Scope executed

- Added v3 contract route surface under `/api` while preserving `/api/v1` compatibility.
- Implemented required endpoints:
  - `POST /api/recommend`
  - `GET /api/timeline/{patient_token}`
  - `GET /api/monitoring-snapshot`
  - `GET /api/audit-logs`
- Added backend contract tests for all new endpoints and legacy route continuity.

## Key implementation decisions

- Input boundary for new recommendation route is `patient_token`.
- Internal orchestration remains `patient_id`-based; mapping resolves token to registry record first.
- `/api/recommend` returns a contract envelope with `patient_id`, `patient_token`, `patient_name`, and nested `recommendation`.
- `/api/timeline/{patient_token}` is assembled from audit history for the patient; when no events exist, a deterministic fallback event is emitted.
- `/api/monitoring-snapshot` derives metrics from current audit logs (`total_audit_entries`, `unique_patient_count`, `recent_decisions_24h`).
- `/api/audit-logs` normalizes existing audit schema into queryable fields and supports filters:
  - `user_id`
  - `patient_token_prefix`
  - `action_type`
  - `resource_type`
  - `start_date`
  - `end_date`

## Files changed

- `backend/src/api/routes/contracts.py` (new)
- `backend/src/api/main.py` (updated to mount `/api` router)
- `scripts/tests/test_api_contract_routes.py` (new)

# Latest Test Results

Status: Passed

## Command 1

```bash
uv run pytest scripts/tests/test_api_contract_routes.py -v
```

Result:

- 6 passed
- Verified:
  - `POST /api/recommend` success and invalid-token behavior
  - `GET /api/timeline/{patient_token}`
  - `GET /api/monitoring-snapshot`
  - `GET /api/audit-logs` filter behavior
  - legacy `GET /api/v1/clinical/audit` compatibility

## Command 2

```bash
uv run pytest scripts/tests -v
```

Result:

- First run: 1 failed, 11 passed (non-deterministic LLM output parsing in `test_end_to_end`)
- Re-run immediately after: 12 passed
- Final verification status for this checkpoint: pass

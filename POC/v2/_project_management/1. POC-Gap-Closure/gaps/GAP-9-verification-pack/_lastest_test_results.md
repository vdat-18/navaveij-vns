# Latest Test Results

Status: Updated

## Deterministic verification matrix

- Command:
  - `uv run pytest scripts/tests/test_gap9_verification_pack.py scripts/tests/test_api_contract_routes.py scripts/tests/test_security_rbac_contract.py scripts/tests/test_timeline_contract_payload.py scripts/tests/test_access_monitoring_contract.py scripts/tests/test_frontend_terminology_visibility.py scripts/tests/test_frontend_reliability_contract.py -v`
- Result:
  - `34 passed in 0.47s`

## Regression suite

- Command:
  - `uv run pytest scripts/tests -v`
- Result:
  - `40 passed in 53.04s`
- Note:
  - `test_end_to_end` now runs with external-dependency classification guard logic for LLM availability/outage behavior.

## Frontend build gate

- Command:
  - `npm run build` in `POC/v2/frontend`
- Result:
  - `zsh: command not found: npm`
- Runtime check:
  - `uv run python -c "import shutil; print(shutil.which('npm')); print(shutil.which('node'))"` → `None`, `None`

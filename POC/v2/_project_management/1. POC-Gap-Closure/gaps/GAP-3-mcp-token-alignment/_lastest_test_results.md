# Latest Test Results

Status: Passed

## Command 1

```bash
uv run pytest scripts/tests/test_api_contract_routes.py -v
```

Result:

- 7 passed
- Verified:
  - `/api/recommend` token-first behavior
  - `/api/v1/clinical/recommend` legacy adapter path still active
  - existing contract endpoints remain healthy

## Command 2

```bash
uv run pytest scripts/tests -v
```

Result:

- 13 passed
- Includes workflow token-call validation and full regression sweep.

## Frontend build check

```bash
npm run build
```

Result:

- failed with `next: command not found`
- indicates missing local frontend runtime dependency in current environment, not a TypeScript compile error from changed files

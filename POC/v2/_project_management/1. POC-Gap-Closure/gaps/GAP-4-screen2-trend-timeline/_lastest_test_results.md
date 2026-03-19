# Latest Test Results

Status: Passed

## Backend contract tests

```bash
uv run pytest scripts/tests/test_timeline_contract_payload.py -v
```

Result:

- 2 passed
- Timeline route returns required event-timeline sections and handles invalid token with 404.

```bash
uv run pytest scripts/tests/test_api_contract_routes.py -v
```

Result:

- 9 passed
- Includes timeline contract shape assertions and new Screen 2 data endpoint checks.

```bash
uv run pytest scripts/tests -v
```

Result:

- 17 passed
- Full backend regression suite passed.

## Frontend verification

```bash
npm install
npm run dev -- --port 3001
```

Result:

- Dependencies installed.
- Dev server running at `http://localhost:3001`.
- Screen 2 route accessible at `http://localhost:3001/trend-timeline`.

```bash
npm run build
```

Result:

- fails due pre-existing unrelated import issue in `src/app/audit/page.tsx` (`@/lib/utils` not found).

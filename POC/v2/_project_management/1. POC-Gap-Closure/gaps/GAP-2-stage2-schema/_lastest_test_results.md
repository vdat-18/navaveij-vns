# Latest Test Results

Status: Passed

## Command 1

```bash
uv run pytest scripts/tests/test_api_contract_routes.py -v
```

Result:

- 6 passed
- Includes Stage-2 assertions for `/api/recommend`:
  - top-level Stage-2 fields present
  - communication script opening mapping
  - add-on enrichment and metadata presence

## Command 2

```bash
uv run pytest scripts/tests -v
```

Result:

- First run: 1 failed, 11 passed (`test_end_to_end` transient LLM failure)
- Re-run: 12 passed
- Final verification status for this checkpoint: pass

# Latest Test Results

Status: Updated

## Phase 1-2 verification

- Command:
  - `uv run pytest /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2/scripts/tests/test_backend_cache_ttl.py /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2/scripts/tests/test_api_contract_routes.py /Users/nguyen.tran/Documents/GitHub/navavej/navaveij/POC/v2/scripts/tests/test_ruleset_path_resolution.py -v`
- Result:
  - `16 passed in 0.44s`

## Coverage highlights

- New TTL cache service behaviors:
  - set/get cycle works
  - immediate expiry behavior works
- Loader-path cache integration verified through:
  - ruleset tier/add-on/package map loading
  - patient registry and token resolution
  - signal store record lookup
- Contract regression coverage remained green for `/api/recommend`, timeline/trends/screening, and monitoring support routes.
- Recommendation cache behavior verified:
  - first `/api/recommend` response marks `cache_status=miss`
  - second same-key request marks `cache_status=hit`
  - LLM orchestration call is skipped on cache hit (await count remains 1)

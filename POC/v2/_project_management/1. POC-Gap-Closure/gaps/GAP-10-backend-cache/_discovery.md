# Discovery

Status: Updated

## Findings

- Recommendation and MCP loader paths had no app-level TTL cache in v2 backend.
- Ruleset and registry loaders repeatedly read JSON files across calls.
- Signal-store record lookup scans generated records each request path and benefits from short-lived token/id cache.
- Frontend cache is intentionally excluded in this gap per scope decision.

## Decisions

- Implement backend-only TTL cache service in `backend/src/services/cache.py`.
- Apply Phase 2 caching to:
  - patient registry loader
  - signal-store record loader
  - ruleset tier/add-on/package map loaders
- Defer recommendation response cache (Phase 3) until explicit approval.

# LLM Cache with TTL Plan — Backend-First Strategy

## Recommendation

Implement cache at the **backend as the source of truth** for recommendation requests, and keep frontend caching as an optional short-lived UX optimization only for non-sensitive read paths.

## Why backend-first

- The expensive path (MCP aggregation + LLM generation + safety validation) happens in backend orchestration.
- Backend can enforce RBAC/scope, privacy masking assumptions, and audit policy consistently.
- Backend can use medically meaningful cache keys (patient token + pipeline/ruleset/model versions) and invalidate safely.
- Frontend-only cache cannot prevent backend recomputation when users refresh, switch clients, or use multiple sessions.

## Scope

### A) L1 cache (safe + high ROI)

1. Cache static/reference loaders:
   - ruleset tier config
   - ruleset add-on items
   - package resolution map
2. Cache signal-store record lookup by patient token/patient id mapping.
3. Cache patient registry map used by token/id resolver.

**TTL suggestion:** 5–15 minutes (or file-mtime/version-aware refresh).

### B) L2 cache (LLM result cache)

Cache normalized recommendation payload for `/api/recommend` with strict keying:

`cache_key = hash(patient_token + signal_pipeline_run_id + ruleset_version + model_id + template_version + auth_mode)`

**TTL suggestion:** 2–10 minutes for demo mode (start with 5m).

## Backend cache policy

### Cache hit behavior

- Return cached recommendation payload directly.
- Record audit entry with `cache_status: "hit"` and reference to source cache key/request id.
- Skip LLM call and safety critic rerun on hit.

### Cache miss behavior

- Execute full orchestration path.
- Persist audit as today with `cache_status: "miss"`.
- Store result in cache with TTL.

### Invalidation rules

- Invalidate on any change in:
  - `signal_store_pipeline_run_id`
  - `ruleset_version`
  - `model_id`
  - `template_version`
- Manual purge endpoint for admin use (optional).
- Optional file-watch/mtime-triggered invalidation for local assets.

## Frontend cache policy

- Do **not** use frontend as authoritative recommendation cache.
- Optional micro-cache (in-memory/session) for UX:
  - patient list
  - trend/timeline bundle
  - monitoring snapshot (short TTL <= polling interval)
- Avoid persisting recommendation payloads in local storage.

## Security & compliance considerations

- Keep cache in backend process memory or Redis with controlled ACL.
- Cache only pseudonymized token-based payloads already returned by API.
- Never cache raw secrets or full prompt context with sensitive internals unless encrypted and policy-approved.
- Preserve auditability: every recommendation response (hit/miss) must remain traceable.

## Proposed implementation phases

### Phase 1 — Foundation cache service

- Add `backend/src/services/cache.py` with TTL get/set/delete abstraction.
- Start with in-memory TTL cache (dict + expiry); keep interface Redis-ready.

### Phase 2 — L1 caches

- Wrap ruleset/signal/patient-registry loaders in TTL cache.
- Add tests for cache hit/miss and stale refresh.

### Phase 3 — L2 recommendation cache

- Add cache check/store around `/api/recommend` normalization boundary.
- Include versioned key builder and invalidation logic.
- Add tests for:
  - hit avoids LLM call
  - miss triggers LLM call
  - key changes force miss

### Phase 4 — Observability

- Add cache metrics:
  - hit rate
  - miss count
  - stale invalidations
  - average latency reduction
- Add structured fields in logs/audit (`cache_key_hash`, `cache_status`, `cache_ttl_seconds`).

## Verification checklist

1. Same request within TTL returns identical payload and records cache hit.
2. Changed signal pipeline run id forces recompute.
3. Changed model/template version forces recompute.
4. Authorization boundaries unchanged (no cross-role leakage).
5. Audit entries present and distinguish hit/miss.
6. End-to-end regression remains green.

## Final position on your question

- **Should we add LLM cache with TTL?** Yes — strong performance and cost win.
- **Backend or frontend?** Backend-first for recommendation caching; frontend only for lightweight UX caching on non-authoritative reads.

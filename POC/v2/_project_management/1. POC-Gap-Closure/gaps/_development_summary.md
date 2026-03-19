## GAP-0 — Baseline Run & Stabilization

- Status: Complete
- Executed full baseline setup: uv sync, BAML generation, .env configuration, API startup.
- Discovered port 8000 collision with co-located Navaveij service; isolated POC to port 8010.
- Confirmed registry IDs are in `id_*` format; stale `P001` ID replaced with dynamic fixture selection.
- Resolved PYTHONPATH issues and async test runner failures in test harness.
- Step 0.5 stabilization gate met: API starts cleanly, recommendation endpoint succeeds for valid fixture IDs, all canonical tests pass (6 passed).

## GAP-1 — API Contract Alignment

- Status: Complete
- Delivered new contract route module `backend/src/api/routes/contracts.py` with all four required v3 endpoints.
- Mounted `/api` prefix in `backend/src/api/main.py`; legacy `/api/v1` retained for compatibility.
- Delivered contract test suite `scripts/tests/test_api_contract_routes.py`.
- Verified with `6 passed` in contract suite and `12 passed` full regression.

## GAP-2 — Stage-2 Schema Completion

- Status: Complete
- Extended `/api/recommend` response to emit Stage-2-shaped output directly: tier alignment context, enriched add-ons (label/category/navavej_product/trigger_signals_matched), confidence score (deterministic formula: signal coverage × data completeness × rule agreement), high-alert section, and metadata envelope.
- All assembly logic in `backend/src/api/routes/contracts.py`.
- Verified with `6 passed` in contract suite and `12 passed` full regression.

## GAP-3 — MCP Token Alignment

- Status: Complete
- Established `patient_token` as canonical boundary key for `/api/recommend` request, MCP tool call parameters, and workflow orchestration.
- Delivered centralized patient id/token resolvers and token-first MCP tool signatures with optional legacy `patient_id` adapter.
- Migrated frontend recommendation call to `/api/recommend` with `patient_token`; v1 legacy routes retained.
- Verified with `7 passed` in contract suite and `13 passed` full regression.

## GAP-4 — Screen 2 Trend & Timeline

- Status: Complete
- Delivered MCP tool `get_patient_event_timeline` and contract route `GET /api/timeline/{patient_token}` returning event-timeline shape (timeline_span, diagnoses, hospitalizations, significant_lab_events, screening_procedure_history, medication_changes).
- Added supporting Screen 2 endpoints: `GET /api/biomarker-trends/{patient_token}`, `GET /api/screening-gaps/{patient_token}`.
- Delivered frontend `/trend-timeline` route with 6-chart trend grid, clinical event timeline, and screening gap status panel with shared range filter.
- Verified with `2 passed` timeline contract tests, `9 passed` API contract suite, `17 passed` full regression.

## GAP-5 — Screen 3 Access Monitoring

- Status: Complete
- Delivered backend contract and role-gated endpoints for Screen-3 domains.
- Delivered frontend Screen-3 route/components with anomaly, audit/hash verification, and governance tabs.
- Verified with passing backend tests and successful frontend production build.

## GAP-7 — Terminology Evidence

- Status: Complete
- Delivered backend mapping normalization with v3-style target terminology fields and compatibility keys.
- Delivered timeline terminology propagation for diagnosis and screening events, including ICD10/SNOMED/CPT evidence.
- Delivered frontend terminology visibility enhancements in timeline rows and mapping table columns.
- Added strict terminology verification in timeline/mapping suites and frontend visibility tests.

## GAP-6 — Security RBAC

- Status: Complete
- Delivered centralized auth-context and role/scope authorization dependency in backend.
- Enforced protected access behavior on recommendation/timeline endpoints and monitoring/admin routes.
- Updated frontend API calls to send auth-context headers consistently and removed role-switch impersonation selector.
- Added GAP-6 security regression tests for unauthorized, wrong-role, missing-scope, and authorized paths.
- Executed targeted GAP-6 security suite with `23 passed`.

## GAP-8 — Frontend Reliability

- Status: In verification
- Delivered route-safe dashboard navigation and sidebar route wiring.
- Delivered guarded async bootstrap/error handling for Screen 2 and Screen 3 data loading flows.
- Added targeted frontend reliability contract tests and executed them successfully (`5 passed`).
- Build evidence remains environment-blocked in this runtime (`npm` unavailable), so final completion is pending build capture.

## GAP-9 — Verification Pack

- Status: In verification
- Delivered `test_gap9_verification_pack.py` as a closure-oriented smoke harness for required modules and key Screen 1/2/3 API routes.
- Delivered external dependency classification improvements in `test_end_to_end.py` via LLM env readiness skip and outage xfail handling.
- Executed deterministic verification matrix (`34 passed`) and full regression (`40 passed`).
- Frontend build gate remains blocked in this runtime (`npm` unavailable), so final GAP-9 completion is pending Node-enabled build evidence.

## GAP-10 — Backend Cache

- Status: Complete
- Delivered backend TTL cache service and cache settings/env surface.
- Applied Phase 2 loader-path caching to ruleset loaders, signal-store record lookup, and patient registry loaders.
- Applied Phase 3 recommendation-response cache at `/api/recommend` with keying and metadata cache status (`hit`/`miss`).
- Added backend cache test coverage and executed targeted regression (`16 passed`).

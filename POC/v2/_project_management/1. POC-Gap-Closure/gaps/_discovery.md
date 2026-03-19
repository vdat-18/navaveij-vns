## GAP-0 — Baseline Run

- macOS 26.3.1, Python 3.12.12, UV 0.10.5 runtime environment confirmed (2026-03-18).
- .env was missing on initial checkout; added and updated before recommendation path could execute.
- Port 8000 collision with co-located `/POC` service discovered; port 8010 designated for this POC workspace.
- API/contract discovery: v3 endpoints all returned 404; registry IDs are `id_*` format, not `P001`.
- pytest path issues and missing LLM env vars identified and resolved in test harness.
- Step 0.5 stabilization: environment/path bootstrap improvements applied; dynamic registry ID selection implemented; canonical test set runs cleanly before GAP-1.

## GAP-1 — API Contract Alignment

- Scope: Add v3 contract route surface under `/api` while preserving `/api/v1` compatibility.
- Endpoints added: POST /api/recommend, GET /api/timeline/{patient_token}, GET /api/monitoring-snapshot, GET /api/audit-logs.
- Input boundary uses `patient_token`; internal orchestration remains `patient_id`-based via token-to-registry mapping.
- `/api/recommend` returns contract envelope with patient identity and nested recommendation.
- `/api/timeline` assembles event-timeline from audit history with fallback events.
- `/api/monitoring-snapshot` derives metrics from audit logs.
- `/api/audit-logs` normalizes existing schema with filters: user_id, patient_token_prefix, action_type, resource_type, start_date, end_date.

## GAP-2 — Stage-2 Schema Completion

- Scope: Migrate `/api/recommend` output from transitional wrapper to Stage-2-shaped response.
- Stage-1 fields sourced from orchestrator AI output; enrichment sourced from `get_program_ruleset(patient_id)`.
- Add-on enrichment fields: label, category, navavej_product, trigger_signals_matched.
- Confidence computation: deterministic formula using signal_coverage × data_completeness × rule_agreement; thresholds: High ≥0.75, Medium ≥0.50, Low <0.50.
- Contract-shape normalizations: clinical_conclusion mapped to opening; high_alert built from risk_flags and missing_signals.
- Metadata fields: request_id, patient_token, model_id, template_version, ruleset_version, signal_store_pipeline_run_id, generated_at, latency_ms.

## GAP-3 — MCP Token Alignment

- Scope: Implement token-first contract behavior from API boundary through MCP tool inputs; retain `/api/v1` compatibility with id-to-token adapter.
- Canonical boundary key: `patient_token` for /api/recommend request, MCP tool primary parameters, and workflow MCP calls.
- Centralized resolver utilities for patient id/token lookup in backend and MCP server.
- MCP tool signatures updated to accept `patient_token` (primary) with optional `patient_id` adapter field.
- Orchestrator updated with token auto-resolution fallback.
- Frontend API client migrated to `/api/recommend` with `patient_token`; approve/audit routes remain on v1.

## GAP-4 — Screen 2 Trend & Timeline

- Scope: Add contract-backed timeline data path for Screen 2 and dedicated frontend route.
- MCP tool `get_patient_event_timeline(patient_token, patient_id=None)` registered and callable.
- `/api/timeline/{patient_token}` returns event-timeline contract shape with 6 required sections.
- Supporting endpoints: `GET /api/biomarker-trends/{patient_token}`, `GET /api/screening-gaps/{patient_token}`.
- Frontend: dedicated page route `/trend-timeline`; Screen 2 isolated from Screen 1 with shared time-range selector; summary/governance routes preserved.
- Pre-existing import issue in `src/app/audit/page.tsx` (@/lib/utils) blocked `npm run build` but did not block dev server or Screen 2 functionality; tracked under GAP-8.

## GAP-5 — Screen 3 Access Monitoring

- Implemented contract-aligned Screen-3 backend data domains: monitoring snapshot, anomaly alerts, audit search, RBAC, mapping, and master programs.
- Added role-gated behavior for admin/dpo with 403 for unauthorized roles.
- Added dedicated Screen-3 frontend route `/access-monitoring` and panel/tabs composition with hash verification UX.

## GAP-7 — Terminology Evidence

- Identified contract mismatch where mapping payload lacked full v3-style target terminology fields.
- Identified timeline synthesis gaps where diagnosis/procedure terminology fields were present but often empty.
- Confirmed required evidence path is Screen-2 timeline plus Screen-3 mapping table with visible LOINC/SNOMED/ICD systems.
- Tightened GAP-7 verification to require non-empty terminology-bearing timeline sections and explicit CPT system coverage.
- Added frontend terminology visibility checks for timeline and mapping components to support UI evidence.

## GAP-6 — Security RBAC

- Replaced mutable role-header-only approach with centralized auth-context extraction at API boundary.
- Added explicit role + scope checks for recommendation and monitoring routes, including legacy `/api/v1/clinical` endpoints.
- Confirmed need for negative-path evidence: missing auth (401), invalid role (403), and missing scope (403).

## GAP-8 — Frontend Reliability

- Confirmed previous import-path issue in the original GAP-8 note is already resolved in current source.
- Identified current reliability risks in active UI flow: dead dashboard links, inert sidebar controls, and unguarded async bootstrap failures.
- Re-scoped GAP-8 closure to executable navigation stability and async failure handling evidence.

## GAP-9 — Verification Pack

- Identified that existing tests lacked an explicit closure-oriented verification pack structure.
- Added a pack-level smoke harness and deterministic matrix framing for GAP-1..8 contract-critical behaviors.
- Identified frontend build as the remaining environment-dependent gate because runtime lacks Node/npm.

## GAP-10 — Backend Cache

- Confirmed backend lacked a reusable TTL cache layer for repeated loader paths.
- Identified Phase 1-2 insertion points: ruleset loaders, signal-store record lookup, and patient registry loading.
- Locked scope to backend-only caching and completed Phase 3 at `/api/recommend` after approval.

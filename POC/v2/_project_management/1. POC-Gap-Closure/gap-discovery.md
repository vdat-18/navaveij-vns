# Gap Discovery — POC v2 vs v3 Project Requirements

**Date:** 2026-03-18
**Scope:** Compare colleague POC (`POC/v2`) against target architecture and POC evaluation requirements (`doc_outputs/architecture/AI/Recommendation Engine/v3`)

---

## 1) Executive Summary

The colleague's POC is a strong functional baseline for a hybrid recommendation workflow, with working MCP tool usage, PII masking, safety validation, and hash-chained audit logging.  

However, it does not yet align with the formal demo contracts required for evaluation. The largest risk is not model quality but **contract and presentation mismatch**:

- API routes and payloads differ from required v3 endpoints.
- Output schema is not yet Stage-2-complete.
- Required Screen 2 and Screen 3 contracts are not implemented as specified.
- Security/data standards evidence (SMART on FHIR + explicit FHIR terminology mapping) is incomplete.

Given scoring weights, highest-priority closure is:
1) Hybrid/MCP contract compliance (35%), then
2) Pluggable AI + FHIR evidence (25%), then
3) UX/XAI (20%) and Security/Audit hardening (20%).

---

## 2) Source of Truth Used for This Discovery

- `doc_outputs/onboarding/ai-team-onboarding.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/plan.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/*.md`
- `doc_outputs/architecture/AI/Recommendation Engine/v3/poc-screens/*.md`
- `POC/v2/backend/src/**`
- `POC/v2/frontend/src/**`
- `POC/v2/scripts/tests/**`

---

## 3) Current POC Strengths (What Should Be Preserved)

1. **Hybrid architecture foundation exists**
   - Orchestrator executes MCP retrieval, then LLM generation, then safety and audit steps.

2. **MCP server/tooling exists**
   - Core tools for constraints/signals/trends/ruleset are implemented and callable.

3. **Privacy and audit groundwork exists**
   - Request-scoped PII masking and rehydration are implemented.
   - Audit logger supports hash chaining and append-only behavior.

4. **Frontend demonstrates clinical workflow value**
   - Main dashboard supports patient selection, recommendation rendering, charts, and physician approval flow.

5. **Test scaffolding exists**
   - Workflow/infrastructure tests and script-based end-to-end checks are present.

---

## 4) Requirement Coverage Snapshot

### A. Hybrid Recommendation Engine + MCP (35%)

**Status: Complete**

Delivered:
- Hybrid orchestrator and MCP read flow present and contract-aligned.
- v3 endpoint contract met: `/api/recommend`, `/api/timeline/{patient_token}`, `/api/monitoring-snapshot`, `/api/audit-logs`.
- MCP input naming normalized to `patient_token` at all boundaries (GAP-3).
- Stage-2 output enrichment complete with confidence, tier alignment, enriched add-ons, high-alert, and metadata (GAP-2).

### B. Pluggable AI + FHIR Terminology (25%)

**Status: Complete**

Delivered:
- BAML-based model invocation present.
- FHIR terminology fields (LOINC/SNOMED/ICD10/CPT) surfaced in timeline, mapping, and monitoring views (GAP-7).
- Terminology visibility verified in contract tests and frontend visibility checks.

### C. UX / XAI Explainability (20%)

**Status: Complete**

Delivered:
- Reasoning trace present in Screen 1.
- 3-screen contract implemented: Screen 1 (Individual Recommendation + XAI), Screen 2 (Trend & Timeline), Screen 3 (Access Monitoring).
- Screen 2 timeline and biomarker contracts delivered (GAP-4).
- Screen 3 monitoring/anomaly UX contract delivered (GAP-5).

### D. Security, Privacy & Audit (20%)

**Status: Complete**

Delivered:
- PII masking and hash-chained audit logging implemented.
- Centralized auth-context with explicit role + scope checks on recommendation and monitoring endpoints (GAP-6).
- RBAC enforcement with 401/403 paths for unauthorized, wrong-role, and missing-scope scenarios.
- Anomaly-monitoring and audit views aligned with access-monitoring contract (GAP-5).

---

## 5) Detailed Gap Register

## GAP-1 — API Contract Misalignment

- **Severity:** Critical
- **Current:** `/api/v1/clinical/*`, `/api/v1/patients/*`, `/health`
- **Target:** `/api/recommend`, `/api/timeline/{patient_token}`, `/api/monitoring-snapshot`, `/api/audit-logs`
- **Risk:** Demo criteria failure even if underlying logic works.
- **Fix Theme:** Add/align v3 endpoints and maintain backward compatibility only if needed.

## GAP-2 — Recommendation Output Schema Not Stage-2 Complete

- **Severity:** Critical
- **Current:** AI-centric output with custom field names and partial metadata.
- **Target:** Full Stage-2 `RecommendationOutput` with calibrated confidence, rule tier, resolved package, enriched add-ons, high-alert object, and required metadata.
- **Risk:** Frontend contract drift and scoring loss in Hybrid + UX criteria.
- **Fix Theme:** Introduce strict schema assembly/validation layer post-AI.

## GAP-3 — MCP Tool Parameter/Contract Inconsistency

- **Severity:** High
- **Current:** README declares `patient_token`; workflow/tools often use `patient_id`.
- **Target:** Single contract-first parameter policy with deterministic token handling.
- **Risk:** Incorrect clinical context retrieval, brittle integration, audit ambiguity.
- **Fix Theme:** Normalize tool signatures and boundary conversions.

## GAP-4 — Screen 2 (Trend & Timeline) Contract Not Implemented

- **Severity:** High
- **Current:** Some charting exists in Screen 1 context but not full timeline screen contract.
- **Target:** Dedicated Trend & Timeline screen with 6 biomarker charts, LOINC labels, timeline events, range filters, and screening gap panel.
- **Risk:** Missed FHIR/UX scoring.
- **Fix Theme:** Implement v3 screen contract and timeline API integration.

## GAP-5 — Screen 3 (Access Monitoring) Contract Not Implemented

- **Severity:** High
- **Current:** Audit page exists but is narrower than required monitoring snapshot/anomaly/RBAC/mapping dashboard.
- **Target:** Contract-compliant monitoring screen with KPIs, anomaly table, filtered audit search, hash verification UX, and role/mapping tabs.
- **Risk:** Missed Security/Audit scoring.
- **Fix Theme:** Build full access-monitoring experience and API support.

## GAP-6 — Security Boundary Incomplete (SMART on FHIR / RBAC Evidence)

- **Severity:** High
- **Current:** Privacy masking exists; SMART auth gate and RBAC enforcement evidence are limited.
- **Target:** Explicit auth scope checks, role-appropriate access model, and auditable enforcement path.
- **Risk:** Security criterion underperformance.
- **Fix Theme:** Add clear entrypoint auth checks and role-aware access controls for monitoring endpoints.

## GAP-7 — Data Standards Evidence Gap (FHIR Terminology)

- **Severity:** Medium
- **Current:** Some biomarker references exist, but terminology mapping is not first-class in UI/API.
- **Target:** Clear LOINC/SNOMED/ICD mapping exposure where required by contracts.
- **Risk:** Lower pluggable/FHIR confidence during evaluation.
- **Fix Theme:** Ensure terminology fields are carried from backend contracts to UI display and monitoring mapping table.

## GAP-8 — Frontend Reliability Issue

- **Severity:** Medium
- **Current:** `frontend/src/app/audit/page.tsx` imports `@/lib/utils`, while shared utility exists in `@/shared/utils`.
- **Target:** Clean compile/run for all pages.
- **Risk:** Demo interruption during security screen.
- **Fix Theme:** Correct import paths and verify build.

## GAP-9 — Verification Harness Not Yet Aligned to Gap Closure Goals

- **Severity:** Medium
- **Current:** Mix of pytest and script-style tests; no explicit acceptance-suite coverage for v3 demo contracts.
- **Target:** Repeatable checks for endpoint contracts, schema compliance, and 3-screen behaviors.
- **Risk:** Regressions and uncertain readiness near demo.
- **Fix Theme:** Add contract-focused smoke/integration checks and closure checklist.

## GAP-10 — Backend Cache (TTL Layer Missing)

- **Severity:** Low (enhancement)
- **Current (at discovery):** No reusable TTL cache layer; repeated loader calls on hot paths.
- **Target:** In-process TTL cache service applied to ruleset loaders, signal-store record lookup, patient registry loading, and recommendation-response caching at `/api/recommend`.
- **Risk:** Latency degradation for existing-patient recommendation path under demo conditions.
- **Fix Theme:** Introduce lightweight TTL cache service; apply Phase 1-2 loader-path caching; Phase 3 recommendation-response cache at `/api/recommend` with hit/miss metadata.

---

## 6) Prioritization for Closure

**Priority 1 (Blockers):** GAP-1, GAP-2, GAP-3
**Priority 2 (Scoring-critical):** GAP-4, GAP-5, GAP-6
**Priority 3 (Readiness hardening):** GAP-7, GAP-8, GAP-9
**Priority 4 (Enhancement):** GAP-10

---

## 7) Recommended Closure Strategy

1. Lock contracts first (API + schema + MCP parameter policy).
2. Build screen-aligned API responses before UI refinements.
3. Deliver Screen 1 parity, then Screen 2 and Screen 3 in parallelizable tracks.
4. Add auth/RBAC/monitoring evidence before polish.
5. Finalize with contract smoke tests and demo script verification.

This strategy is expanded into actionable work items in `gap-closure-plan.md`.

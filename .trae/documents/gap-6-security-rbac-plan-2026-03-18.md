# GAP-6 Implementation Plan — Security Boundary & RBAC Evidence

## Summary

Close GAP-6 by replacing header-spoofable role checks with a demonstrable auth context path, enforcing role-aware access behavior on monitoring endpoints, and producing positive/negative verification evidence that satisfies WS-C acceptance checks.

## Current State Analysis

- GAP-6 is currently marked **Not started** in:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/README.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/_discovery.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/_lastest_test_results.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/_development_summary.md`
- Existing security behavior already includes:
  - role gate for monitoring endpoints in `backend/src/api/routes/contracts.py`
  - admin/dpo role propagation from frontend in `frontend/src/services/api.ts`
- Main gaps:
  - role is taken from a mutable request header and defaults to admin when missing
  - no entrypoint authentication context for route authorization decisions
  - no robust negative-path evidence beyond basic role tests

## GAP-6 Acceptance Targets

From project plan WS-C and gap mapping:
- unauthorized requests are rejected with safe response behavior
- monitoring access paths respect role constraints
- exit evidence: unauthorized/role tests pass

## Assumptions & Decisions

- Implement a **POC-safe auth context** (not full production SMART) to provide verifiable auth scope + role claims at API boundary.
- Preserve existing `/api` route contracts while tightening access checks.
- Keep SMART-on-FHIR production-depth integration out of scope; provide a clear adapter seam for future swap-in.
- Remove permissive admin defaulting for monitoring access.

## Proposed Changes

### 1) Add centralized auth context dependency for API routes

**Files**
- Create: `POC/v2/backend/src/api/security.py`
- Update: `POC/v2/backend/src/api/routes/contracts.py`
- Update: `POC/v2/backend/src/api/routes/clinical.py`
- Update: `POC/v2/backend/src/api/routes/patients.py` (if scope-protection needed on sensitive reads)

**What**
- Add a reusable dependency that extracts and validates auth claims from request headers/token surrogate:
  - authenticated principal id
  - role claim
  - scope list (e.g., `monitoring:read`, `recommendation:write`)
- Return 401 for missing/invalid auth context.
- Return 403 for valid auth context lacking required role/scope.

**Why**
- Creates demonstrable entrypoint auth verification and decouples authorization from UI-controlled role strings.

### 2) Replace monitoring role gate with auth-context RBAC checks

**Files**
- Update: `POC/v2/backend/src/api/routes/contracts.py`

**What**
- Replace `_require_monitoring_role` behavior so:
  - no implicit default to admin
  - allowed roles remain `admin` and `dpo`
  - required scope is enforced for monitoring resources
- Keep route signatures stable for existing consumers where possible.

**Why**
- Directly addresses GAP-6 requirement: role-aware access with unauthorized rejection evidence.

### 3) Tighten API security-related configuration defaults

**Files**
- Update: `POC/v2/backend/src/api/main.py`
- Update: `POC/v2/shared/settings.py`
- Update: `POC/v2/.env.example` (if present)

**What**
- Restrict CORS from wildcard to configured allowed origins list for POC environments.
- Add explicit settings for:
  - auth mode (`poc_claims` default)
  - required monitoring scope name(s)
  - allowed monitoring roles

**Why**
- Provides safer baseline and explicit security toggles for reproducible validation.

### 4) Update frontend API client to send auth context consistently

**Files**
- Update: `POC/v2/frontend/src/services/api.ts`
- Update: `POC/v2/frontend/src/app/access-monitoring/page.tsx`
- Update: `POC/v2/frontend/src/components/access-monitoring/AccessMonitoringScreen.tsx`

**What**
- Stop role-only behavior as primary authority signal.
- Send auth-context headers/token stub from a single client helper.
- Keep role selector only as a test harness mode when explicitly enabled (or remove if unnecessary).

**Why**
- Ensures frontend behavior aligns with backend auth model and prevents accidental role spoof assumptions.

### 5) Expand GAP-6 verification tests (positive + negative paths)

**Files**
- Update: `POC/v2/scripts/tests/test_access_monitoring_contract.py`
- Update: `POC/v2/scripts/tests/test_api_contract_routes.py`
- Add: `POC/v2/scripts/tests/test_security_rbac_contract.py` (if separation improves clarity)

**What**
- Add explicit cases:
  - missing auth context → 401
  - malformed auth context → 401
  - authenticated but wrong role → 403
  - authenticated with right role but missing scope → 403
  - authenticated admin/dpo with required scope → 200
- Keep existing route contract checks intact.

**Why**
- GAP-6 exit evidence requires unauthorized/role tests pass with clear negative-path proofs.

### 6) Update GAP-6 evidence artifacts and rollups

**Files**
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/README.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/_discovery.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/_lastest_test_results.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-6-security-rbac/_development_summary.md`
- Update rollups under `POC/v2/_project_management/POC-Gap-Closure/gaps/`

**What**
- Record design decisions, auth model, negative-path evidence, and closure assessment.

## Verification Plan

1. Run targeted GAP-6 security tests for auth/role/scope.
2. Run broader contract regression suite to protect GAP-1..5/7 behavior.
3. Validate frontend build/runtime for access-monitoring path under new auth model.
4. Confirm acceptance evidence:
   - 401 on missing/invalid auth
   - 403 on insufficient role/scope
   - 200 on permitted admin/dpo access

## Risks & Mitigations

- **Risk:** Tightened auth checks could break existing manual demo flows.
  - **Mitigation:** provide explicit POC auth stub headers and clear local test profile defaults.
- **Risk:** CORS tightening may block local ports unexpectedly.
  - **Mitigation:** make origins configurable and include existing known dev origins.
- **Risk:** Security changes may impact prior GAP route tests.
  - **Mitigation:** run targeted + regression suites and adjust tests to include auth context fixture.

## Out of Scope

- Full production SMART-on-FHIR token introspection and external IdP integration.
- Enterprise-grade policy engine or ABAC beyond GAP-6 contract evidence needs.
- Final cross-gap verification pack orchestration (GAP-9 scope).

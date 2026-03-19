# GAP-5 Implementation Plan — Screen 3 Access Monitoring Contract

## Summary

Implement GAP-5 by delivering a dedicated Screen 3 (Access Monitoring) that is contract-aligned with v3 specs, including:
- live KPI metrics bar from monitoring snapshot
- anomaly alerts table with status actions
- audit log search and row drilldown
- client-side hash verification UX
- secondary tabs for role matrix, terminology mapping, and master data

This plan covers backend contract additions, frontend Screen 3 implementation, RBAC/access behavior, verification evidence, and checkpoint updates.

## Current State Analysis

- GAP-5 is currently not started in:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-5-screen3-access-monitoring/README.md`
- Existing `/api/monitoring-snapshot` and `/api/audit-logs` are present but narrower than Screen-3 contract requirements:
  - `POC/v2/backend/src/api/routes/contracts.py`
- No dedicated anomaly, RBAC, mapping, or master-data contract routes exist in POC/v2 backend.
- Existing frontend `/audit` page does not implement Screen-3 layout/flow and lacks anomaly + secondary tab experience:
  - `POC/v2/frontend/src/app/audit/page.tsx`
- A pre-existing import mismatch is present in audit page (`@/lib/utils`), while local utility location is under shared utilities.
- v3 references contain complete Screen-3 contract definitions and sample structures:
  - `doc_outputs/architecture/AI/Recommendation Engine/v3/poc-screens/screen-3-access-monitoring.md`
  - `doc_outputs/architecture/AI/Recommendation Engine/v3/schema-contracts/access-monitoring-contract.md`

## Assumptions & Decisions

- Deliver GAP-5 as a dedicated Screen-3 route/components in POC/v2 instead of overloading the current `/audit` page.
- Keep `/api` contract routes as primary integration surface, consistent with GAP-1/2/3/4 progression.
- Implement demo-grade role boundary in UI/API for `admin` and `dpo`, while reserving deeper SMART/RBAC enforcement hardening for GAP-6.
- Reuse existing audit hash-chain fields and provide deterministic client-side verification against displayed entry payload.
- Keep patient token masking behavior in Screen-3 tables and drilldowns.

## Proposed Changes

### 1) Extend backend contract routes for Screen-3 data domains

**Files**
- Update: `POC/v2/backend/src/api/routes/contracts.py`

**What**
- Expand monitoring snapshot payload to include required KPI fields:
  - `active_users_now`
  - `sessions_today`
  - `patient_records_accessed_today`
  - `ai_recommendations_generated_today`
  - `alert_counts` (critical/high/medium/low)
  - `safety_validator_failures_today`
  - `snapshot_at`
- Add contract routes for:
  - anomaly alerts list/search
  - role matrix listing
  - mapping table listing
  - master data listing
- Extend audit search payload/filters to match Screen-3 use cases (user/action/resource/date/token-prefix).

**Why**
- GAP-5 requires a full Screen-3 contract surface beyond current snapshot/audit-only endpoints.

**How**
- Reuse existing data loaders and normalized response helpers.
- Map available local sample/generated data to v3-like contract keys with safe defaults.

### 2) Add Screen-3 access guard behavior at API boundary

**Files**
- Update: `POC/v2/backend/src/api/routes/contracts.py`
- Update (if needed): `POC/v2/backend/src/api/main.py`

**What**
- Introduce lightweight admin-role gate for Screen-3 endpoints using request role context/header pattern used in POC runtime.
- Allow `admin` and `dpo`; reject other roles with explicit forbidden response.

**Why**
- Screen-3 contract is explicitly admin/DPO scoped and must demonstrate role-restricted behavior.

**How**
- Implement minimal, testable dependency/check function without introducing external auth providers in GAP-5.

### 3) Add frontend API service bindings for Screen-3 endpoints

**Files**
- Update: `POC/v2/frontend/src/services/api.ts`
- Create or update typed models under frontend types module for monitoring/audit/admin payloads.

**What**
- Add typed calls for:
  - monitoring snapshot
  - anomaly alerts
  - audit search with filter object
  - role matrix
  - mapping table
  - master data

**Why**
- Screen-3 UI needs stable service entrypoints and type-safe payload handling.

**How**
- Follow existing `apiV3` pattern and token-first conventions used by GAP-4 endpoints.

### 4) Build dedicated Screen-3 route and primary dashboard panels

**Files**
- Create: `POC/v2/frontend/src/app/access-monitoring/page.tsx`
- Create: `POC/v2/frontend/src/components/access-monitoring/AccessMonitoringScreen.tsx`
- Create: `POC/v2/frontend/src/components/access-monitoring/LiveMetricsBar.tsx`
- Create: `POC/v2/frontend/src/components/access-monitoring/AnomalyAlertsPanel.tsx`
- Create: `POC/v2/frontend/src/components/access-monitoring/AuditLogSearchPanel.tsx`
- Update: `POC/v2/frontend/src/app/page.tsx` (navigation link)

**What**
- Implement Screen-3 Panels A/B/C equivalent:
  - metrics KPI cards
  - anomaly table with acknowledge/resolve UI state
  - audit filter + result table + row detail drawer/panel

**Why**
- GAP-5 acceptance and v3 screen contract require a dedicated access-monitoring dashboard.

**How**
- Compose panel container with shared loading/error states.
- Keep interactions deterministic and demo-safe.

### 5) Implement hash verification UX and secondary tabs

**Files**
- Update: Screen-3 components created above
- Create:
  - `RoleManagementTab.tsx`
  - `MappingToolTab.tsx`
  - `MasterDataTab.tsx`

**What**
- Add row-level hash verification action for audit entries:
  - recompute SHA-256 from displayed entry data fields
  - compare with entry hash
  - show pass/fail state in UI
- Add Screen-3 secondary tabs:
  - role permission matrix
  - terminology mapping table
  - master data read-only panels

**Why**
- Hash verification and secondary tabs are explicit Screen-3 contract obligations.

**How**
- Use browser crypto API for hash computation and normalized serialization for deterministic checks.

### 6) Add and update tests for GAP-5 contract behavior

**Files**
- Update: `POC/v2/scripts/tests/test_api_contract_routes.py`
- Add: `POC/v2/scripts/tests/test_access_monitoring_contract.py`
- Add frontend test(s) for panel rendering/filter/hash verify where test framework support exists.

**What**
- Verify endpoint availability and payload keys for Screen-3 domains.
- Verify role gate behavior (`admin`/`dpo` allowed; non-admin roles rejected).
- Verify audit filtering behavior and hash-verification calculation consistency.

**Why**
- GAP-5 closure requires evidence-driven functional checklist validation.

**How**
- Reuse deterministic fixtures and existing test client patterns.

### 7) Update GAP-5 checkpoint artifacts and execution evidence

**Files**
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-5-screen3-access-monitoring/README.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-5-screen3-access-monitoring/_discovery.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-5-screen3-access-monitoring/_lastest_test_results.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-5-screen3-access-monitoring/_development_summary.md`
- Update rollups under `POC/v2/_project_management/POC-Gap-Closure/gaps/` if project convention requires aggregate updates.

**What**
- Capture architecture decisions, contract mapping, command outputs, and closure status.

**Why**
- Required for traceable, auditable gap closure and handoff.

## Verification Steps

1. Backend contract checks:
   - run targeted contract tests for Screen-3 routes and role checks
2. Backend regression checks:
   - run full `scripts/tests` suite to ensure GAP-1..4 stability
3. Frontend checks:
   - build/type-check and screen rendering smoke for `/access-monitoring`
4. Functional checklist:
   - all 7 KPIs visible from snapshot
   - audit filter (e.g., `action_type=View`) reduces results
   - hash verification action returns expected match status
   - role matrix displays restricted access semantics
5. Manual inspection readiness:
   - backend/frontend launched with URLs documented for demo/UAT pass.

## Risks & Mitigations

- **Risk:** Sample/fixture data lacks full Screen-3 field depth.
  - **Mitigation:** add normalization/default layer and explicit fallback values.
- **Risk:** Role gate implementation conflicts with future SMART auth flow.
  - **Mitigation:** keep GAP-5 guard lightweight and encapsulated; reserve full auth integration for GAP-6.
- **Risk:** Hash verification mismatch due to inconsistent field serialization.
  - **Mitigation:** define canonical client serialization order for hash input.
- **Risk:** Existing `/audit` route overlap causes confusion.
  - **Mitigation:** prioritize dedicated `/access-monitoring` route and keep `/audit` backward-compatible.

## Out of Scope

- Full SMART-on-FHIR auth implementation and production RBAC enforcement depth (GAP-6).
- Broader terminology/FHIR evidence closure beyond Screen-3 tab exposure (GAP-7).
- End-to-end final verification pack consolidation (GAP-9).

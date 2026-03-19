# GAP-9 Implementation Plan — Verification Pack Closure

## Summary

Close GAP-9 by delivering a repeatable verification harness and evidence bundle that proves endpoint contracts, schema expectations, and 3-screen behaviors across GAP-1..8, with an explicit smoke/regression report.

## Current State Analysis

- GAP-9 is currently **Not started** in:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/README.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/_discovery.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/_lastest_test_results.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/_development_summary.md`
- Existing tests are substantial but not packaged as a single closure-oriented verification harness:
  - API/security/contract suites exist and are passing in targeted runs.
  - Frontend source-level reliability/terminology checks exist and pass.
  - Full frontend build evidence is blocked in current runtime because `npm/node` are unavailable.
  - Full regression includes one known external dependency failure (`test_end_to_end` with upstream 503 risk).

## GAP-9 Acceptance Targets

From WS-D and gap mapping:
- verification suite demonstrates required endpoint and screen contracts
- final evidence contains smoke + regression outcomes
- closure report clearly separates deterministic pass/fail from environment/external blockers

## Assumptions & Decisions

- GAP-9 depends on all prior gaps and acts as packaging/verification closure, not feature expansion.
- Verification should be deterministic by default; external-service-dependent tests are isolated and labeled.
- Evidence must be executable and reproducible from documented commands.
- GAP-9 can be set to **Complete** only when frontend build evidence is captured in an environment with Node/npm.

## Proposed Changes

### 1) Define verification-pack structure and command matrix

**Files**
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/_discovery.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/README.md`

**What**
- Define verification layers:
  - L1: contract/security backend checks (GAP-1/2/3/6/7)
  - L2: screen-contract checks (Screen 2/3 and frontend source-contract assertions)
  - L3: integration/regression run with explicit external dependency classification
  - L4: frontend production build confirmation
- Document canonical command order and pass/fail interpretation rules.

### 2) Implement a closure-focused verification runner

**Files**
- Add: `POC/v2/scripts/tests/test_gap9_verification_pack.py`
- Optionally add: `POC/v2/scripts/verify_gap9.py` (single orchestrated entrypoint)

**What**
- Add a pack-level test/runner that:
  - executes or references required deterministic checks
  - validates that mandatory suites are present and runnable
  - records preconditions (env load, port preflight, runtime tool availability)
- Keep runner local-only and avoid hardcoded external credentials.

### 3) Harden regression classification for external dependencies

**Files**
- Update: `POC/v2/scripts/tests/test_end_to_end.py` (if needed)
- Update: `POC/v2/scripts/tests/conftest.py` (if needed)

**What**
- Mark or gate external-LLM-dependent paths so GAP-9 closure can distinguish:
  - deterministic contract regressions (must fail closure)
  - external upstream outages (reported separately, non-contract blocker with mitigation)
- Preserve existing integration coverage while making closure signal reliable.

### 4) Execute verification pack and capture evidence

**Verification commands**
- Run targeted deterministic suites:
  - `scripts/tests/test_api_contract_routes.py`
  - `scripts/tests/test_security_rbac_contract.py`
  - `scripts/tests/test_timeline_contract_payload.py`
  - `scripts/tests/test_access_monitoring_contract.py`
  - `scripts/tests/test_frontend_terminology_visibility.py`
  - `scripts/tests/test_frontend_reliability_contract.py`
- Run broad regression:
  - `uv run pytest scripts/tests -v` with categorized reporting.
- Run frontend build gate:
  - `npm run build` in `POC/v2/frontend`.

**Evidence files**
- Update:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/_lastest_test_results.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/_lastest_test_results.md`

### 5) Finalize GAP-9 closure artifacts and rollups

**Files**
- Update:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/README.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/_development_summary.md`
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-9-verification-pack/_discovery.md`
  - rollups in `POC/v2/_project_management/POC-Gap-Closure/gaps/`

**What**
- Set final status to **Complete** only when:
  - deterministic contract/screen checks pass
  - smoke + regression report is captured
  - frontend build evidence is executed and recorded
- If runtime lacks Node/npm, keep status **In verification** and record explicit blocker.

## Verification Plan

1. Validate runtime/tool preconditions (uv/python and node/npm availability).
2. Execute deterministic verification matrix and capture outputs.
3. Execute regression run and classify external dependency failures separately.
4. Execute frontend build gate and record result.
5. Reconcile per-gap and rollup statuses with evidence-backed closure decision.

## Risks & Mitigations

- **Risk:** External-service-dependent tests create noisy failure signals.
  - **Mitigation:** explicit classification and non-contract segregation in results.
- **Risk:** Build verification cannot run in this runtime due missing Node/npm.
  - **Mitigation:** keep GAP-9 in verification and run build gate in Node-enabled environment before final closure.
- **Risk:** Cross-gap artifact inconsistency across per-gap and rollup files.
  - **Mitigation:** update GAP-9 files and shared rollups in same execution pass.

## Out of Scope

- New feature implementation beyond verification and evidence packaging.
- Production CI/CD pipeline redesign.
- Re-architecting orchestration logic unrelated to test harness closure.

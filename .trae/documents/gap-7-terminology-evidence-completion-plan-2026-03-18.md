# GAP-7 Completion Plan — Terminology Evidence Closure

## Why GAP-7 is still incomplete

- GAP-7 artifacts currently say **Complete**, but verification artifacts also state tests were not executed in this environment.
- Current GAP-7 tests do not strictly fail when terminology-bearing sections are empty.
- Claimed CPT coverage is not explicitly asserted in mapping-system tests.
- UI terminology rendering exists, but there is no explicit frontend verification evidence tied to GAP-7 closure.

## Completion objective

Close GAP-7 with strict, reproducible evidence that terminology fields are present and visible end-to-end (API + UI), and remove status contradictions in project artifacts.

## Planned work

### 1) Normalize GAP-7 evidence status before re-verification

**Files**
- `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-7-terminology-evidence/README.md`
- `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-7-terminology-evidence/_development_summary.md`
- rollups under `POC/v2/_project_management/POC-Gap-Closure/gaps/`

**Actions**
- Temporarily move GAP-7 status from “Complete” to “In verification” until executable evidence is captured.
- Align per-gap and rollup wording to avoid contradictory completion claims.

### 2) Strengthen backend contract assertions for terminology evidence

**Files**
- `POC/v2/scripts/tests/test_timeline_contract_payload.py`
- `POC/v2/scripts/tests/test_access_monitoring_contract.py`
- `POC/v2/scripts/tests/test_api_contract_routes.py`

**Actions**
- Enforce non-empty terminology-bearing sections for fixture-backed timeline responses (diagnosis/lab/procedure) where applicable.
- Require explicit system coverage assertions for `LOINC`, `SNOMED_CT`, `ICD10`, and `CPT` in mapping payload checks.
- Keep role/scope header requirements compatible with GAP-6 security model.

### 3) Add frontend verification evidence for terminology visibility

**Files**
- Add targeted frontend tests under existing test structure for:
  - `frontend/src/components/trend-timeline/ClinicalEventTimeline.tsx`
  - `frontend/src/components/access-monitoring/MappingToolTab.tsx`

**Actions**
- Add assertions that timeline rows render terminology labels (`ICD10`, `SNOMED`, `LOINC`, `CPT` where present).
- Add assertions that mapping table renders target system/code/label and mapping type.

### 4) Execute verification and capture raw outputs

**Commands to run**
- Backend targeted GAP-7 tests (timeline + mapping + contract routes).
- Frontend test/build commands that validate terminology rendering pathways.

**Evidence updates**
- Update:
  - `gaps/GAP-7-terminology-evidence/_lastest_test_results.md`
  - `gaps/_lastest_test_results.md`
- Include command, pass/fail summary, and relevant output snippets.

### 5) Finalize GAP-7 closure artifacts

**Files**
- `gaps/GAP-7-terminology-evidence/README.md`
- `gaps/GAP-7-terminology-evidence/_discovery.md`
- `gaps/GAP-7-terminology-evidence/_development_summary.md`
- rollups:
  - `gaps/_discovery.md`
  - `gaps/_development_summary.md`

**Actions**
- Set final status to **Complete** only after executable evidence is present.
- Record final closure rationale: terminology fields proven in API payloads and visible in UI views.

## Completion gate

GAP-7 is considered complete only when all are true:

- Backend tests with strict terminology assertions pass.
- Frontend terminology visibility verification passes.
- Per-gap and rollup artifacts contain real executed evidence and consistent “Complete” status.

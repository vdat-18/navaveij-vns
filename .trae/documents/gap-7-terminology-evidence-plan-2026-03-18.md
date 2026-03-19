# GAP-7 Implementation Plan — Terminology Evidence (LOINC/SNOMED/ICD)

## Summary

Close GAP-7 by making terminology evidence first-class and contract-aligned across backend APIs and frontend views, with explicit visibility of LOINC/SNOMED/ICD where the v3 contracts expect them.

This plan focuses on:
- timeline/event terminology propagation (API + UI)
- mapping-table contract alignment and richer terminology rows
- targeted verification proving end-to-end terminology field presence
- required GAP-7 checkpoint artifact updates

## Current State Analysis

- GAP-7 is currently marked **Not started**:
  - `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-7-terminology-evidence/README.md`
- Project plan expects GAP-7 exit evidence as:
  - “Mapping fields visible in UI/API” and terminology fields present end-to-end.
- Existing Screen-3 mapping path is implemented but only partially aligned:
  - backend: `POC/v2/backend/src/api/routes/contracts.py` (`/api/mapping-codes`)
  - fixture: `POC/v2/assets/monitoring.json` (`mapping_codes`)
  - frontend: `POC/v2/frontend/src/components/access-monitoring/MappingToolTab.tsx`
- Terminology propagation in timeline is incomplete:
  - timeline assembly currently emits blank `snomed_code`/`icd10_code`/`cpt_code` in several synthesized events
  - frontend timeline type and row rendering do not fully surface terminology fields expected by v3 docs.
- Existing tests validate route availability and basic payload shape, but not strong terminology evidence assertions.

## Assumptions & Decisions

- Keep `/api` routes as the primary integration surface; preserve existing `/api/admin/*` aliases.
- Prefer backward-compatible contract extension (additive fields) over breaking rename-only changes.
- Use canonical terminology system naming aligned to v3 specs (`LOINC`, `SNOMED_CT`, `ICD10`, etc.) while maintaining compatibility for current fields during transition.
- Scope GAP-7 to evidence exposure and contract propagation only; deeper auth-hardening remains GAP-6 scope.

## Proposed Changes

### 1) Align mapping-code contract payload with v3 terminology schema

**Files**
- Update: `POC/v2/backend/src/api/routes/contracts.py`
- Update: `POC/v2/assets/monitoring.json`
- Update: `POC/v2/frontend/src/types/access-monitoring.ts`

**What**
- Extend mapping records to include v3-aligned fields (additive compatibility):
  - `mapping_id`
  - `target_system`, `target_code`, `target_label`
  - `local_label`
  - `validated_by_user_id`, `validated_at`
  - `last_updated_by_user_id`, `last_updated_at`
  - `notes`
- Keep existing keys (`standard_system`, `standard_code`, `display`) during migration and map/normalize server-side to avoid frontend breakage.
- Add explicit SNOMED and ICD rows to fixture data (not just LOINC/CPT) to provide visible GAP-7 evidence.

**Why**
- Current mapping structure is weaker than v3 schema and does not provide sufficient standards evidence.

### 2) Ensure terminology fields are populated in timeline/event contract output

**Files**
- Update: `POC/v2/backend/src/mcp_server/utils.py` (timeline/event synthesis)
- Update: `POC/v2/backend/src/api/routes/contracts.py` (normalization if needed)

**What**
- Populate diagnosis/procedure/lab event terminology fields with consistent fallback behavior:
  - diagnosis: `icd10_code`, optional `snomed_code`
  - procedure/screening: `cpt_code` and/or `snomed_code` where relevant
  - labs: `loinc_code`
- Avoid empty-string-only placeholders where deterministic fixture/source values exist.
- Keep event output compatible with existing timeline consumers.

**Why**
- GAP-7 requires terminology to be carried end-to-end, not only listed in a separate mapping table.

### 3) Surface terminology evidence clearly in Screen-2/Screen-3 UI

**Files**
- Update: `POC/v2/frontend/src/types/timeline.ts`
- Update: `POC/v2/frontend/src/components/trend-timeline/ClinicalEventTimeline.tsx`
- Update: `POC/v2/frontend/src/components/access-monitoring/MappingToolTab.tsx`
- Update: `POC/v2/frontend/src/components/trend-timeline/BiomarkerTrendGrid.tsx` (if label consistency needed)

**What**
- Extend timeline types to include missing terminology fields already expected by contract docs.
- Render terminology badges/labels in event rows:
  - ICD-10 and SNOMED for diagnosis/procedure when present
  - LOINC for lab events
- Expand mapping table columns to show both source/local and target terminology plus mapping type/status.

**Why**
- GAP-7 success evidence must be visible in the actual UI, not hidden in payload only.

### 4) Add targeted GAP-7 verification tests

**Files**
- Update: `POC/v2/scripts/tests/test_timeline_contract_payload.py`
- Update: `POC/v2/scripts/tests/test_api_contract_routes.py`
- Update: `POC/v2/scripts/tests/test_access_monitoring_contract.py`
- Add: `POC/v2/scripts/tests/test_terminology_evidence_contract.py` (if clearer isolation is preferred)

**What**
- Add assertions that:
  - timeline payload includes expected terminology fields for relevant event types
  - mapping endpoint includes v3-aligned terminology keys
  - mapping dataset contains representative systems including LOINC/SNOMED/ICD
  - role-gated access to mapping endpoint still behaves correctly

**Why**
- Converts GAP-7 from visual/manual confidence to objective, repeatable evidence.

### 5) Update GAP-7 checkpoint artifacts and rollups

**Files**
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-7-terminology-evidence/README.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-7-terminology-evidence/_discovery.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-7-terminology-evidence/_lastest_test_results.md`
- Update: `POC/v2/_project_management/POC-Gap-Closure/gaps/GAP-7-terminology-evidence/_development_summary.md`
- Update rollups under `POC/v2/_project_management/POC-Gap-Closure/gaps/` as convention requires

**What**
- Record decisions, contract mappings, verification outputs, and final closure status for GAP-7.

## Verification Steps

1. Run targeted backend tests for timeline + mapping terminology assertions.
2. Run full backend regression suite (`scripts/tests`) to ensure no regressions from additive contract updates.
3. Run frontend build and verify `/trend-timeline` + `/access-monitoring` terminology display behavior.
4. Perform manual evidence pass:
   - confirm LOINC/SNOMED/ICD visibility in API responses
   - confirm terminology visibility in mapping table and timeline UI rows.

## Risks & Mitigations

- **Risk:** Introducing stricter mapping schema could break existing frontend consumers.
  - **Mitigation:** additive schema extension with compatibility normalization.
- **Risk:** Some event sources may not contain SNOMED/ICD in fixture data.
  - **Mitigation:** explicit fallback strategy and seeded representative fixture records for evidence.
- **Risk:** UI clutter from too many terminology columns.
  - **Mitigation:** concise badges/secondary lines and responsive column prioritization.
- **Risk:** Overlap with GAP-8 reliability work.
  - **Mitigation:** keep GAP-7 changes scoped to terminology fields and evidence rendering only.

## Out of Scope

- Full SMART-on-FHIR authentication hardening (GAP-6).
- Broad frontend reliability cleanup unrelated to terminology evidence (GAP-8).
- Final cross-gap closure pack orchestration (GAP-9).

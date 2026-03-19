# Event Timeline Contract
## Smart Health Checkup Recommendation Dashboard — MCP Tool API Specification

**Version:** 1.0
**Date:** 2026-03-14
**Audience:** MCP Server implementation team, Inference Orchestrator implementation team, Data Pipeline (FHIR Transform) implementation team, UI implementation team
**Depends on:** `fhir-discovery-report.md`, `signal-store-contract.md`
**Companion:** `sample_patient_checkup.json` (reference patient input)

---

## Overview

The Event Timeline tool is the **5th MCP tool** in the Signal Store. It is called at query time by the dashboard frontend (not by the Inference Orchestrator) to power the **Trend & Timeline screen** (Screen 2).

Unlike the three Signal Store tools consumed by the AI model, `get_patient_event_timeline` is a **display-oriented** tool — it returns structured clinical history events for rendering the timeline track alongside biomarker charts. The AI model does **not** receive this data; it is fetched after AI inference by the UI layer.

```
Data Pipeline (offline)
  FHIR Transform
      ↓
  Event Timeline Store DB  ←── this document defines the records written here
      ↑
MCP Server (query time)
  get_hard_constraints(patient_token)      ─┐
  get_clinical_signals(patient_token)       │  signal-store-contract.md
  get_biomarker_trends(patient_token)      ─┘  (AI inference inputs)
  get_program_ruleset(tier, gender, age)   ──   ruleset-store-contract.md
  get_patient_event_timeline(patient_token) ──  this document  (UI display only)
```

**Access pattern:** Read-only. No patient identifiers are exposed — `patient_token` = `HMAC-SHA256(fhir_patient_id, secret_salt)` is the only key.

**PDPA note:** This tool is subject to the same SMART on FHIR scope restriction and audit logging as all Signal Store tools. Every call is logged by the Audit Logger (Who / When / Where / What / Why).

---

## Tool — `get_patient_event_timeline(patient_token)`

### Purpose

Returns a structured set of historical clinical events across 5 arrays, spanning the patient's full available record history (up to the pipeline run date). The UI renders these as a horizontal chronological timeline track beneath the biomarker charts.

**FHIR sources:**

| Array | Primary FHIR Resource | Key Fields Used |
|-------|----------------------|-----------------|
| `diagnoses[]` | `Condition` | `onsetDateTime`, `code.coding` (ICD-10 + SNOMED CT), `clinicalStatus`, `verificationStatus` |
| `hospitalizations[]` | `Encounter` (class: inpatient) | `period.start`, `period.end`, `reasonCode`, `class` |
| `significant_lab_events[]` | `Observation` | `effectiveDateTime`, `code.coding` (LOINC), `valueQuantity`, `interpretation` |
| `screening_procedure_history[]` | `Procedure` | `performedDateTime`, `code.coding` (CPT / SNOMED), `status` |
| `medication_changes[]` | `MedicationStatement` + `MedicationRequest` | `effectiveDateTime`, `medication.coding` (RxNorm), `status`, `dosage` |

**Filtering rules applied by the Data Pipeline:**
- `significant_lab_events[]`: Only includes observations where `interpretation` is not Normal (H, L, HH, LL, A). Maximum 5-year lookback from pipeline run date.
- `hospitalizations[]`: Only `Encounter.class = IMP` (inpatient) or `EMER` (emergency). Outpatient visits excluded.
- `diagnoses[]`: Only `Condition.verificationStatus = confirmed`. Provisional diagnoses excluded.
- `screening_procedure_history[]`: Only `Procedure.status = completed`. Ordered-but-not-performed excluded.
- `medication_changes[]`: Deduplicates concurrent refills; one entry per drug per change event (start / stop / dose change).

---

### Example Response — Somchai W. (54yo male, `patient_token: tok_hmac_56291047`)

```json
{
  "patient_token": "tok_hmac_56291047",
  "timeline_span": {
    "earliest_event_date": "2019-06-12",
    "latest_event_date": "2026-03-11",
    "total_years_covered": 6.7
  },
  "diagnoses": [
    {
      "event_id": "dx-001",
      "date": "2022-03-08",
      "onset_year": 2022,
      "onset_type": "chronic",
      "icd10_code": "E78.5",
      "snomed_code": "13644009",
      "label": "Hyperlipidaemia / Dyslipidaemia",
      "clinical_status": "active",
      "fhir_condition_id": "Condition/cond-dyslipid-001"
    },
    {
      "event_id": "dx-002",
      "date": "2024-01-15",
      "onset_year": 2024,
      "onset_type": "chronic",
      "icd10_code": "R73.09",
      "snomed_code": "714628002",
      "label": "Prediabetes confirmed (IFG: FBS 100–125 mg/dL)",
      "clinical_status": "active",
      "fhir_condition_id": "Condition/cond-prediab-001"
    },
    {
      "event_id": "dx-003",
      "date": "2025-06-20",
      "onset_year": 2025,
      "onset_type": "chronic",
      "icd10_code": "I10",
      "snomed_code": "38341003",
      "label": "Essential (primary) hypertension",
      "clinical_status": "active",
      "fhir_condition_id": "Condition/cond-htn-001"
    },
    {
      "event_id": "dx-004",
      "date": "2026-01-10",
      "onset_year": 2026,
      "onset_type": "acute",
      "icd10_code": "M10.9",
      "snomed_code": "90560007",
      "label": "Hyperuricaemia / Gout (first episode)",
      "clinical_status": "active",
      "fhir_condition_id": "Condition/cond-gout-001"
    }
  ],
  "hospitalizations": [],
  "significant_lab_events": [
    {
      "event_id": "lab-001",
      "date": "2024-01-10",
      "lab_id": "obs-fbs-2024-01",
      "loinc_code": "1558-6",
      "label": "Fasting Blood Sugar (FBS)",
      "value": 105.0,
      "unit": "mg/dL",
      "interpretation": "H",
      "interpretation_label": "Above upper limit of normal",
      "threshold_crossed": "FBS ≥ 100 mg/dL (IFG threshold)",
      "normal_range": "70–99 mg/dL"
    },
    {
      "event_id": "lab-002",
      "date": "2024-01-10",
      "lab_id": "obs-hba1c-2024-01",
      "loinc_code": "4548-4",
      "label": "HbA1c",
      "value": 5.8,
      "unit": "%",
      "interpretation": "H",
      "interpretation_label": "Above upper limit of normal",
      "threshold_crossed": "HbA1c ≥ 5.7% (prediabetes threshold)",
      "normal_range": "< 5.7%"
    },
    {
      "event_id": "lab-003",
      "date": "2022-03-08",
      "lab_id": "obs-ldl-2022-03",
      "loinc_code": "2089-1",
      "label": "LDL Cholesterol",
      "value": 158.0,
      "unit": "mg/dL",
      "interpretation": "H",
      "interpretation_label": "Above upper limit of normal",
      "threshold_crossed": "LDL ≥ 130 mg/dL (borderline high)",
      "normal_range": "< 130 mg/dL"
    },
    {
      "event_id": "lab-004",
      "date": "2026-01-08",
      "lab_id": "obs-uric-2026-01",
      "loinc_code": "3084-1",
      "label": "Uric Acid",
      "value": 8.9,
      "unit": "mg/dL",
      "interpretation": "HH",
      "interpretation_label": "Critical high",
      "threshold_crossed": "Uric acid > 7.0 mg/dL (hyperuricaemia) + ≥ 8.0 mg/dL (gout risk high)",
      "normal_range": "3.5–7.0 mg/dL (male)"
    },
    {
      "event_id": "lab-005",
      "date": "2025-06-15",
      "lab_id": "obs-bp-2025-06",
      "loinc_code": "55284-4",
      "label": "Blood Pressure (Systolic / Diastolic)",
      "value": 142.0,
      "unit": "mmHg (systolic)",
      "interpretation": "H",
      "interpretation_label": "Stage 1 Hypertension",
      "threshold_crossed": "SBP ≥ 130 mmHg (ACC/AHA 2017 HTN Stage 1)",
      "normal_range": "< 120 / < 80 mmHg (Normal)"
    }
  ],
  "screening_procedure_history": [
    {
      "event_id": "proc-001",
      "date": "2019-06-12",
      "days_ago": 2465,
      "procedure_code": "colonoscopy",
      "cpt_code": "45378",
      "snomed_code": "73761001",
      "label": "Colonoscopy (colorectal cancer screening)",
      "status": "completed",
      "result_summary": "No polyps detected",
      "fhir_procedure_id": "Procedure/proc-colon-001"
    }
  ],
  "medication_changes": [
    {
      "event_id": "med-001",
      "date": "2022-03-10",
      "drug_name": "Atorvastatin",
      "rxnorm_code": "83367",
      "change_type": "started",
      "dose": "10 mg once daily",
      "indication": "Dyslipidaemia management",
      "fhir_resource_id": "MedicationStatement/med-atorv-001"
    },
    {
      "event_id": "med-002",
      "date": "2025-06-22",
      "drug_name": "Amlodipine",
      "rxnorm_code": "17767",
      "change_type": "started",
      "dose": "5 mg once daily",
      "indication": "Essential hypertension",
      "fhir_resource_id": "MedicationStatement/med-amlo-001"
    }
  ],
  "pipeline_run_id": "pipe_20260312_0300",
  "computed_at": "2026-03-12T03:00:00Z"
}
```

---

### JSON Schema

```jsonschema
{
  "$schema": "https://json-schema.org/draft/2020-12",
  "$id": "signal-store/get_patient_event_timeline/response",
  "type": "object",
  "required": ["patient_token", "timeline_span", "diagnoses", "hospitalizations", "significant_lab_events", "screening_procedure_history", "medication_changes", "computed_at"],
  "properties": {

    "patient_token": {
      "type": "string",
      "description": "HMAC-SHA256 pseudonymous patient identifier. Never contains MRN or real FHIR Patient ID."
    },

    "timeline_span": {
      "type": "object",
      "required": ["earliest_event_date", "latest_event_date", "total_years_covered"],
      "properties": {
        "earliest_event_date": { "type": "string", "format": "date", "description": "ISO 8601 date of the oldest event in any of the 5 arrays." },
        "latest_event_date":   { "type": "string", "format": "date", "description": "ISO 8601 date of the most recent event (≤ pipeline run date)." },
        "total_years_covered": { "type": "number", "description": "Decimal years from earliest_event_date to pipeline run date." }
      }
    },

    "diagnoses": {
      "type": "array",
      "description": "Confirmed chronic and acute diagnoses from FHIR Condition resources. verificationStatus=confirmed only.",
      "items": {
        "type": "object",
        "required": ["event_id", "date", "onset_year", "onset_type", "icd10_code", "label", "clinical_status"],
        "properties": {
          "event_id":        { "type": "string", "description": "Stable local identifier for this event (used for deduplication)." },
          "date":            { "type": "string", "format": "date", "description": "Condition.onsetDateTime (date portion)." },
          "onset_year":      { "type": "integer", "description": "Year portion of onset date. Used by UI for decade-level timeline rendering." },
          "onset_type":      { "type": "string", "enum": ["acute", "chronic"], "description": "Derived from condition duration and ICD category." },
          "icd10_code":      { "type": "string", "description": "ICD-10-CM/TH code." },
          "snomed_code":     { "type": "string", "description": "SNOMED CT concept ID. Optional — present when HIS provides it." },
          "label":           { "type": "string", "description": "Human-readable diagnosis label for display on timeline." },
          "clinical_status": { "type": "string", "enum": ["active", "recurrence", "remission", "resolved"], "description": "Condition.clinicalStatus.coding.code" },
          "fhir_condition_id": { "type": "string", "description": "Source FHIR Condition resource reference. For traceability only — not displayed." }
        }
      }
    },

    "hospitalizations": {
      "type": "array",
      "description": "Inpatient and emergency encounters from FHIR Encounter. Empty array if no inpatient history.",
      "items": {
        "type": "object",
        "required": ["event_id", "date_admit", "reason_label", "encounter_class"],
        "properties": {
          "event_id":            { "type": "string" },
          "date_admit":          { "type": "string", "format": "date", "description": "Encounter.period.start" },
          "date_discharge":      { "type": "string", "format": "date", "description": "Encounter.period.end. Null if discharge date not recorded." },
          "length_of_stay_days": { "type": "integer", "description": "Computed: date_discharge - date_admit. Null if date_discharge is null." },
          "reason_label":        { "type": "string", "description": "Encounter.reasonCode display text or diagnosis label." },
          "encounter_class":     { "type": "string", "enum": ["IMP", "EMER"], "description": "HL7 v3 ActCode: IMP=Inpatient, EMER=Emergency." },
          "fhir_encounter_id":   { "type": "string" }
        }
      }
    },

    "significant_lab_events": {
      "type": "array",
      "description": "Abnormal lab results only (interpretation ≠ N). Maximum 5-year lookback from pipeline run date. Source: FHIR Observation.",
      "items": {
        "type": "object",
        "required": ["event_id", "date", "loinc_code", "label", "value", "unit", "interpretation", "threshold_crossed"],
        "properties": {
          "event_id":             { "type": "string" },
          "date":                 { "type": "string", "format": "date", "description": "Observation.effectiveDateTime (date portion)." },
          "lab_id":               { "type": "string", "description": "Observation resource ID. For traceability." },
          "loinc_code":           { "type": "string", "description": "LOINC code for the test. Aligned with fhir-discovery-report.md LOINC table." },
          "label":                { "type": "string", "description": "Human-readable test name." },
          "value":                { "type": "number", "description": "Observation.valueQuantity.value" },
          "unit":                 { "type": "string", "description": "Observation.valueQuantity.unit" },
          "interpretation":       { "type": "string", "enum": ["H", "L", "HH", "LL", "A"], "description": "HL7 interpretation code. H=High, L=Low, HH=Critical High, LL=Critical Low, A=Abnormal (non-numeric)." },
          "interpretation_label": { "type": "string", "description": "Human-readable interpretation for UI display." },
          "threshold_crossed":    { "type": "string", "description": "Which clinical threshold was exceeded, with value. For display on timeline tooltip." },
          "normal_range":         { "type": "string", "description": "Reference range string from Observation.referenceRange." }
        }
      }
    },

    "screening_procedure_history": {
      "type": "array",
      "description": "Completed cancer screening and preventive procedures from FHIR Procedure. Status=completed only. Used to show when screenings were last performed.",
      "items": {
        "type": "object",
        "required": ["event_id", "date", "days_ago", "procedure_code", "label", "status"],
        "properties": {
          "event_id":         { "type": "string" },
          "date":             { "type": "string", "format": "date", "description": "Procedure.performedDateTime (date portion)." },
          "days_ago":         { "type": "integer", "description": "Computed: pipeline_run_date - procedure date. Aligns with overdue_days in get_clinical_signals() screening_gaps." },
          "procedure_code":   { "type": "string", "description": "Internal procedure code. Matches test_code in eligibility_exclusions and Ruleset Store add-on item_code." },
          "cpt_code":         { "type": "string", "description": "CPT-4 code. Optional — present when HIS provides it." },
          "snomed_code":      { "type": "string", "description": "SNOMED CT code for the procedure. Optional." },
          "label":            { "type": "string", "description": "Human-readable procedure name for timeline display." },
          "status":           { "type": "string", "const": "completed", "description": "Always 'completed' — incomplete procedures are excluded by the pipeline." },
          "result_summary":   { "type": "string", "description": "Brief free-text summary of procedure result (if available in FHIR). May be null." },
          "fhir_procedure_id":{ "type": "string" }
        }
      }
    },

    "medication_changes": {
      "type": "array",
      "description": "Medication start / stop / dose-change events from FHIR MedicationStatement and MedicationRequest. One entry per distinct change event per drug.",
      "items": {
        "type": "object",
        "required": ["event_id", "date", "drug_name", "change_type"],
        "properties": {
          "event_id":         { "type": "string" },
          "date":             { "type": "string", "format": "date", "description": "Effective date of the change. MedicationStatement.effectiveDateTime or MedicationRequest.authoredOn." },
          "drug_name":        { "type": "string", "description": "Generic drug name." },
          "rxnorm_code":      { "type": "string", "description": "RxNorm concept code. Optional — present when HIS provides it." },
          "change_type":      { "type": "string", "enum": ["started", "stopped", "dose_change"], "description": "Nature of the medication change event." },
          "dose":             { "type": "string", "description": "Dose and frequency string at time of change. E.g. '10 mg once daily'." },
          "indication":       { "type": "string", "description": "Clinical indication for the medication. Derived from associated Condition or free-text reason." },
          "fhir_resource_id": { "type": "string" }
        }
      }
    },

    "pipeline_run_id": {
      "type": "string",
      "description": "Batch pipeline run that populated this record. For lineage and debugging."
    },

    "computed_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp when this record was written by the Data Pipeline."
    }
  }
}
```

---

### Field Dictionary

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `patient_token` | string | System | HMAC-SHA256 pseudonymous key. Same token used across all 5 MCP tools. |
| `timeline_span.earliest_event_date` | date | Computed | Min date across all 5 arrays. |
| `timeline_span.total_years_covered` | number | Computed | Decimal. Used by UI to set x-axis range. |
| `diagnoses[].event_id` | string | System | Stable ID for deduplication across pipeline runs. Format: `dx-{NNN}`. |
| `diagnoses[].onset_type` | enum | Derived | Derived from ICD-10 category and condition duration. Acute = single episode; chronic = persistent/recurrent. |
| `diagnoses[].icd10_code` | string | FHIR `Condition.code` | ICD-10-CM (or ICD-10-TH for Thai-coded HIS systems). |
| `diagnoses[].snomed_code` | string | FHIR `Condition.code` | Optional. Populated only when HIS provides SNOMED mapping. |
| `diagnoses[].clinical_status` | enum | FHIR `Condition.clinicalStatus` | `active` is the most common value for chronic disease monitoring. |
| `hospitalizations[].encounter_class` | enum | FHIR `Encounter.class` | HL7 ActCode: `IMP` = inpatient, `EMER` = emergency/ED. |
| `hospitalizations[].length_of_stay_days` | integer | Computed | `null` when discharge date is unavailable. |
| `significant_lab_events[].interpretation` | enum | FHIR `Observation.interpretation` | Only H/L/HH/LL/A values are included. Normal (N) results are excluded by pipeline filter. |
| `significant_lab_events[].threshold_crossed` | string | Derived | Computed by Clinical Signal Engine using `clinical-guidelines-reference.md` thresholds. |
| `screening_procedure_history[].days_ago` | integer | Computed | `pipeline_run_date - procedure.date`. Intended to align with `overdue_days` in `get_clinical_signals().screening_gaps[]` — the UI can cross-reference these. |
| `screening_procedure_history[].procedure_code` | string | Internal | Matches `item_code` in `sample_add_on_items.json` and `test_code` in `eligibility_exclusions`. Consistent across all contracts. |
| `medication_changes[].change_type` | enum | Derived | `started` = new prescription; `stopped` = discontinued; `dose_change` = same drug, different dose/frequency. |
| `medication_changes[].indication` | string | Derived | From linked Condition or MedicationRequest.reasonCode. May be null if not coded in HIS. |
| `computed_at` | datetime | System | UTC. Same `pipeline_run_id` appears in all Signal Store records for the same batch run. |

---

## DB Record — Event Timeline Store

The Data Pipeline writes one record per patient per pipeline run. The Event Timeline Store is a separate logical table from the Signal Store DB — same physical infrastructure, different schema.

```
EventTimelineStore
  PK:   patient_token  (string)   ← HMAC-SHA256 pseudonymous key
  SK:   pipeline_run_id (string)  ← composite key allows history of runs

  diagnoses                JSON array
  hospitalizations         JSON array
  significant_lab_events   JSON array
  screening_procedure_history JSON array
  medication_changes       JSON array
  timeline_span            JSON object
  computed_at              ISO 8601 datetime
```

**Update frequency:** Populated on each scheduled pipeline run (nightly or triggered by new FHIR data). The most recent `pipeline_run_id` record is always served at query time.

---

## UI Consumption Notes (Screen 2)

The dashboard **Screen 2: Trend & Timeline** uses this tool alongside `get_biomarker_trends` from the Signal Store:

| Chart element | Data source |
|--------------|-------------|
| Biomarker line charts (FBS, HbA1c, LDL, BP, BMI, eGFR) | `get_biomarker_trends` — history arrays |
| Timeline track — diagnosis markers (blue) | `diagnoses[]` |
| Timeline track — hospitalization markers (red) | `hospitalizations[]` |
| Timeline track — abnormal lab markers (orange) | `significant_lab_events[]` |
| Timeline track — screening markers (green) | `screening_procedure_history[]` |
| Timeline track — medication change markers (grey) | `medication_changes[]` |
| Screening gap status bar (overdue items) | `get_clinical_signals` — `screening_gaps[]` |
| Vaccination status row | `get_clinical_signals` — `vaccination_gaps[]` |

The `days_ago` field in `screening_procedure_history[]` is intentionally aligned with `overdue_days` in `get_clinical_signals().screening_gaps[]`, allowing the UI to link a timeline marker to its corresponding overdue alert badge.

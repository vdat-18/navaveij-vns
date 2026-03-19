# Screen 2 — Trend & Timeline
## Navavej Health Intelligence Dashboard — POC UI Specification

**Version:** 1.0
**Date:** 2026-03-14
**Audience:** Physician, Nurse (longitudinal health history view)
**Reference patient:** Somchai W., 54yo male (`patient_token: tok_hmac_56291047`)
**Data source contracts:** `signal-store-contract.md` (biomarker trends), `event-timeline-contract.md` (clinical events)

**POC evaluation criteria addressed:**
- **20%** — Trend & timeline display: 6 multi-year biomarker charts + chronological event track (panels C + D)
- **25%** — FHIR data sourcing: LOINC codes shown on every chart title (panel C); event labels use ICD-10 codes (panel D)

---

## User Journey

After reviewing the AI recommendation on Screen 1, the physician switches to this screen to understand the patient's longitudinal health trajectory before discussing with the patient. Key questions answered:
1. Is each key biomarker trending toward or away from the normal range? (panel C — 6 charts)
2. When did significant clinical events occur, and how do they correlate with biomarker changes? (panel D — timeline track)
3. Which screenings are most overdue, and when were they last performed? (panel E — screening gap bar)

---

## Biomarker Data (Somchai W.)

The following values are drawn verbatim from `get_biomarker_trends` history arrays:

| Biomarker | LOINC | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Unit | Ref | Trend |
|-----------|-------|------|------|------|------|------|------|------|-----|-------|
| FBS | 1558-6 | 96 | — | 102 | 105 | — | 108 | mg/dL | <100 | ↑ WORSENING |
| HbA1c | 4548-4 | 5.4 | — | 5.7 | 5.8 | — | 6.1 | % | <5.7 | ↑ WORSENING |
| LDL | 2089-1 | — | 158 | 145 | 138 | — | 132 | mg/dL | <130 | ↓ IMPROVING |
| BMI | 39156-5 | — | — | 24.9 | 25.8 | — | 26.7 | kg/m² | <23 | ↑ WORSENING |
| BP Systolic | 55284-4 | — | 124 | — | 131 | 142 | — | mmHg | <120 | ↑ WORSENING |
| eGFR | 62238-1 | — | 88 | — | 85 | — | 82 | mL/min | ≥60 | ↓ SLOW DECLINE |

## Clinical Event Timeline Data (Somchai W.)

The following events are drawn verbatim from `get_patient_event_timeline` arrays:

| Date | Type | Event | Contract array | Key field |
|------|------|-------|---------------|-----------|
| 2019-06-12 | 🟢 Screening | Colonoscopy — no polyps detected | `screening_procedure_history[]` | `date`, `label`, `result_summary` |
| 2022-03-08 | 🔵 Diagnosis | Hyperlipidaemia / Dyslipidaemia (E78.5) | `diagnoses[]` | `date`, `label`, `icd10_code` |
| 2022-03-08 | 🟠 Abnormal Lab | LDL 158 mg/dL — borderline high (H) | `significant_lab_events[]` | `date`, `value`, `threshold_crossed` |
| 2022-03-10 | ⚫ Medication | Atorvastatin 10mg — started | `medication_changes[]` | `date`, `drug_name`, `change_type` |
| 2024-01-10 | 🟠 Abnormal Lab | FBS 105 mg/dL — IFG threshold (H) | `significant_lab_events[]` | `date`, `value`, `threshold_crossed` |
| 2024-01-10 | 🟠 Abnormal Lab | HbA1c 5.8% — prediabetes threshold (H) | `significant_lab_events[]` | `date`, `value`, `threshold_crossed` |
| 2024-01-15 | 🔵 Diagnosis | Prediabetes confirmed (R73.09) | `diagnoses[]` | `date`, `label`, `icd10_code` |
| 2025-06-15 | 🟠 Abnormal Lab | BP Systolic 142 mmHg — HTN Stage 1 (H) | `significant_lab_events[]` | `date`, `value`, `threshold_crossed` |
| 2025-06-20 | 🔵 Diagnosis | Essential hypertension (I10) | `diagnoses[]` | `date`, `label`, `icd10_code` |
| 2025-06-22 | ⚫ Medication | Amlodipine 5mg — started | `medication_changes[]` | `date`, `drug_name`, `change_type` |
| 2026-01-08 | 🟠 Abnormal Lab | Uric Acid 8.9 mg/dL — critical high (HH) | `significant_lab_events[]` | `date`, `value`, `interpretation` |
| 2026-01-10 | 🔵 Diagnosis | Hyperuricaemia / Gout (M10.9) | `diagnoses[]` | `date`, `label`, `icd10_code` |

---

## Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  [A] NAVIGATION BAR                                                         ║
║  🏥 Navavej Health Intelligence    Somchai W. ▾    Screen: Trend & Timeline ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [B] PATIENT HEADER STRIP                                                   ║
║  Somchai W.    54 yo  ♂    tok_hmac_562****47    Pipeline: 2026-03-12       ║
║  [ ← Back to Summary ]    [ View Recommendation → ]    [ Print ]            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [C] BIOMARKER TREND CHARTS                                  Time range: ▾  ║
║                                                              2019 – 2026     ║
║  ┌──────────────────────────────┐  ┌──────────────────────────────┐        ║
║  │  FBS  (LOINC 1558-6)         │  │  HbA1c  (LOINC 4548-4)       │        ║
║  │  mg/dL              ↑WORSENING│  │  %                  ↑WORSENING│        ║
║  │ 120 ┤                     ●  │  │ 6.5 ┤                     ●  │        ║
║  │ 108 ┤                  ●     │  │ 6.1 ┤                  ●     │        ║
║  │ 100 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│  │ 5.7 ┤ ─ ─ ─ ─ ─ ─ ● ─ ● ─ │        ║
║  │  96 ┤ ●    ●      ●          │  │ 5.4 ┤ ●              ●      │        ║
║  │     └─ 21 ─ 23 ─ 24 ─ 26    │  │     └─ 21 ─ 23 ─ 24 ─ 26   │        ║
║  │  Now: 108    Ref: < 100 ──── │  │  Now: 6.1%   Ref: < 5.7% ── │        ║
║  │  Slope: +6.0 mg/dL/yr        │  │  Slope: +0.23 %/yr          │        ║
║  └──────────────────────────────┘  └──────────────────────────────┘        ║
║                                                                              ║
║  ┌──────────────────────────────┐  ┌──────────────────────────────┐        ║
║  │  LDL  (LOINC 2089-1)         │  │  BMI  (LOINC 39156-5)        │        ║
║  │  mg/dL              ↓IMPROVING│  │  kg/m²              ↑WORSENING│        ║
║  │ 160 ┤ ●                      │  │  27 ┤                     ●  │        ║
║  │ 145 ┤      ●                 │  │  26 ┤                  ●     │        ║
║  │ 138 ┤          ●             │  │  25 ┤             ●          │        ║
║  │ 130 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ● ─ ─│  │  23 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│        ║
║  │     └─ 22 ─ 23 ─ 24 ─ 26    │  │     └─ 23 ─ 24 ─ 26         │        ║
║  │  Now: 132    Ref: < 130 ──── │  │  Now: 26.7   Ref: < 23 ───── │        ║
║  │  Slope: −8.7 mg/dL/yr ✓ stat │  │  Slope: +0.9 kg/m²/yr       │        ║
║  └──────────────────────────────┘  └──────────────────────────────┘        ║
║                                                                              ║
║  ┌──────────────────────────────┐  ┌──────────────────────────────┐        ║
║  │  BP Systolic  (LOINC 55284-4)│  │  eGFR  (LOINC 62238-1)       │        ║
║  │  mmHg               ↑WORSENING│  │  mL/min/1.73m²     ↓SLOW DEC │        ║
║  │ 145 ┤                  ●     │  │  90 ┤ ●                      │        ║
║  │ 131 ┤           ●            │  │  85 ┤          ●             │        ║
║  │ 124 ┤ ●                      │  │  82 ┤                   ●    │        ║
║  │ 120 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│  │  60 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│        ║
║  │     └─ 22 ─ 24 ─ 25          │  │     └─ 22 ─ 24 ─ 26         │        ║
║  │  Now: 142    [Stage 1 HTN]   │  │  Now: 82  CKD G2  Ref: ≥ 60 │        ║
║  │  Slope: +9.0 mmHg/yr         │  │  Slope: −2.0 mL/min/yr       │        ║
║  └──────────────────────────────┘  └──────────────────────────────┘        ║
║                                                                              ║
║  Dotted line (─ ─) = reference range upper/lower limit                      ║
║  ● = data point from FHIR Observation (hover for date, value, LOINC, unit)  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [D] CLINICAL EVENT TIMELINE                                                ║
║                                                                              ║
║  LEGEND:  🔵 Diagnosis   🟠 Abnormal Lab   🟢 Screening   ⚫ Medication     ║
║                                                                              ║
║  2019           2020    2021    2022         2023    2024         2025  2026 ║
║  ├──────────────┼───────┼───────┼────────────┼───────┼────────────┼────┤   ║
║  │              │       │      🔵🟠⚫        │      🟠🟠🔵       🟠🔵⚫ 🟠🔵 ║
║  🟢             │       │       │             │       │            │         ║
║  Colonoscopy    │       │      Dyslipidaemia  │      FBS↑         HTN  UA↑  ║
║  2019-06-12     │       │      E78.5          │      HbA1c↑       I10  M10.9║
║  (last done)    │       │      LDL 158 (H)    │      Prediabetes  Amlo-     ║
║                 │       │      Atorvastatin   │      R73.09       dipine    ║
║                 │       │      10mg started   │                   started   ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────     ║
║  Hover any marker for event detail:                                         ║
║  ┌─────────────────────────────────────────────────────────┐               ║
║  │  🟠  LDL Cholesterol  (LOINC 2089-1)                    │ [tooltip]     ║
║  │  Date: 2022-03-08  │  Value: 158 mg/dL                  │               ║
║  │  Interpretation: H (Above upper limit)                   │               ║
║  │  Threshold crossed: LDL ≥ 130 mg/dL (borderline high)   │               ║
║  │  Normal range: < 130 mg/dL                              │               ║
║  └─────────────────────────────────────────────────────────┘               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [E] SCREENING GAP STATUS                                                   ║
║                                                                              ║
║  Overdue screenings  (from get_clinical_signals → screening_gaps[])         ║
║                                                                              ║
║  Priority    Screening                Days Overdue   Last Performed         ║
║  ─────────   ──────────────────────   ────────────   ────────────────────   ║
║  🔴  Red     Colonoscopy              2,557 days     Jun 2019 (from event   ║
║              (5-yr: FDR colon ca)                    timeline → 2019-06-12) ║
║                                                                              ║
║  🔴  Red     LDCT Lung                Never          Never performed         ║
║              (annual: USPSTF 2021)                                          ║
║                                                                              ║
║  🟠  Orange  Influenza Vaccine         428 days      Oct 2024               ║
║              (annual: CDC ACIP 2024)                                        ║
║                                                                              ║
║  🟠  Orange  Shingrix Dose 1           Never          Never performed        ║
║              (≥50: CDC ACIP 2017)     (eligible since age 50 = 2021)        ║
║                                                                              ║
║  [ View all add-on recommendations on Summary screen → ]                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Field-to-Contract Mapping

### Panel C — Biomarker Trend Charts

| Chart | UI Element | Value (Somchai W.) | Source Contract | Source Field |
|-------|-----------|-------------------|----------------|--------------|
| FBS | Chart title + LOINC | FBS (LOINC 1558-6) | signal-store-contract | `get_biomarker_trends → metabolic.fbs.loinc_code` |
| FBS | Data points (●) | 96 (2021), 102 (2023), 105 (2024), 108 (2026) | signal-store-contract | `get_biomarker_trends → metabolic.fbs.history[].{date, value}` |
| FBS | Current value | 108 mg/dL | signal-store-contract | `get_biomarker_trends → metabolic.fbs.current_value` |
| FBS | Reference line | 100 mg/dL | signal-store-contract | `get_biomarker_trends → metabolic.fbs.reference_range_upper` |
| FBS | Trend label | ↑ WORSENING | signal-store-contract | `get_biomarker_trends → metabolic.fbs.trend_direction` = "worsening" |
| FBS | Slope | +6.0 mg/dL/yr | signal-store-contract | `get_biomarker_trends → metabolic.fbs.slope_per_year` |
| HbA1c | Data points | 5.4 (2021), 5.7 (2023), 5.8 (2024), 6.1 (2026) | signal-store-contract | `get_biomarker_trends → metabolic.hba1c.history[]` |
| HbA1c | Reference line | 5.7% | signal-store-contract | `get_biomarker_trends → metabolic.hba1c.reference_range_upper` |
| HbA1c | Trend | ↑ WORSENING | signal-store-contract | `get_biomarker_trends → metabolic.hba1c.trend_direction` |
| HbA1c | Slope | +0.23 %/yr | signal-store-contract | `get_biomarker_trends → metabolic.hba1c.slope_per_year` |
| LDL | Data points | 158 (2022), 145 (2023), 138 (2024), 132 (2026) | signal-store-contract | `get_biomarker_trends → lipids.ldl.history[]` |
| LDL | Reference line | 130 mg/dL | signal-store-contract | `get_biomarker_trends → lipids.ldl.reference_range_upper` |
| LDL | Trend | ↓ IMPROVING | signal-store-contract | `get_biomarker_trends → lipids.ldl.trend_direction` = "improving" |
| LDL | Slope note | −8.7 mg/dL/yr ✓ stat | signal-store-contract | `get_biomarker_trends → lipids.ldl.slope_per_year` (negative = improving on statin) |
| BMI | Data points | 24.9 (2023), 25.8 (2024), 26.7 (2026) | signal-store-contract | `get_biomarker_trends → anthropometric.bmi.history[]` |
| BMI | Reference line | 23 kg/m² | signal-store-contract | `get_biomarker_trends → anthropometric.bmi.reference_range_upper` (Asian-adjusted) |
| BMI | Trend | ↑ WORSENING | signal-store-contract | `get_biomarker_trends → anthropometric.bmi.trend_direction` |
| BP Systolic | Data points | 124 (2022), 131 (2024), 142 (2025) | signal-store-contract | `get_biomarker_trends → vitals.bp_systolic.history[]` |
| BP Systolic | Reference line | 120 mmHg | signal-store-contract | `get_biomarker_trends → vitals.bp_systolic.reference_range_upper` |
| BP Systolic | Classification label | Stage 1 HTN | signal-store-contract | derived: current_value 142 → ACC/AHA 2017 Stage 1 (130–139) |
| BP Systolic | Trend | ↑ WORSENING | signal-store-contract | `get_biomarker_trends → vitals.bp_systolic.trend_direction` |
| eGFR | Data points | 88 (2022), 85 (2024), 82 (2026) | signal-store-contract | `get_biomarker_trends → renal.egfr.history[]` |
| eGFR | Reference line | 60 mL/min | signal-store-contract | `get_biomarker_trends → renal.egfr.reference_range_lower` |
| eGFR | CKD stage label | CKD G2 | signal-store-contract | derived: eGFR 60–89 = CKD G2 |
| eGFR | Slope | −2.0 mL/min/yr | signal-store-contract | `get_biomarker_trends → renal.egfr.slope_per_year` |
| eGFR | Trend label | ↓ SLOW DECLINE | signal-store-contract | `get_biomarker_trends → renal.egfr.trend_direction` = "worsening" (slow) |

### Panel D — Clinical Event Timeline

| UI Element | Value (Somchai W.) | Source Contract | Source Field |
|-----------|-------------------|----------------|--------------|
| Timeline x-axis start | 2019 | event-timeline-contract | `timeline_span.earliest_event_date` (2019-06-12) |
| Timeline x-axis end | 2026 | event-timeline-contract | `timeline_span.latest_event_date` |
| 🟢 Colonoscopy marker (2019) | Colonoscopy 2019-06-12 | event-timeline-contract | `screening_procedure_history[0].date`, `.label` |
| Colonoscopy result | No polyps detected | event-timeline-contract | `screening_procedure_history[0].result_summary` |
| 🔵 Dyslipidaemia dx (2022) | Dyslipidaemia E78.5 | event-timeline-contract | `diagnoses[0].date`, `.label`, `.icd10_code` |
| 🟠 LDL 158 lab event (2022) | LDL 158 mg/dL — borderline high | event-timeline-contract | `significant_lab_events[0].date`, `.label`, `.value`, `.unit`, `.interpretation`, `.threshold_crossed` |
| ⚫ Atorvastatin started (2022) | Atorvastatin 10mg — started | event-timeline-contract | `medication_changes[0].date`, `.drug_name`, `.change_type`, `.dose` |
| 🟠 FBS 105 lab event (2024) | FBS 105 mg/dL — IFG threshold | event-timeline-contract | `significant_lab_events[2].date`, `.value`, `.threshold_crossed` |
| 🟠 HbA1c 5.8% lab event (2024) | HbA1c 5.8% — prediabetes threshold | event-timeline-contract | `significant_lab_events[1].date`, `.value`, `.threshold_crossed` |
| 🔵 Prediabetes dx (2024) | Prediabetes R73.09 | event-timeline-contract | `diagnoses[1].date`, `.label`, `.icd10_code` |
| 🟠 BP 142 lab event (2025) | BP Systolic 142 mmHg — HTN Stage 1 | event-timeline-contract | `significant_lab_events[4].date`, `.value`, `.threshold_crossed` |
| 🔵 HTN dx (2025) | Essential hypertension I10 | event-timeline-contract | `diagnoses[2].date`, `.label`, `.icd10_code` |
| ⚫ Amlodipine started (2025) | Amlodipine 5mg — started | event-timeline-contract | `medication_changes[1].date`, `.drug_name`, `.change_type`, `.dose` |
| 🟠 UA 8.9 lab event (2026) | Uric Acid 8.9 mg/dL — critical high | event-timeline-contract | `significant_lab_events[3].date`, `.value`, `.interpretation` (HH) |
| 🔵 Hyperuricaemia dx (2026) | Hyperuricaemia M10.9 | event-timeline-contract | `diagnoses[3].date`, `.label`, `.icd10_code` |
| Tooltip: all fields | Date, value, LOINC, interpretation, threshold | event-timeline-contract | per-array field set (see event-timeline-contract field dictionary) |

### Panel E — Screening Gap Status

| UI Element | Value | Source Contract | Source Field |
|-----------|-------|----------------|--------------|
| Colonoscopy priority badge | 🔴 Red | signal-store-contract | `get_clinical_signals → screening_gaps[colonoscopy].priority_color` |
| Colonoscopy overdue days | 2,557 days | signal-store-contract | `get_clinical_signals → screening_gaps[colonoscopy].overdue_days` |
| Colonoscopy last performed date | Jun 2019 (2019-06-12) | event-timeline-contract | `screening_procedure_history[0].date` — cross-referenced via `days_ago` field alignment |
| LDCT Lung priority badge | 🔴 Red | signal-store-contract | `get_clinical_signals → screening_gaps[ldct_lung].priority_color` |
| LDCT status | Never performed | signal-store-contract | `get_clinical_signals → screening_gaps[ldct_lung].overdue_days` = null / never |
| Influenza priority badge | 🟠 Orange | signal-store-contract | `get_clinical_signals → screening_gaps[influenza].priority_color` |
| Influenza overdue days | 428 days | signal-store-contract | `get_clinical_signals → screening_gaps[influenza].overdue_days` |
| Shingrix priority badge | 🟠 Orange | signal-store-contract | `get_clinical_signals → vaccination_gaps[shingrix].priority_color` |
| Shingrix status | Never — eligible since age 50 (2021) | signal-store-contract | `get_clinical_signals → vaccination_gaps[shingrix]` |

---

## Design Notes

### Chart Rendering

- **Data point dots (●):** Each ● maps to one `{date, value}` entry in the `history[]` array. The x-axis position is proportional to the actual date, not evenly spaced — so gaps between measurements are reflected accurately.
- **Reference band:** A horizontal dotted line (─ ─) at `reference_range_upper` (or `reference_range_lower` for eGFR). The region between the line and the chart origin is lightly shaded green to indicate the normal range zone.
- **WORSENING / IMPROVING / SLOW DECLINE:** Derived from `trend_direction` field and whether the trend is moving toward or away from the reference range. A WORSENING trend for eGFR means declining toward the lower limit (60), not an increase.
- **Slope annotation:** `slope_per_year` is displayed as a signed number with unit (e.g., "+6.0 mg/dL/yr"). For LDL with a statin, "✓ stat" annotation confirms the decline is medication-assisted — displayed when `medication_changes` contains an active statin start event.

### Timeline Interaction

- **Hovering a marker** shows a tooltip with all detail fields from the corresponding array entry (date, value/label, ICD-10/LOINC code, interpretation, threshold crossed).
- **Clicking a 🟢 screening marker** scrolls panel E to the corresponding screening gap row and highlights it.
- **Stacked markers** (multiple events on the same date — e.g., 2022-03-08 has Dyslipidaemia dx + LDL lab event + Atorvastatin start) are shown stacked vertically with a small offset. Clicking the cluster opens a list view of all events on that date.
- **Zoom:** The time range selector (panel C top-right, default "2019 – 2026") allows narrowing to 1yr, 3yr, 5yr, or a custom date range. All 6 charts and the timeline track respond to the same zoom setting.

### Cross-reference: `days_ago` alignment

The `days_ago` field in `screening_procedure_history[]` is computed at pipeline time as `pipeline_run_date − procedure.date`. This is intentionally aligned with `overdue_days` in `get_clinical_signals().screening_gaps[]`, so that panel E can display both:
- the computed gap duration (from signal-store-contract)
- the actual last-performed date (from event-timeline-contract, via the matching procedure record)

### POC Scope Notes

- Charts in the POC wireframe use ASCII art to represent the line charts. The actual implementation would use a JavaScript charting library (e.g., Recharts, Chart.js) consuming the same `history[]` data arrays.
- The "Print" button generates a PDF containing all 6 charts and the timeline. This action is logged as `action_type: Export` in the Audit Logger.

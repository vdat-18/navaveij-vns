# Rule Synthesis Framework
## Ruleset Store — Clinical-to-Rule Derivation Methodology

**Version:** 1.0
**Date:** 2026-03-13
**Audience:** Clinical team, Admin Panel team, QA team
**Governs:** How to derive valid `ruleset_tier_config` and `add_on_item` DB records from clinical guidelines
**Does NOT govern:** Signal computation (`clinical-guidelines-reference.md`), FHIR mapping (`fhir-discovery-report.md`), MCP API shape (`ruleset-store-contract.md`)

---

## 1. Purpose & Scope

This framework establishes the methodology for translating clinical guidelines into structured Ruleset Store records. It serves three functions:

1. **Derivation** — step-by-step process for creating new tier rules and add-on items
2. **Audit trail** — a ledger documenting the source of every rule and add-on in the current ruleset
3. **Validation gate** — a checklist to pass before any ruleset version is promoted to production

Every rule in the Ruleset Store must be traceable to a named clinical guideline. Every signal ID referenced in a rule must exist in the Signal Store Contract Field Dictionary. Admin Panel changes may only touch admin-configurable fields (marked in the Field Dictionary); all other changes require a code release and clinical review.

---

## 2. Source Chain (Full Traceability)

Every rule follows this four-document chain. A rule is invalid if any link is broken.

```
Step 1 — Clinical Guideline (published evidence base)
          e.g., USPSTF Colorectal Cancer Screening 2021; ADA Standards 2024
              ↓
Step 2 — clinical-guidelines-reference.md
          Defines: thresholds, pseudocode rules, signal IDs produced
          e.g., §4.3: colonoscopy_screening_gap, signal: overdue_days > 0
              ↓
Step 3 — signal-store-contract.md → Field Dictionary
          Confirms: signal_id exists in applicable_signals[] / signals_fired[] vocabulary
          e.g., "colonoscopy_screening_gap" → Category: Screening, Guideline: USPSTF 2021
              ↓
Step 4 — ruleset-store-contract.md → add_on_item / tier_selection_rules schema
          Specifies: how signal maps to rule condition or add-on trigger_signals[]
              ↓
Step 5 — sample JSON files (generated from this framework)
          sample_ruleset_tier_config.json, sample_add_on_items.json
```

**Hard rule:** Any `signal_id` string that does not appear in the signal-store-contract.md Field Dictionary is invalid and must not be used in a rule. New signals require a Clinical Signal Engine update first.

---

## 3. Tier Boundary Calibration

### 3.1 Tier Assignment Logic

Rules are evaluated top-down; the first match wins. There are two Premium rules (single severe signal; multi-signal count), one Advanced rule (any moderate signal or ≥ 2 low-moderate), and one Standard default.

| Tier | Clinical Rationale | Assignment Approach |
|---|---|---|
| **Premium** | Active multi-system disease or a single high-severity condition that warrants comprehensive personalized evaluation beyond standard enhanced screening | Single-signal: any one of a defined high-severity set; OR multi-signal count: ≥ N from a moderate pool |
| **Advanced** | Elevated risk in one or more systems with no active multi-system disease; requires enhanced screening beyond routine | Any single moderate-severity signal, OR ≥ 2 signals from a low-moderate pool |
| **Standard** | No active elevated risk signals; routine annual preventive health screening appropriate | Default — no Premium or Advanced rule matched |

### 3.2 Signal Pool Assignment

Signals are assigned to pools based on their clinical severity classification:

#### High-Severity Pool (Premium single-signal qualifiers)
These signals alone are sufficient to trigger Premium. Each represents either an active multi-organ disease, imminent serious outcome, or a guideline-endorsed indication for comprehensive evaluation.

| Signal ID | Clinical Basis | Source §(clinical-guidelines-reference.md) |
|---|---|---|
| `ckd_rapid_progression` | eGFR decline > 5 mL/min/1.73m²/yr → urgent nephrology evaluation | §7.2 |
| `ascvd_very_high` | ASCVD 10-yr risk ≥ 20% → high-intensity statin + comprehensive CV workup | §5.1 |
| `hypertensive_crisis` | SBP > 180 or DBP > 120 → emergency evaluation; EST and many procedures contraindicated | §2 |
| `diabetes_confirmed` + `dm_organ_complication_screening` | Confirmed DM with organ complication screening gap → multi-system follow-up (retina, kidney, foot, cardiac) | §1.2, §6.2 |
| `liver_enzyme_elevation_significant` + `fibroscan_indication` | ALT > 3× ULN with liver disease risk → comprehensive hepatic evaluation | §1.4, §8.1 |

#### Moderate Pool (Advanced single-signal qualifiers)
Any one of these alone triggers Advanced.

| Signal ID | Clinical Basis |
|---|---|
| `prediabetes_confirmed` | ADA 2024 — pre-diabetes confirmed (FBS 100–125 or HbA1c 5.7–6.4%) |
| `diabetes_confirmation_required` | ADA 2024 — FBS ≥ 126, pending confirmatory test |
| `ascvd_risk_intermediate` | ACC/AHA — ASCVD 10-yr risk 7.5–19.9% |
| `htn_active` | ACC/AHA 2017 — active hypertension comorbidity (Stage 1 or 2) |
| `lung_ct_threshold_met` | USPSTF 2021 — age 50–80, ≥ 20 pack-years, current/quit ≤ 15yr |
| `ckd_comorbidity` | KDIGO — CKD any stage confirmed |
| `bmi_obese_asian` | WHO Asia-Pacific — BMI ≥ 27.5 (Asian-adjusted obese) |
| `history_syncope` | History of loss of consciousness (syncope) — arrhythmia risk |

#### Low-Moderate Pool (Advanced count-threshold qualifiers)
Two or more of these signals co-occurring triggers Advanced.

| Signal ID | Clinical Basis |
|---|---|
| `bmi_overweight_asian` | WHO Asia-Pacific — BMI ≥ 23 (Asian overweight) |
| `low_hdl` | ACC/AHA 2018 — HDL < 40 (M) / < 50 (F) |
| `high_triglycerides` | ACC/AHA 2018 — TG ≥ 200 mg/dL |
| `high_ldl` | ACC/AHA 2018 — LDL ≥ 160 mg/dL |
| `bp_stage1_htn` | ACC/AHA 2017 — SBP 130–139 or DBP 80–89 (not yet confirmed comorbidity) |
| `bp_worsening` | ACC/AHA 2017 — increasing BP trend over readings |
| `fbs_upward_trend` | Fasting Blood Sugar upward trend (e.g. >5 mg/dL/yr) — metabolic risk |
| `family_hx_premature_cad` | ACC/AHA 2018 Risk Enhancers |
| `at_risk_alcohol_use` | NIAAA — AUDIT-C ≥ 3 (F) / ≥ 4 (M) |
| `office_syndrome` | WHO Workers' Health 2008 — prolonged sedentary work |
| `night_shift_worker` | WHO Workers' Health 2008 — rotating/permanent night shift |
| `uric_acid_hyperuricemia` | ACR 2020 — uric acid above sex-specific threshold |
| `dyslipidemia_active` | Active dyslipidemia comorbidity tag |
| `fibroscan_indication` | AASLD 2023 — liver disease risk (BMI + ALT or alcohol + ALT) |
| `diagnosis_fatty_liver` | Historical diagnosis of fatty liver (NAFLD/MASLD) |

#### Multi-Signal Premium Threshold
When a patient accumulates ≥ **N** signals from the moderate + low-moderate pools combined, the sheer volume of concurrent risk factors warrants Premium. The threshold **N** is admin-configurable (default: **5**).

**Rationale for N = 5:** At 5 concurrent independent risk signals, the patient's phenotype has exceeded what Advanced enhanced screening can adequately address; a comprehensive personalized Premium evaluation is needed. Below 5, a single Advanced package with targeted add-ons is clinically sufficient.

**Calibration note:** The clinical team MUST validate N through the Medical Acceptance Test (TOR §6.2 — 100 blind cases, 3/5 expert consensus) before production. The MAT result may raise or lower the default.

---

## 4. Priority Level Assignment Criteria

Every `add_on_item` has a `priority_level_default`. The AI may assign a higher level; the Safety Rule Validator may silently lower a level if the underlying signals don't support the AI's assignment.

| Priority | Color | Assignment Criteria | Clinical Rationale |
|---|---|---|---|
| **Red** | 🔴 | Overdue ≥ 2× the recommended interval; OR first-degree family history of a relevant cancer; OR signal severity classified "High" (e.g., `lung_ct_threshold_met` never done) | Immediate action needed; delay increases harm risk |
| **Orange** | 🟠 | Overdue ≤ 2× recommended interval; OR vaccination gap (low burden, high preventive value) | Timely action recommended within this visit |
| **Yellow** | 🟡 | Triggered by a moderate signal; within a reasonable window; shared decision-making appropriate; or a follow-up item | Worth discussing and scheduling; not urgent |
| **Green** | 🟢 | Preventive discussion item with no active clinical trigger; patient-reported concern; occupational or lifestyle screening | Optional enhancement; patient-initiated or low-urgency |

### Priority Override Signals
For items where a specific signal context raises urgency above the default:

| Add-On | Default | Override Signal | Override Priority |
|---|---|---|---|
| `colonoscopy` | Red | `family_hx_colon_ca_first_degree` or `symptom_hematochezia` | Red (confirm; no change but forced regardless of overdue days) |
| `upper_gi_endoscopy` | Red | `symptom_hematemesis` or `symptom_melena` | Red |
| `exercise_stress_test` | Yellow | `ascvd_very_high` or `ascvd_high` | Red |
| `fibroscan` | Yellow | `liver_enzyme_elevation_significant` | Red |
| `hepatitis_b_vaccine` | Red | `hepatitis_b_series_incomplete` | Yellow (series started, just incomplete) |
| `ldct_lung` | Red | — | Red (always Red when threshold met and never done) |

---

## 5. Add-On Item Derivation Template

Use this template to derive a new `add_on_item` DB record from a clinical guideline:

```
─────────────────────────────────────────────────────
SOURCE CHAIN
  Guideline:        [Org name, guideline title, year, section/page]
  clinical-guidelines-reference.md section: §[N.N]
  Signal ID produced: [signal_id from Field Dictionary]

ITEM RECORD FIELDS
  item_code:               [lowercase_snake derived from signal/test name]
  label:                   "[Plain English — Test Type — Purpose]"
  category:                [from enum: cancer_screening | cardiac | endocrine | gi_liver |
                            nephrology | imaging | musculoskeletal | neurology |
                            ophthalmology | vaccination | women_health | other]
  trigger_signals:         ["signal_id_1", "signal_id_2"]  ← ALL must be in Field Dictionary
  match_logic:             "ANY_OF_TRIGGER_SIGNALS" | "ALL_OF_TRIGGER_SIGNALS"
  priority_level_default:  "Red" | "Orange" | "Yellow" | "Green"  ← per §4 criteria
  priority_override_signals: { "signal_id": "priority_level" }  ← if applicable
  safety_contraindication_signals: ["signal_id"]  ← if a safety flag makes this test unsafe
  gender_constraint:       null | "male" | "female"  ← from guideline eligibility text
  age_min:                 [integer or null]  ← from guideline age eligibility
  age_max:                 [integer or null]  ← from guideline age eligibility
  navavej_product:
    product_name:          [from navavej-checkup-package-discovery.md §5]
    product_code:          [from discovery doc; "TBD" if unconfirmed — see Open Questions]
    price_thb:             [integer or null if unconfirmed]
  guideline:               "[Org] [Title] [Year]"
  admin_configurable_fields: ["price_thb", "age_min", "age_max", "priority_level_default"]
─────────────────────────────────────────────────────
```

**Validation before committing:**
- [ ] `signal_id` exists in signal-store-contract.md Field Dictionary (exact match, case-sensitive)
- [ ] `category` is one of the enum values in ruleset-store-contract.md JSON Schema
- [ ] `gender_constraint` matches the guideline eligibility text verbatim
- [ ] `age_min` and `age_max` match the guideline age range
- [ ] `navavej_product.product_code` is confirmed or explicitly flagged "TBD" with Open Question reference

---

## 6. Complete Add-On Derivation Ledger

Audit table for all add-on items. Each row traces from guideline → signal → item → Navavej product.

| # | item_code | clinical-guidelines-reference.md § | Trigger Signal(s) | Priority Default | Priority Rationale | gender_constraint | age_min | age_max | Navavej Product | Price (฿) | Open Question? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `colonoscopy` | §4.3 | `colonoscopy_screening_gap`, `symptom_hematochezia` | Red | First-degree FHx colon ca; overdue > 10yr interval; or red-flag symptom (blood in stool) | null | 45 | 85 | Colonoscopy (Lower GI) | TBD | #7 — confirm standalone colonoscopy |
| 2 | `upper_gi_endoscopy` | §4.3 | `symptom_dyspepsia`, `symptom_hematemesis`, `symptom_melena` | Red | Red flag symptoms (vomit blood, black stool) or persistent dyspepsia | null | 18 | null | Endoscopy Package (Upper GI) | 9,500 | — |
| 3 | `exercise_stress_test` | §5.2 | `est_gap`, `est_consideration`, `ascvd_risk_intermediate`, `ascvd_high` | Yellow | Moderate ASCVD risk — SDM appropriate; Red override if ascvd_very_high | null | 30 | null | Exercise Stress Test (EST) | 2,900 | — |
| 4 | `echocardiogram` | §5.2, §6.2 | `echo_gap`, `dm_comorbidity`, `htn_active` | Yellow | DM/HTN organ risk screening; within standard follow-up window | null | 35 | null | Echocardiogram (ECHO) | 2,900 | — |
| 5 | `ct_coronary_calcium` | §5.1 | `family_hx_premature_cad`, `ascvd_risk_intermediate`, `high_ldl` | Yellow | Risk enhancer — helps refine statin/further workup decision (ACC/AHA 2018) | null | 40 | null | CT Coronary Artery Calcium (CAC) | 3,900 | — |
| 6 | `cardiac_patch_48h` | — (symptom-driven) | `symptom_palpitations`, `history_syncope`, `family_hx_sudden_cardiac_death` | Yellow | Palpitations or syncope history — arrhythmia workup; scheduled evaluation | null | 18 | null | 48-hr Cardiac Patch (S-Patch EX) | 7,742 | — |
| 7 | `ldct_lung` | §4.4, §10.1 | `lung_ct_threshold_met`, `family_hx_lung_ca` | Red | Never-screened eligible smoker or family history = high severity | null | 50 | 80 | Low-Dose CT Chest (LDCT Lung) | 3,900 | — |
| 8 | `mammogram` | §4.1 | `mammogram_screening_gap` | Red (if overdue ≥ 48mo) / Orange (if overdue < 48mo) | Biennial interval; family hx forces Red regardless | female | 40 | 74 | Mammogram | 2,850 | — |
| 9 | `cervical_cancer_hpv_screen` | §4.2 | `pap_smear_screening_gap` | Orange | Overdue ≤ 5yr (co-test interval) = Orange; overdue > 10yr = Red | female | 21 | 65 | Cervical Cancer + HPV Screening | 2,300 | — |
| 10 | `dexa_bone_density` | §4.6 | `dexa_screening_gap` | Orange | Routine USPSTF grade B for female ≥ 65; insufficient evidence for males | female | 65 | null | Bone Density Scan DEXA (2 areas) | 1,450 | — |
| 11 | `psa_sdm` | §1.7, §4.5 | `psa_sdm_status`, `family_hx_prostate_ca` | Green | SDM only — no universal recommendation; low urgency discussion item | male | 50 | 69 | PSA Standalone Test | TBD | #10 — confirm standalone PSA code |
| 12 | `diabetes_screening_pro` | §1.1, §1.2, §6.1 | `prediabetes_confirmed`, `diabetes_confirmation_required`, `bmi_obese_asian`, `fbs_upward_trend` | Yellow | Pre-diabetes confirmed or suspected; or upward trend >5mg/dL/yr | null | 15 | null | Diabetes Screening Pro 1 | 2,134 | — |
| 13 | `thyroid_pro1` | §1.6 | `tsh_status`, `symptom_palpitations` | Yellow | Abnormal TSH or palpitation symptom; 6-item basic thyroid panel | null | 15 | null | Thyroid Pro 1 | 2,134 | — |
| 14 | `thyroid_pro2` | §1.6 | `tsh_borderline_high`, `hypothyroidism_likely`, `hyperthyroidism_possible` | Yellow | Confirmed abnormal TSH requires Free T3/T4 + antibodies (7-item) | null | 15 | null | Thyroid Pro 2 | 3,395 | — |
| 15 | `fibroscan` | §8.1 | `fibroscan_indication`, `liver_enzyme_elevation_significant`, `diagnosis_fatty_liver` | Yellow (Red if ALT > 3× ULN) | Liver disease risk or history of fatty liver | null | 18 | null | FibroTouch (Liver Fat Assessment) | 1,900 | — |
| 16 | `hepatitis_abc_screen` | §8.2, §9.2 | `hepatitis_b_vaccination_status`, `hepatitis_b_anti_hbs_check_needed` | Yellow | Hepatitis B immunity check or incomplete screening; 5-item panel | null | 18 | null | Hepatitis A, B, C Screening (5 items) | 1,900 | — |
| 17 | `kidney_screening` | §1.5, §7.1, §6.2 | `ckd_comorbidity`, `ckd_rapid_progression`, `dm_comorbidity`, `htn_active` | Yellow (Red if `ckd_rapid_progression`) | CKD monitoring or DM/HTN organ risk; ACR + eGFR panel | null | 18 | null | Kidney Disease Screening | 2,500 | — |
| 18 | `abdominal_ultrasound_full` | §8.1, §11.1 | `at_risk_alcohol_use`, `fibroscan_indication`, `liver_enzyme_mildly_elevated` | Yellow | At-risk alcohol use + liver risk; abdominal organ survey | null | 18 | null | Abdominal Ultrasound (Full) | 2,550 | — |
| 19 | `carotid_ultrasound` | §5.1 | `family_hx_premature_cad`, `ascvd_risk_intermediate`, `ascvd_high`, `bp_stage2_htn` | Yellow | ACC/AHA 2018 risk enhancer — subclinical atherosclerosis assessment | null | 50 | null | Carotid Artery Ultrasound | 5,096 | — |
| 20 | `retinal_exam` | §6.2 | `dm_organ_complication_screening`, `dm_comorbidity` | Yellow | ADA 2024 — annual diabetic retinopathy screening once DM confirmed | null | 18 | null | Retinal Examination | 2,590 | — |
| 21 | `spine_mri` | §11.2 | `office_syndrome`, `symptom_chronic_back_pain` | Green | Occupational risk (prolonged desk work) or patient-reported chronic back pain | null | 18 | null | Spine MRI (Cervical or Lumbar) | 6,500 | — |
| 22 | `multi_cancer_spotmas` | §4.1, §4.3, §4.5 | `family_hx_colon_ca`, `family_hx_breast_ca`, `family_hx_prostate_ca` | Yellow | First-degree family history of hereditary cancers; blood-based multi-cancer panel | null | 40 | null | Multi-Cancer Screening SPOT-MAS | 15,900 | — |
| 23 | `influenza_vaccine` | §9.1 | `influenza_vaccination_gap` | Orange | Annual — vaccination gap > 14 months; low burden, high preventive value | null | 1 | 59 | Influenza Vaccine (3-strain) | 490 | — |
| 24 | `influenza_vaccine_senior` | §9.1 | `influenza_vaccination_gap` | Orange | Age ≥ 60 — high-dose or adjuvanted preferred by CDC ACIP 2024 | null | 60 | null | Senior Influenza Vaccine (High-Dose) | 2,300 | — |
| 25 | `hepatitis_b_vaccine` | §9.2, §8.2 | `hepatitis_b_vaccination_status` | Red (not started) / Yellow (incomplete) | Not started = high urgency; series incomplete = continue | null | 1 | null | Hepatitis B Vaccine | TBD | confirm per-dose price |
| 26 | `pneumococcal_vaccine` | §9.4 | `pneumococcal_vaccination_gap` | Orange | Age ≥ 65 routine — ACIP 2022; or high-risk < 65 conditions | null | 65 | null | Pneumococcal Vaccine | TBD | confirm product code + price |
| 27 | `shingrix_vaccine` | §9.5 | `shingrix_vaccination_gap` | Yellow | Age ≥ 50 — 2-dose RZV series; not urgent but recommended | null | 50 | null | Shingrix (RZV) Zoster Vaccine | TBD | confirm per-dose price |
| 28 | `sleep_apnea_psg` | §11.2 | `night_shift_worker`, `bmi_obese_asian`, `sleep_apnea_screen_result` | Yellow | Night shift + obesity risk combination; or positive sleep screen questionnaire | null | 18 | null | Full Sleep Test 1 Night PSG | 10,900 | — |
| 29 | `menopause_screening` | §1.6 (TSH), §6.1 (endocrine) | `reproductive_history` | Yellow | Perimenopausal age signal; hormonal assessment panel (19 items) | female | 40 | 60 | Menopause Screening Pro Premium | 7,900 | — |
| 30 | `dementia_screening` | — | `family_hx_dementia` | Yellow | Family history of dementia or age > 65 concern | null | 65 | null | Dementia / Cognitive Decline Screening | TBD | — |
| 31 | `allergy_food_panel` | — | `symptom_food_intolerance` | Green | Patient-reported food intolerance | null | 18 | null | Food Allergy Test (20 items) | TBD | — |
| 32 | `allergy_airborne_panel` | — | `occupational_exposure_risk` | Green | Environmental or occupational exposure risk | null | 18 | null | Airborne Allergy Test (20 items) | TBD | — |
| 33 | `dengue_vaccine` | — | `dengue_vaccination_gap` | Green | Tropical endemic protection; ages 4-60 | null | 4 | 60 | Dengue Vaccine (Qdenga) | TBD | — |

**Total add-on items:** 33 (30 gender-agnostic; 3 female-only: `mammogram`, `cervical_cancer_hpv_screen`, `dexa_bone_density`, `menopause_screening`; 1 male-only: `psa_sdm`)

> **Note on `symptom_*` signals:** `symptom_palpitations`, `symptom_chronic_back_pain` are derived from the `symptom_tags[]` array in `get_clinical_signals`. They are not standalone signal IDs in the Field Dictionary today. Before the JSON files are generated, the clinical team must confirm whether these are added to the Signal Store Contract Field Dictionary as first-class signals or handled differently (e.g., a separate `get_symptom_tags` MCP tool). **Update: Proceeding with Option A (First-Class Signals) for all symptom triggers.**

---

## 7. Tier Config Derivation Notes

### Rule 1: `PREMIUM_SEVERE_SINGLE` (priority 1)

| Condition | Source | Clinical Justification |
|---|---|---|
| `ckd_rapid_progression` | §7.2 (KDIGO 2022) | eGFR decline > 5/yr = rapid progression → urgent nephrology; comprehensive evaluation warranted |
| `ascvd_very_high` | §5.1 (ACC/AHA 2013/2018) | 10-yr CV risk ≥ 20% → guideline-mandated high-intensity statin + comprehensive workup |
| `hypertensive_crisis` | §2 (ACC/AHA 2017) | SBP > 180 or DBP > 120 → emergency evaluation; multiple procedures contraindicated |
| `diabetes_confirmed` AND `dm_organ_complication_screening` | §1.2 + §6.2 (ADA 2024) | Confirmed DM with active organ complication screening gap = multi-system disease requiring Premium |

**Cannot be admin-configured.** Changing which conditions trigger Premium requires clinical review and code release.

### Rule 2: `PREMIUM_MULTI_SIGNAL` (priority 2)

**Signal pool:** 12 signals from the moderate + low-moderate tiers (see §3.3 above)
**Default min_count:** 5
**Admin-configurable:** `min_count` only (not signal pool membership)

**Rationale for pool composition:**
- Excludes high-severity signals already covered by Rule 1
- Includes all moderate + low-moderate signals that individually justify Advanced
- When 5 or more converge, the cumulative multi-system burden exceeds what Enhanced (Platinum) screening can adequately address

**What happens if min_count is wrong:**
- Too low (e.g., 2): many Advanced patients escalate to Premium unnecessarily → over-testing, cost burden
- Too high (e.g., 7): genuine multi-system patients stay in Advanced → under-testing, clinical risk
- MAT (blind test 100 cases) must confirm calibration

### Rule 3: `ADVANCED_METABOLIC_OR_CVD` (priority 3)

**Single-signal qualifiers (ANY):** 7 moderate-severity signals (see §3.2 Moderate Pool)
**Multi-signal threshold:** ≥ 2 from the low-moderate pool (13 signals)
**Admin-configurable:** multi-signal `min_count` only (default: 2)

**Design rationale:** The single-signal path covers the most common clinical entry points to Advanced (prediabetes, active hypertension, ASCVD intermediate). The count path catches patients with multiple lower-severity signals that collectively demand enhanced screening.

### Rule 4: `STANDARD_DEFAULT` (priority 4)

Always matches. No conditions. Cannot be removed or reordered — the rule array must end with a DEFAULT. The tier assignment (`Standard`) cannot be changed via Admin Panel.

---

## 8. Symptom Signal Open Item

**Issue:** The add-on items `cardiac_patch_48h` (trigger: `symptom_palpitations`) and `spine_mri` (trigger: `symptom_chronic_back_pain`) reference symptom-derived signals. In the current signal-store-contract.md, symptoms are returned as a free-form `symptom_tags[]` array (e.g., `["palpitations", "neck_pain"]`), not as individual named signal IDs in the Field Dictionary.

**Options for resolution:**
| Option | Description | Impact |
|---|---|---|
| A | Add `symptom_palpitations`, `symptom_chronic_back_pain` etc. as first-class signal IDs to the Signal Store Field Dictionary | Clean; consistent with all other trigger_signals; requires CSE update to populate these from symptom_tags |
| B | Add a separate MCP tool `get_symptom_tags(patient_token)` returning raw tags; Inference Orchestrator maps tags → add-on triggers at query time | No CSE change; but adds orchestrator logic outside Ruleset Store |
| C | Keep symptom_tags[] in `get_clinical_signals` and document that these strings can appear in trigger_signals[] as a special prefix `symptom:*` | Simpler but breaks the strict "all trigger_signals must be in Field Dictionary" rule |

**Recommendation:** Option A — add symptom signals as first-class Field Dictionary entries. Decision must be made before JSON sample files are generated.

---

## 9. Validation Checklist (Pre-Production Gate)

Run before promoting any `ruleset_version` to `status: "active"` in production:

### Structural Integrity
- [ ] All `trigger_signals[]` values exist verbatim in signal-store-contract.md Field Dictionary (exact `snake_case` match)
- [ ] All `safety_contraindication_signals[]` values are valid `flag_id` values in `get_hard_constraints.active_safety_flags[]`
- [ ] `tier_selection_rules[]` ends with exactly one `match_logic: "DEFAULT"` rule
- [ ] `tier_selection_rules[]` priorities are unique and form a contiguous sequence starting at 1
- [ ] Every `add_on_item.category` is in the enum defined in ruleset-store-contract.md JSON Schema

### Clinical Correctness
- [ ] All female-only add-ons have `gender_constraint: "female"` (mammogram, cervical screen, DEXA, menopause)
- [ ] All male-only add-ons have `gender_constraint: "male"` (psa_sdm)
- [ ] `influenza_vaccine` (age 1–59) and `influenza_vaccine_senior` (age 60+) are mutually exclusive by age band
- [ ] `exercise_stress_test` has `safety_contraindication_signals: ["hypertensive_crisis"]`
- [ ] `ldct_lung` `age_min: 50`, `age_max: 80` (USPSTF 2021 — not the old 55–80 threshold)
- [ ] `colonoscopy` `age_min: 45` (USPSTF 2021 — not the old 50 threshold)

### Product Integration
- [ ] All `navavej_product.product_code` values are confirmed with client or explicitly flagged "TBD"
- [ ] Open Questions #7 and #10 from navavej-checkup-package-discovery.md are resolved (colonoscopy standalone; PSA standalone)
- [ ] All `price_thb` values reflect current non-promotional pricing (Expo pricing expires 2026-03-31)

### Functional Testing
- [ ] Somchai W. (`sample_patient_checkup.json`) produces `rule_preliminary_tier: "Advanced"` with active ruleset
- [ ] Female patient (age 42) produces add-on library containing `mammogram` but NOT `psa_sdm`
- [ ] Male patient (age 54) produces add-on library containing `psa_sdm` but NOT `mammogram`, `cervical_cancer_hpv_screen`, `dexa_bone_density`, `menopause_screening`
- [ ] Patient with `hypertensive_crisis` in `active_safety_flags` does NOT receive `exercise_stress_test`
- [ ] Patient with eGFR < 30 is assigned `tier_ceiling: "Standard"` (no Premium/Advanced if frailty rule applies — confirm with clinical team)

### Medical Acceptance Test
- [ ] Blind test of 100+ patient cases
- [ ] ≥ 3 of 5 clinical experts agree on expected tier and add-ons for each case
- [ ] System output matches expert consensus on ≥ 95% of cases (TOR §6.2)
- [ ] Disagreement cases are documented and fed back to ruleset calibration

---

## 10. Files to be Generated (Next Step)

After clinical team reviews this framework and resolves the Symptom Signal Open Item (§8), the following sample JSON files will be generated:

| File | Record Type | Content |
|---|---|---|
| `samples/sample_ruleset_tier_config.json` | `ruleset_tier_config` | Complete DB record — all 4 tier selection rules, production-ready, consistent with ruleset-store-contract.md example |
| `samples/sample_add_on_items.json` | `add_on_item[]` | All 28 add-on items as individual DB records — complete catalog, using signal IDs and product codes confirmed in this framework |

Both files will use Somchai W.'s `patient_token: "tok_hmac_56291047"` as the reference patient for consistency with `sample_patient_checkup.json` and the signal-store-contract.md example response.

---

*This framework is reviewed and approved before JSON sample generation proceeds.*
*Companion documents: `ruleset-store-contract.md`, `signal-store-contract.md`, `clinical-guidelines-reference.md`, `navavej-checkup-package-discovery.md`*

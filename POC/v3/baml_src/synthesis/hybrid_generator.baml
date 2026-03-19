// Hybrid Synthesis - Step 1: Perturb from Seed
function PerturbSignalStoreRecord(seed: SignalStoreRecord, scenario: ClinicalScenario) -> SignalStoreRecord {
  client NavaveijClient

  prompt #"
    ### MISSION:
    You are a clinical data synthesizer. Your task is to generate a realistic VARIATION of a 'Seed' record.
    The goal is to create a new unique patient record that still fits the scenario: {{ scenario }}.

    ### INPUT SEED:
    {{ seed }}

    ### PERTURBATION RULES:
    1. DEMOGRAPHICS: 
       - Change the patient name to a realistic Thai name (e.g., "Kanya P.", "Wichai S.").
       - Randomize Age within a +/- 5-year range of the seed. Update `birth_date` and `date_of_birth_token` accordingly.
       - Ensure `patient_demographics` and `waist_circumference` thresholds match the gender and ethnicity.
    2. TIMELINES:
       - Shift all dates to be relative to TODAY: 2026-03-15.
       - `computed_at` should be "2026-03-15T03:00:00Z".
       - History dates should be realistic (e.g., last visit 6 months ago, previous visit 18 months ago).
    3. NUMERICAL JITTER & CLINICAL LOGIC:
       - Apply a jitter of +/- 5% to numerical values (BP, BMI, Labs).
       - IMPORTANT: Maintain medical consistency. If scenario is "Healthy", don't jitter labs into abnormal ranges. If scenario is "UncontrolledHypertension", SBP must be >= 140.
       - Recalculate `category` and `interpretation` if the jittered value crosses a threshold (refer to clinical-guidelines-reference.md).
    4. VARIATION:
       - Slightly vary 1-2 secondary factors (e.g., change specific symptom tags, adjust physical activity level).
    5. DATA INTEGRITY: 
       - Generate a new unique `patient_token` (e.g., tok_hmac_[random]).
       - Maintain the exact Signal Store Contract structure.

    {{ ctx.output_format }}
  "#
}

// Hybrid Synthesis - Step 2: Critique and Fix
function CritiqueAndFixRecord(record: SignalStoreRecord) -> SignalStoreRecord {
  client NavaveijClient

  prompt #"
    ### MISSION:
    Identify and fix any medical or logical inconsistencies in the following Signal Store Record.
    You must ensure 100% compliance with clinical-guidelines-reference.md and signal-store-contract.md.

    ### RECORD TO AUDIT:
    {{ record }}

    ### AUDIT CHECKLIST:

    1. VALID SIGNAL IDs (VOCABULARY CONTROL):
       Only use these IDs in `applicable_signals`, `signals_fired`, and `missing_signals`. DO NOT use generic status IDs.
       - High Severity (Premium): ckd_rapid_progression, ascvd_very_high, hypertensive_crisis, diabetes_confirmed (requires dm_organ_complication_screening), liver_enzyme_elevation_significant (requires fibroscan_indication).
       - Moderate (Advanced ANY): prediabetes_confirmed, diabetes_confirmation_required, ascvd_risk_intermediate, htn_active, lung_ct_threshold_met, ckd_comorbidity, bmi_obese_asian.
       - Low-Moderate (Advanced COUNT >= 2): bmi_overweight_asian, low_hdl, high_triglycerides, high_ldl, bp_stage1_htn, bp_worsening, family_hx_premature_cad, at_risk_alcohol_use, office_syndrome, night_shift_worker, uric_acid_hyperuricemia, dyslipidemia_active, fibroscan_indication.
       - Gaps: colonoscopy_screening_gap, mammogram_screening_gap, pap_smear_screening_gap, dexa_screening_gap, influenza_vaccination_gap, hepatitis_b_vaccination_status, hpv_vaccination_gap, pneumococcal_vaccination_gap, shingrix_vaccination_gap.

    2. CROSS-FIELD CONSISTENCY (TRUTH-ANCHORING):
       - TIERING LOGIC: Update `rule_preliminary_tier` strictly:
         * "Premium": Any High Severity signal fired; OR >= 5 Moderate/Low-Moderate signals fired.
         * "Advanced": Any single Moderate signal fired; OR >= 2 Low-Moderate signals fired.
         * "Standard": Default if no other rules match.
       - ASCVD RISK: Check `ascvd_10yr_risk.inputs_used`. Age, Sex, Total Cholesterol, HDL, Systolic BP, Smoking status, and Diabetes status MUST match other fields.
       - BP CATEGORY: If SBP >= 180 or DBP >= 120 -> "Hypertensive Crisis". If SBP >= 140 or DBP >= 90 -> "Stage2_HTN". If SBP 130-139 -> "Stage1_HTN".
       - BMI: If ethnicity is "asian" and BMI >= 27.5 -> "Obese". If BMI >= 23 -> "Overweight".

    3. CONFIDENCE FORMULA LOGIC:
       - Every signal ID in `signals_fired` MUST also be present in `applicable_signals`.
       - `signal_coverage` = `len(signals_fired) / len(applicable_signals)`. Ensure this ratio is between 0.3 and 1.0. 
       - `data_completeness`: Ensure `populated_key_fields` count matches the actual non-null fields in the JSON.

    4. GENDER & AGE SAFETY:
       - If gender is "male", REMOVE any: mammogram, pap_smear, breast CA history.
       - Ensure age-based screenings (e.g., Lung LDCT for 50-80, Shingrix for >=50) are correctly triggered or excluded.

    5. TEMPORAL CONSISTENCY:
       - All `history` dates must be PRIOR to `computed_at` (2026-03-15).
       - Overdue days calculation: `today - last_performed_date`.

    ### IMPORTANT:
    - DO NOT EXPLAIN.
    - RETURN ONLY THE RECTIFIED RAW JSON OBJECT.
    - NO MARKDOWN CODE BLOCKS.

    {{ ctx.output_format }}
  "#
}

function ListScenarioSeeds() -> string[] {
  client NavaveijClient
  prompt #"
    List the available seed filenames for clinical scenarios in a medical synthesis context.
    Return a list of strings representing clinical scenario seed files.

    {{ ctx.output_format }}
  "#
}

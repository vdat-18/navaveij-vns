
class ReproductiveHistoryDetail {
  age_at_menarche int?
  age_at_menopause int?
  num_children int?
  hormonal_contraception bool?
}

class EnrichmentFields {
  chief_complaint string?
  occupational_tags string[]
  computer_hours_per_day float?
  night_shift_worker bool?
  factory_chemical_exposure bool?
  stress_level string? // "Low", "Moderate", "High"
  snoring_or_sleep_apnea bool?
  smoking_pack_years float?
  quit_years_ago float? // For former smokers
  alcohol_units_per_week float?
  reproductive_history ReproductiveHistoryDetail?
  history_of_gdm bool? // History of Gestational Diabetes
  is_retired bool? 
  // Hypertension-specific enrichment
  high_salt_intake bool?
  medication_adherence_note string?
  home_bp_monitoring bool?
  
  // We can also suggest additional specific vaccine gaps if missing
  suggested_vaccines VaccinationGap[]
}

function EnrichHealthyPatientRecord(record: SignalStoreRecord) -> EnrichmentFields {
  client NavaveijClient

  prompt #"
    ### MISSION:
    You are a senior physician specializing in preventive medicine. 
    Analyze the following patient record and infer realistic clinical, occupational, and behavioral details to enrich the data for a high-fidelity demonstration.

    ### PATIENT DATA:
    {{ record }}

    ### INFERENCE RULES:
    1. CHIEF COMPLAINT:
       - Healthy/Wellness: suggest minor wellness concerns.
       - Metabolic Risk: link to cardiometabolic/fatigue.
       - Senior (Age > 65): link to geriatric concerns (joint pain, cancer screening gaps).
       - Uncontrolled Hypertension: link to HTN symptoms (morning headaches, blurred vision, dizziness).

    2. OCCUPATIONAL & BEHAVIORAL:
       - Hypertension: Often associated with 'High' stress_level and sedentary 'office_syndrome'.
       - Diet: If HTN is uncontrolled (>140/90), infer 'high_salt_intake'=true and provide a realistic 'medication_adherence_note' (e.g., "Missed doses on weekends").
       - Home BP: Infer if the patient is compliant or proactive.

    3. MEDICAL & REPRODUCTIVE:
       - Senior: Set 'is_retired'=true and chronic symptoms like 'joint_pain'.
       - Metabolic: history_of_gdm for high BMI females.

    4. VACCINATION GAPS:
       - High priority: 'pneumococcal' (PCV20) for any patient with HTN or ASCVD risk markers.
       - Age >= 50: 'shingrix'.
       - Always add missing 'hepatitis_b' or 'hpv' if age-appropriate.

    ### OUTPUT REQUIREMENT:
    - Your inferences MUST be clinically consistent with the biomarkers and demographics provided.
    - DO NOT alter existing data, only provide the new enriched fields.

    {{ ctx.output_format }}
  "#
}

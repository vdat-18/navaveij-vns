// Signal Store Types - Based on signal-store-contract.md v1.0
// These types represent the pre-computed Signal Store DB record structure

class PatientDemographics {
  gender string // "male" | "female" | "other"
  age int
  date_of_birth_token string
  ethnicity string // "asian" | "caucasian" | "african" | "hispanic" | "other" | "unknown"
  bmi_threshold_profile string // "asian_adjusted" | "who_global"
}

class EligibilityExclusion {
  test_code string
  test_label string
  reason_code string // "gender_male_ineligible" | "gender_female_ineligible" | "age_below_threshold" | "age_above_threshold" | "age_above_threshold_male" | "age_above_threshold_female" | "contraindicated_with_active_condition" | "admin_configured_exclusion"
  reason_label string
  guideline string
  overridable bool // Always false
}

class SafetyFlag {
  flag_id string // e.g., "hypertensive_crisis", "ckd_no_contrast", "hypoglycemia_active"
  flag_label string
  restricts string[]
  guideline string
}

class HardConstraints {
  patient_token string
  patient_demographics PatientDemographics
  eligibility_exclusions EligibilityExclusion[]
  active_safety_flags SafetyFlag[]
  tier_ceiling string? // "Standard" | "Advanced" | "Premium" | null
  computed_at string
  pipeline_run_id string
}

class RiskFlag {
  flag_id string // Must match signal ID from catalog
  label string
  severity string // "Low" | "Moderate" | "High" | "Critical"
  source_signals string[]
  guideline string
  add_on_triggers string[]
}

class ComorbidityTag {
  tag string // "HTN" | "DM" | "CKD" | "Dyslipidemia" | "Prediabetes" | "Hyperuricemia"
  label string
  onset_year int
  organ_risk_tags string[]
  on_treatment bool
  treatment_note string?
}

class ScreeningGap {
  screening_id string // "colonoscopy" | "mammogram" | "pap_smear" | "lung_ldct" | "dexa" | "est" | "echo"
  label string
  last_performed_date string?
  recommended_interval_months int
  overdue_days int?
  overdue_score float? // 0.0-1.0
  priority_color string // "Red" | "Orange" | "Yellow" | "Green"
  guideline string
  note string?
}

class VaccinationGap {
  vaccine_id string // "influenza" | "hepatitis_b" | "hpv" | "pneumococcal" | "shingrix"
  label string
  last_administered_date string?
  overdue_days int?
  recommended_annual bool?
  series_complete bool?
  doses_received int?
  doses_required int?
  eligible_since_age int?
  age_at_evaluation int?
  years_until_due int?
  priority_color string // "Red" | "Orange" | "Yellow" | "Green"
  guideline string
  note string?
  anti_hbs_checked bool?
}

class AbnormalTrigger {
  trigger_id string
  label string
  source_lab string?
  source_value float?
  source_unit string?
  suggested_follow_up string[]
  urgency string // "Urgent" | "Soon" | "Routine"
}

class FamilyHistoryFlags {
  ca_breast bool
  ca_colon bool
  ca_prostate bool
  premature_cad bool
  premature_cad_detail string?
  ca_colon_detail string?
}

class SmokingBehavior {
  status string // "current" | "former" | "never"
  pack_years float?
  quit_years_ago float?
  lung_ct_threshold_met bool
}

class AlcoholBehavior {
  audit_c_score float?
  risk_level string // "none" | "low" | "borderline" | "at_risk" | "dependence_possible"
  fibroscan_indicated bool
  note string?
}

class OccupationalBehavior {
  tags string[]
  add_ons_triggered string[]
}

class PhysicalActivityBehavior {
  days_per_week int?
  level string // "sufficient" | "insufficient" | "sedentary" | "unknown"
  add_ons_triggered string[]?
}

class BehavioralFlags {
  smoking SmokingBehavior?
  alcohol AlcoholBehavior?
  occupational OccupationalBehavior?
  physical_activity PhysicalActivityBehavior?
}

class ClinicalSignals {
  patient_token string
  rule_preliminary_tier string // "Standard" | "Advanced" | "Premium"
  overall_risk_level string // "Low" | "Moderate" | "High"
  applicable_signals string[] // All 40 signal IDs from catalog evaluated for this patient
  signals_fired string[] // Subset that evaluated to active
  missing_signals string[] // Signals in applicable with no source data
  risk_flags RiskFlag[]
  comorbidity_tags ComorbidityTag[]
  screening_gaps ScreeningGap[]
  vaccination_gaps VaccinationGap[]
  abnormal_triggers AbnormalTrigger[]
  family_history_flags FamilyHistoryFlags
  behavioral_flags BehavioralFlags
  symptom_tags string[]
  computed_at string
  pipeline_run_id string
}

class BMITrend {
  current float
  unit string // "kg/m2"
  threshold_profile string // "asian_adjusted" | "who_global"
  category string // "Underweight" | "Normal" | "Overweight" | "Obese" | "Morbidly_Obese"
  trend_direction string // "increasing" | "stable" | "decreasing" | "insufficient_data"
  slope_per_year float? // Annualized slope from ≥3 data points
  history BMIDataPoint[]
  alert string?
}

class BMIDataPoint {
  date string
  value float
}

class BloodPressureLatest {
  sbp int
  dbp int
  date string
}

class BPDataPoint {
  date string
  sbp int
  dbp int
}

class BloodPressureTrend {
  latest BloodPressureLatest
  unit string // "mmHg"
  category string // "Normal" | "Elevated" | "Stage1_HTN" | "Stage2_HTN" | "Crisis"
  category_label string
  trend_direction string // "increasing" | "stable" | "decreasing" | "insufficient_data"
  sbp_slope_per_year float?
  history BPDataPoint[]
  alert string?
}

class EGFRDataPoint {
  date string
  value float
}

class EGFRTrend {
  current float
  unit string // "mL/min/1.73m2"
  loinc_code string // "62238-1"
  ckd_stage string // "G1" | "G2" | "G3a" | "G3b" | "G4" | "G5"
  ckd_stage_label string
  annual_slope float? // Negative = declining, > -5 = rapid progression
  rapid_progression bool
  rapid_progression_threshold float // -5.0
  history EGFRDataPoint[]
  alert string?
}

class LabReferenceRange {
  low float?
  high float?
  optimal float?
  borderline_high_low float?
  borderline_high_high float?
  normal_high float?
  borderline_high float?
  uln float? // Upper limit of normal
  uln_male float?
  low_male float?
  protective float?
  desirable_high float?
  age_adjusted_uln_50s float?
}

class LabDataPoint {
  date string
  value float
}

class LabTrend {
  lab_id string // "fbs" | "hba1c" | "ldl" | "hdl" | "triglycerides" | "total_cholesterol" | "alt" | "ast" | "creatinine" | "tsh" | "psa" | "uric_acid"
  label string
  loinc_code string
  current_value float
  unit string
  reference_range LabReferenceRange?
  interpretation string // "N" | "H" | "L" | "HH" | "LL" | "A"
  category string
  velocity_per_year float? // Rate of change per year from ≥3 data points
  trend_direction string // "increasing" | "stable" | "decreasing" | "insufficient_data"
  trend_flag string? // "worsening" | "improving" | "stable"
  history LabDataPoint[]
  alert string?
  trend_data_note string?
  sdm_note string? // For PSA only
}

class ASCVDInputs {
  age int
  sex string
  race string
  total_cholesterol float
  hdl float
  systolic_bp int
  bp_treatment bool
  diabetes bool
  smoking string // "current" | "former" | "never"
}

class ASCVDRisk {
  score float // 0.0-1.0
  score_pct float
  category string // "Low" | "Borderline" | "Intermediate" | "High" | "Very_High"
  category_label string
  inputs_used ASCVDInputs
  guideline string
  note string?
}

class WaistCircumference {
  value float
  unit string // "cm"
  threshold_male_asian float?
  category string
  note string?
}

class BiomarkerTrends {
  patient_token string
  bmi BMITrend
  blood_pressure BloodPressureTrend
  egfr EGFRTrend
  labs LabTrend[]
  ascvd_10yr_risk ASCVDRisk
  waist_circumference WaistCircumference?
  computed_at string
  pipeline_run_id string
}

class SignalStoreMeta {
  data_completeness_ratio float // 0.0-1.0
  total_key_fields int
  populated_key_fields int
  missing_data_fields string[]
}

class SignalStoreRecord {
  schema_version string
  patient_token string
  computed_at string
  pipeline_run_id string
  fhir_snapshot_version string
  hard_constraints HardConstraints
  clinical_signals ClinicalSignals
  biomarker_trends BiomarkerTrends
  metadata SignalStoreMeta
}


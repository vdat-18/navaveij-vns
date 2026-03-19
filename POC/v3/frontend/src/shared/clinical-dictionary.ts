export const CLINICAL_DICTIONARY: Record<string, string> = {
    // Tiers
    "Standard": "Standard",
    "Advanced": "Advanced",
    "Premium": "Premium",

    // Risk Levels
    "Low": "Low Risk",
    "Moderate": "Moderate Risk",
    "High": "High Risk",
    "Very High": "Very High Risk",

    // Biomarker Categories
    "Normal": "Normal",
    "Optimal": "Optimal",
    "Near-optimal": "Near-optimal",
    "Protective": "Protective",
    "Overweight": "Overweight",
    "Obese": "Obese",
    "Stage 1 Hypertension": "Stage 1 HTN",
    "Stage 2 Hypertension": "Stage 2 HTN",
    "Hypertensive Crisis": "HTN Crisis",

    // Clinical Signals
    "bmi_obese_asian": "Obese (Asian)",
    "bmi_overweight_asian": "Overweight (Asian)",
    "ascvd_very_high": "Very High ASCVD Risk",
    "hypertensive_crisis": "Hypertensive Crisis",
    "diabetes_confirmed": "Diabetes (Confirmed)",
    "ckd_rapid_progression": "Rapid CKD Progression",
    "liver_enzyme_elevation_significant": "Significant Liver Enzyme Elevation",
    "fibroscan_indication": "Fibroscan Indicated",
    "prediabetes_confirmed": "Prediabetes Confirmed",
    "ascvd_risk_intermediate": "Intermediate ASCVD Risk",
    "htn_active": "Active Hypertension",
    "low_hdl": "Low HDL",
    "high_triglycerides": "High Triglycerides",
    "high_ldl": "High LDL",
    "bp_stage1_htn": "Stage 1 HTN",
    "bp_worsening": "Worsening BP Trend",
    "uric_acid_hyperuricemia": "Hyperuricemia",
    "dyslipidemia_active": "Active Dyslipidemia",
    "colonoscopy_screening_gap": "Colonoscopy Gap",
    "mammogram_screening_gap": "Mammogram Gap",
    "dexa_screening_gap": "DEXA Scan Gap",
    "shingrix_vaccination_gap": "Shingles Vaccine Gap",
    "pneumococcal_vaccination_gap": "Pneumococcal Vaccine Gap",
    "influenza_vaccination_gap": "Flu Vaccine Gap",

    // CKD Stages
    "G1": "Stage G1 (Normal)",
    "G2": "Stage G2 (Mild)",
    "G3a": "Stage G3a (Mild-Mod)",
    "G3b": "Stage G3b (Mod-Severe)",
    "G4": "Stage G4 (Severe)",
    "G5": "Stage G5 (Failure)"
};

export function translateIdentifier(key: string): string {
    if (!key) return "--";
    return CLINICAL_DICTIONARY[key] || key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
}

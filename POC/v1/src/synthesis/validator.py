"""Signal Store record validation against signal-store-contract.md."""

from loguru import logger

# Base Signal ID Catalog from signal-store-contract.md Field Dictionary
BASE_SIGNAL_IDS = {
    # Lab signals (11)
    "fbs_status",
    "hba1c_status",
    "ldl_status",
    "hdl_status",
    "tg_status",
    "alt_status",
    "ast_status",
    "egfr_status",
    "tsh_status",
    "psa_sdm_status",  # male only
    "uric_acid_status",
    # Vital signals (2)
    "bp_category",
    "bmi_status",
    # Screening gaps (7)
    "colonoscopy_screening_gap",
    "mammogram_screening_gap",  # female only
    "pap_smear_screening_gap",  # female 21-65
    "lung_ldct_gap",
    "dexa_screening_gap",  # female ≥65
    "est_gap",
    "echo_gap",
    # Vaccination (5)
    "influenza_vaccination_gap",
    "hepatitis_b_vaccination_status",
    "hpv_vaccination_gap",  # ≤45
    "pneumococcal_vaccination_gap",  # ≥65
    "shingrix_vaccination_gap",  # ≥50
    # Family history (4)
    "family_hx_premature_cad",
    "family_hx_breast_ca",  # female
    "family_hx_colon_ca",
    "family_hx_prostate_ca",  # male
    # Behavioral (4)
    "smoking_status",
    "lung_ct_threshold",
    "alcohol_risk",
    "occupational_risk",
    # Comorbidity (4)
    "dm_comorbidity",
    "htn_comorbidity",
    "ckd_comorbidity",
    "dyslipidemia_comorbidity",
    # Computed (3)
    "ascvd_10yr_risk_status",
    "dm_organ_complication_screening",
    "fibroscan_indication",
    # Other (4)
    "reproductive_history",  # female
    "frax_bone_density_risk",  # female <65
    "sleep_apnea_screen_result",
    "physical_activity_level",
}


def _is_valid_signal_id(signal_id: str) -> bool:
    """Return True if signal_id is allowed by the contract and guidelines."""
    if signal_id in BASE_SIGNAL_IDS:
        return True

    # Overdue pattern from screening/vaccination gaps, e.g. colonoscopy_overdue_2557d
    if "_overdue_" in signal_id and signal_id.endswith("d"):
        return True

    # Guideline-derived flags from clinical-guidelines-reference appendix
    suffixes = (
        "_confirmed",
        "_high",
        "_low",
        "_very_high",
        "_intermediate",
        "_borderline_high",
        "_borderline",
        "_active",
        "_rapid_progression",
    )
    if signal_id.endswith(suffixes):
        return True

    # Specific known composite flags used in examples
    known_flags = {
        "prediabetes_confirmed",
        "diabetes_confirmed",
        "diabetes_confirmation_required",
        "bmi_normal_asian",
        "bmi_overweight_asian",
        "bmi_obese_asian",
        "ascvd_risk_intermediate",
        "ascvd_risk_high",
        "ascvd_very_high",
        "bp_normal",
        "bp_stage1_htn",
        "bp_stage2_htn",
        "bp_trend_worsening",
        "lifestyle_healthy",
        "influenza_due_soon",
        "hypertriglyceridemia_severe",
        "hyperuricemia",
        "office_syndrome",
        "night_shift_worker",
        "at_risk_alcohol_use",
        "lung_ct_threshold_met",
        "ckd_rapid_progression",
    }
    if signal_id in known_flags:
        return True

    return False


def validate_signal_ids(applicable_signals: list[str], signals_fired: list[str], missing_signals: list[str]) -> None:
    """Validate all signal IDs match the Signal Store Contract catalog."""
    all_signals = set(applicable_signals) | set(signals_fired) | set(missing_signals)
    invalid_signals = [s for s in all_signals if not _is_valid_signal_id(s)]

    assert not invalid_signals, f"Invalid signal IDs: {sorted(invalid_signals)}"
    assert signals_fired, "signals_fired[] cannot be empty"

    fired_not_applicable = set(signals_fired) - set(applicable_signals)
    assert not fired_not_applicable, f"signals_fired contains unknown IDs: {sorted(list(fired_not_applicable))}"

    missing_not_applicable = set(missing_signals) - set(applicable_signals)
    assert not missing_not_applicable, f"missing_signals contains unknown IDs: {sorted(list(missing_not_applicable))}"

    if applicable_signals:
        coverage = len(signals_fired) / len(applicable_signals)
        if not (0.3 <= coverage <= 1.0):
            logger.warning(f"Signal coverage {coverage:.2f} is outside range (0.3-1.0)")


def validate_signal_store_record(record: dict) -> None:
    """Validate Signal Store record structure."""
    version = record.get("schema_version")
    assert version == "signal_store_record_v1", f"Expected version 'signal_store_record_v1', got {version}"

    signals = record.get("clinical_signals", {})
    validate_signal_ids(
        signals.get("applicable_signals", []), signals.get("signals_fired", []), signals.get("missing_signals", [])
    )

    tier = signals.get("rule_preliminary_tier")
    assert tier in ["Standard", "Advanced", "Premium"], f"Invalid tier: {tier}"

    risk = signals.get("overall_risk_level")
    assert risk in ["Low", "Moderate", "High"], f"Invalid risk level: {risk}"

    meta = record.get("metadata", {})
    completeness = meta.get("data_completeness_ratio", 0.0)
    assert 0.0 <= completeness <= 1.0, f"Completeness ratio must be 0-1, got {completeness}"

    logger.info(f"Validated: {len(signals.get('signals_fired', []))} signals active")

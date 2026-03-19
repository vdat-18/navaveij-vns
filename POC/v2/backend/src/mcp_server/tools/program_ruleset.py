"""Tool for retrieving program selection ruleset from Ruleset Store."""

from loguru import logger

from src.mcp_server.utils import (
    extract_clinical_signals,
    extract_hard_constraints,
    filter_add_ons_by_demographics,
    get_current_timestamp,
    load_package_resolution_map,
    load_ruleset_add_on_items,
    load_ruleset_tier_config,
    load_signal_store_record,
    resolve_package,
    resolve_patient_token,
)




def get_program_ruleset(patient_token: str, patient_id: str | None = None) -> dict:
    """Retrieve complete program ruleset applicable to this patient.

    Returns tier selection rules, filtered add-on library, package resolution map,
    and resolved package according to Ruleset Store Contract.

    Args:
        patient_token: Canonical patient token
        patient_id: Optional legacy stable patient identifier

    Returns:
        Program ruleset dict matching Ruleset Store Contract format:
        {
            "patient_id": str,
            "ruleset_version": str,
            "admin_last_updated": str,
            "computed_at": str,
            "tier_selection_rules": [...],
            "applied_rule_id": str,
            "applied_condition": str | null,
            "rule_preliminary_tier": str,
            "package_resolution_map": {...},
            "resolved_package": {...},
            "add_on_library": [...],
            "_add_on_library_filtered_count": int,
            "_add_on_library_excluded_count": int,
            "_add_on_library_excluded_items": [...]
        }
    """
    logger.info(f"Retrieving program ruleset for patient_token: {patient_token}")
    resolved_patient_id = patient_id or resolve_patient_token(patient_token)

    # Load Signal Store record to get patient demographics and signals_fired
    record = load_signal_store_record(patient_token=patient_token, patient_id=resolved_patient_id)
    if not record:
        logger.error(f"Signal Store record not found for patient_token: {patient_token}")
        return {
            "patient_token": patient_token,
            "ruleset_version": "v2026.03.1",
            "admin_last_updated": "",
            "computed_at": get_current_timestamp(),
            "tier_selection_rules": [],
            "applied_rule_id": "STANDARD_DEFAULT",
            "applied_condition": None,
            "rule_preliminary_tier": "Standard",
            "package_resolution_map": {},
            "resolved_package": {},
            "add_on_library": [],
            "_add_on_library_filtered_count": 0,
            "_add_on_library_excluded_count": 0,
            "_add_on_library_excluded_items": [],
        }

    hard_constraints = extract_hard_constraints(record)
    clinical_signals = extract_clinical_signals(record)

    patient_demographics = hard_constraints.get("patient_demographics", {})
    gender = patient_demographics.get("gender", "other")
    age = patient_demographics.get("age", 0)
    signals_fired = clinical_signals.get("signals_fired", [])
    rule_preliminary_tier = clinical_signals.get("rule_preliminary_tier", "Standard")

    # Load Ruleset Store data
    tier_config = load_ruleset_tier_config()
    tier_selection_rules = tier_config.get("tier_selection_rules", [])
    ruleset_version = tier_config.get("version", "v2026.03.1")
    admin_last_updated = tier_config.get("created_at", "")

    # Cleaned up: Removed redundant _evaluate_tier_rules call.
    # We rely on the Clinical Signal Engine's offline computation results already in the record.

    # Load and filter add-on items
    all_add_ons = load_ruleset_add_on_items()
    filtered_add_ons, excluded_add_ons = filter_add_ons_by_demographics(all_add_ons, gender, age)

    # Externalized: Package resolution map is now loaded from a JSON file
    package_resolution_map = load_package_resolution_map()

    # Resolve package
    resolved_package = resolve_package(rule_preliminary_tier, gender, age, package_resolution_map)

    return {
        "patient_token": patient_token,
        "ruleset_version": ruleset_version,
        "admin_last_updated": admin_last_updated,
        "computed_at": get_current_timestamp(),
        "tier_selection_rules": tier_selection_rules,
        "applied_rule_id": "RESOLVED_BY_OFFLINE_ENGINE",
        "applied_condition": "See rule_preliminary_tier",
        "rule_preliminary_tier": rule_preliminary_tier,
        "package_resolution_map": package_resolution_map,
        "resolved_package": resolved_package or {},
        "add_on_library": filtered_add_ons,
        "_add_on_library_filtered_count": len(filtered_add_ons),
        "_add_on_library_excluded_count": len(excluded_add_ons),
        "_add_on_library_excluded_items": excluded_add_ons,
    }

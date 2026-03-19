"""Tool for retrieving program selection ruleset from Ruleset Store."""

from loguru import logger

from src.mcp_server.utils import (
    extract_clinical_signals,
    extract_hard_constraints,
    filter_add_ons_by_demographics,
    get_current_timestamp,
    load_ruleset_add_on_items,
    load_ruleset_tier_config,
    load_signal_store_record,
    resolve_package,
)


def _evaluate_tier_rules(
    tier_selection_rules: list[dict], signals_fired: list[str]
) -> tuple[str | None, str | None, str]:
    """Evaluate tier selection rules against signals_fired.

    Args:
        tier_selection_rules: Ordered list of tier selection rules
        signals_fired: List of active signal IDs

    Returns:
        Tuple of (applied_rule_id, applied_condition, rule_preliminary_tier)
    """
    signals_fired_set = set(signals_fired)

    for rule in tier_selection_rules:
        if rule.get("match_logic") == "DEFAULT":
            return rule.get("rule_id"), None, rule.get("tier", "Standard")

        match_logic = rule.get("match_logic")
        conditions = rule.get("conditions", [])

        if match_logic == "ANY":
            for condition in conditions:
                condition_type = condition.get("type")
                if condition_type == "signal_active":
                    signal_ids = condition.get("signal_ids", [])
                    and_signals = condition.get("and_signal_active", [])

                    if any(sig in signals_fired_set for sig in signal_ids):
                        if not and_signals or all(sig in signals_fired_set for sig in and_signals):
                            return (
                                rule.get("rule_id"),
                                condition.get("description"),
                                rule.get("tier"),
                            )

        elif match_logic == "COUNT_THRESHOLD":
            for condition in conditions:
                if condition.get("type") == "signal_count_threshold":
                    signal_pool = condition.get("signal_pool", [])
                    min_count = condition.get("min_count", 0)

                    matching_count = sum(1 for sig in signal_pool if sig in signals_fired_set)
                    if matching_count >= min_count:
                        return (
                            rule.get("rule_id"),
                            condition.get("description"),
                            rule.get("tier"),
                        )

    return None, None, "Standard"


def get_program_ruleset(patient_token: str) -> dict:
    """Retrieve complete program ruleset applicable to this patient.

    Returns tier selection rules, filtered add-on library, package resolution map,
    and resolved package according to Ruleset Store Contract.

    Args:
        patient_token: HMAC-SHA256 pseudonymous patient identifier

    Returns:
        Program ruleset dict matching Ruleset Store Contract format:
        {
            "patient_token": str,
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

    # Load Signal Store record to get patient demographics and signals_fired
    record = load_signal_store_record(patient_token)
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

    # Evaluate tier rules to find applied rule
    applied_rule_id, applied_condition, evaluated_tier = _evaluate_tier_rules(tier_selection_rules, signals_fired)

    # Use rule_preliminary_tier from Signal Store if available, otherwise use evaluated
    final_tier = rule_preliminary_tier if rule_preliminary_tier else evaluated_tier

    # Load and filter add-on items
    all_add_ons = load_ruleset_add_on_items()
    filtered_add_ons, excluded_add_ons = filter_add_ons_by_demographics(all_add_ons, gender, age)

    # Build package resolution map (simplified - should be loaded from config)
    package_resolution_map = {
        "Standard": {
            "male": {
                "age_15_to_35": {
                    "package_name": "Gold",
                    "package_code": "GOLD_ANY",
                    "price_thb": 5900,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
                "age_36_plus": {
                    "package_name": "Gold",
                    "package_code": "GOLD_ANY",
                    "price_thb": 5900,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
            },
            "female": {
                "age_15_to_35": {
                    "package_name": "Gold",
                    "package_code": "GOLD_ANY",
                    "price_thb": 5900,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
                "age_36_plus": {
                    "package_name": "Gold",
                    "package_code": "GOLD_ANY",
                    "price_thb": 5900,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
            },
        },
        "Advanced": {
            "male": {
                "age_35_plus": {
                    "package_name": "Platinum — Men",
                    "package_code": "PLAT_M",
                    "price_thb": 8700,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
            },
            "female": {
                "age_35_plus": {
                    "package_name": "Platinum — Women",
                    "package_code": "PLAT_F",
                    "price_thb": 13500,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
            },
        },
        "Premium": {
            "male": {
                "age_40_plus": {
                    "package_name": "Diamond — Men",
                    "package_code": "DIAM_M",
                    "price_thb": 15000,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
            },
            "female": {
                "age_40_plus": {
                    "package_name": "Diamond — Women",
                    "package_code": "DIAM_F",
                    "price_thb": 19000,
                    "source": "navavej-checkup-package-discovery.md §2",
                },
            },
        },
    }

    # Resolve package
    resolved_package = resolve_package(final_tier, gender, age, package_resolution_map)

    return {
        "patient_token": patient_token,
        "ruleset_version": ruleset_version,
        "admin_last_updated": admin_last_updated,
        "computed_at": get_current_timestamp(),
        "tier_selection_rules": tier_selection_rules,
        "applied_rule_id": applied_rule_id or "STANDARD_DEFAULT",
        "applied_condition": applied_condition,
        "rule_preliminary_tier": final_tier,
        "package_resolution_map": package_resolution_map,
        "resolved_package": resolved_package or {},
        "add_on_library": filtered_add_ons,
        "_add_on_library_filtered_count": len(filtered_add_ons),
        "_add_on_library_excluded_count": len(excluded_add_ons),
        "_add_on_library_excluded_items": excluded_add_ons,
    }

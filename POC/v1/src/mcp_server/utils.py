"""Utility functions for loading Signal Store and Ruleset Store data."""

import json
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

# Constants
SIGNAL_STORE_DIR = Path("assets/synthesis")
RULESET_TIER_CONFIG_PATH = Path(
    "doc_outputs/architecture/AI/Recommendation Engine/v3/samples/sample_ruleset_tier_config.json"
)
RULESET_ADD_ON_ITEMS_PATH = Path(
    "doc_outputs/architecture/AI/Recommendation Engine/v3/samples/sample_add_on_items.json"
)


def load_signal_store_record(patient_token: str) -> dict | None:
    """Load Signal Store record by patient_token from JSON files.

    Args:
        patient_token: HMAC-SHA256 pseudonymous patient identifier

    Returns:
        Complete Signal Store record dict, or None if not found
    """
    if not SIGNAL_STORE_DIR.exists():
        logger.warning(f"Signal Store directory not found: {SIGNAL_STORE_DIR}")
        return None

    # Search recursively for record_*.json in all scenario subdirectories
    for file_path in SIGNAL_STORE_DIR.glob("**/record_*.json"):
        with open(file_path, encoding="utf-8") as f:
            record = json.load(f)
            if record.get("patient_token") == patient_token:
                logger.debug(f"Found Signal Store record: {file_path.parent.name}/{file_path.name}")
                return record

    logger.warning(f"Record not found for token: {patient_token}")
    return None


def extract_hard_constraints(record: dict) -> dict:
    """Extract hard_constraints section from Signal Store record.

    Args:
        record: Complete Signal Store record

    Returns:
        Hard constraints dict matching Signal Store Contract format
    """
    return record.get("hard_constraints", {})


def extract_clinical_signals(record: dict) -> dict:
    """Extract clinical_signals section from Signal Store record.

    Args:
        record: Complete Signal Store record

    Returns:
        Clinical signals dict matching Signal Store Contract format
    """
    return record.get("clinical_signals", {})


def extract_biomarker_trends(record: dict) -> dict:
    """Extract biomarker_trends section from Signal Store record.

    Args:
        record: Complete Signal Store record

    Returns:
        Biomarker trends dict matching Signal Store Contract format
    """
    return record.get("biomarker_trends", {})


def load_ruleset_tier_config() -> dict:
    """Load tier selection rules from Ruleset Store sample JSON.

    Returns:
        Ruleset tier config dict with tier_selection_rules array
    """
    if not RULESET_TIER_CONFIG_PATH.exists():
        logger.error(f"Ruleset tier config not found: {RULESET_TIER_CONFIG_PATH}")
        return {"tier_selection_rules": []}

    with open(RULESET_TIER_CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
        return config


def load_ruleset_add_on_items() -> list[dict]:
    """Load add-on items from Ruleset Store sample JSON.

    Returns:
        List of add-on item dicts
    """
    if not RULESET_ADD_ON_ITEMS_PATH.exists():
        logger.error(f"Ruleset add-on items not found: {RULESET_ADD_ON_ITEMS_PATH}")
        return []

    with open(RULESET_ADD_ON_ITEMS_PATH, encoding="utf-8") as f:
        data = json.load(f)
        return data.get("items", [])


def filter_add_ons_by_demographics(
    add_on_items: list[dict],
    gender: str,
    age: int,
) -> tuple[list[dict], list[dict]]:
    """Filter add-on items by patient demographics.

    Args:
        add_on_items: List of all add-on item dicts
        gender: Patient gender ("male", "female", "other")
        age: Patient age

    Returns:
        Tuple of (filtered_items, excluded_items) where excluded_items contains
        items filtered out with exclusion_reason
    """
    filtered = []
    excluded = []

    for item in add_on_items:
        if item.get("status") != "active":
            continue

        gender_constraint = item.get("gender_constraint")
        age_min = item.get("age_min")
        age_max = item.get("age_max")

        # Check gender constraint
        if gender_constraint and gender_constraint != gender:
            exclusion_reason = (
                f"gender_{gender}_ineligible" if gender in ["male", "female"] else "gender_constraint_mismatch"
            )
            excluded.append(
                {
                    "item_code": item.get("item_code"),
                    "exclusion_reason": exclusion_reason,
                }
            )
            continue

        # Check age constraints
        if age_min is not None and age < age_min:
            excluded.append(
                {
                    "item_code": item.get("item_code"),
                    "exclusion_reason": "age_below_minimum",
                }
            )
            continue

        if age_max is not None and age > age_max:
            excluded.append(
                {
                    "item_code": item.get("item_code"),
                    "exclusion_reason": "age_above_maximum",
                }
            )
            continue

        filtered.append(item)

    return filtered, excluded


def resolve_package(
    tier: str,
    gender: str,
    age: int,
    package_resolution_map: dict,
) -> dict | None:
    """Resolve package name and price from tier, gender, and age.

    Args:
        tier: Program tier ("Standard", "Advanced", "Premium")
        gender: Patient gender ("male", "female", "other")
        age: Patient age

    Returns:
        Resolved package dict with package_name, package_code, price_thb,
        or None
    """
    tier_map = package_resolution_map.get(tier, {})
    gender_map = tier_map.get(gender, {})

    # Determine age band
    age_band = None
    age_band_keys = [
        "age_15_to_35",
        "age_35_plus",
        "age_36_plus",
        "age_40_plus",
    ]
    for band_key in age_band_keys:
        if band_key in gender_map:
            # Simple age band matching (can be enhanced)
            if "15_to_35" in band_key and 15 <= age <= 35:
                age_band = band_key
                break
            elif "35_plus" in band_key and age >= 35:
                age_band = band_key
                break
            elif "36_plus" in band_key and age >= 36:
                age_band = band_key
                break
            elif "40_plus" in band_key and age >= 40:
                age_band = band_key
                break

    if not age_band:
        # Fallback to first available age band
        age_band = next(iter(gender_map.keys()), None)

    if not age_band:
        return None

    package_info = gender_map.get(age_band, {})
    if not package_info:
        return None

    return {
        "tier": tier,
        "gender": gender,
        "age": age,
        "age_band": age_band,
        "package_name": package_info.get("package_name"),
        "package_code": package_info.get("package_code"),
        "price_thb": package_info.get("price_thb"),
    }


def get_current_timestamp() -> str:
    """Get current ISO 8601 UTC timestamp.

    Returns:
        ISO 8601 formatted timestamp string
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

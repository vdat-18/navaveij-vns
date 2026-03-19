"""Utility functions for loading Signal Store and Ruleset Store data."""

import json
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from src.services.cache import cache_service
from shared.settings import settings

V2_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = Path(__file__).resolve().parents[5]


def _resolve_existing_path(candidates: list[Path], default_path: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return default_path


SIGNAL_STORE_DIR = V2_ROOT / "assets/synthesis/generated"
RULESET_TIER_CONFIG_PATH = _resolve_existing_path(
    candidates=[
        V2_ROOT / "assets/synthesis/rulesets/sample_ruleset_tier_config.json",
        REPO_ROOT / "doc_outputs/architecture/AI/Recommendation Engine/v3/samples/sample_ruleset_tier_config.json",
        REPO_ROOT / "POC/v3/assets/synthesis/rulesets/sample_ruleset_tier_config.json",
    ],
    default_path=V2_ROOT / "assets/synthesis/rulesets/sample_ruleset_tier_config.json",
)
RULESET_ADD_ON_ITEMS_PATH = _resolve_existing_path(
    candidates=[
        V2_ROOT / "assets/synthesis/rulesets/sample_add_on_items.json",
        REPO_ROOT / "doc_outputs/architecture/AI/Recommendation Engine/v3/samples/sample_add_on_items.json",
        REPO_ROOT / "POC/v3/assets/synthesis/rulesets/sample_add_on_items.json",
    ],
    default_path=V2_ROOT / "assets/synthesis/rulesets/sample_add_on_items.json",
)
PACKAGE_RESOLUTION_PATH = _resolve_existing_path(
    candidates=[
        V2_ROOT / "assets/synthesis/rulesets/sample_package_resolution.json",
        REPO_ROOT / "doc_outputs/architecture/AI/Recommendation Engine/v3/samples/sample_package_resolution.json",
        REPO_ROOT / "POC/v3/assets/synthesis/rulesets/sample_package_resolution.json",
    ],
    default_path=V2_ROOT / "assets/synthesis/rulesets/sample_package_resolution.json",
)
TIMELINE_SAMPLE_PATH = _resolve_existing_path(
    candidates=[
        V2_ROOT / "assets/synthesis/timeline.json",
        REPO_ROOT / "doc_outputs/architecture/AI/Recommendation Engine/v3/demo/backend/data/timeline.json",
    ],
    default_path=V2_ROOT / "assets/synthesis/timeline.json",
)
PATIENT_REGISTRY_PATH = V2_ROOT / "assets/patient_registry.json"


def _resolve_ttl(ttl_seconds: int) -> int:
    if ttl_seconds > 0:
        return ttl_seconds
    return settings.cache_ttl_seconds


def _cache_key_for_path(prefix: str, path: Path) -> str:
    if path.exists():
        return f"{prefix}:{path}:{path.stat().st_mtime_ns}"
    return f"{prefix}:{path}:missing"


def load_patient_registry() -> list[dict]:
    cache_key = _cache_key_for_path("registry", PATIENT_REGISTRY_PATH)
    if settings.cache_enabled:
        hit, cached = cache_service.get(cache_key)
        if hit:
            return cached
    if not PATIENT_REGISTRY_PATH.exists():
        if settings.cache_enabled:
            cache_service.set(cache_key, [], _resolve_ttl(settings.cache_registry_ttl_seconds))
        return []
    with open(PATIENT_REGISTRY_PATH, encoding="utf-8") as f:
        registry = json.load(f)
    if settings.cache_enabled:
        cache_service.set(cache_key, registry, _resolve_ttl(settings.cache_registry_ttl_seconds))
    return registry


def resolve_patient_id(patient_token: str) -> str | None:
    registry = load_patient_registry()
    patient = next((item for item in registry if item.get("patient_token") == patient_token), None)
    return patient.get("patient_id") if patient else None


def resolve_patient_token(patient_id: str) -> str | None:
    registry = load_patient_registry()
    patient = next((item for item in registry if item.get("patient_id") == patient_id), None)
    return patient.get("patient_token") if patient else None


def load_signal_store_record(patient_token: str | None = None, patient_id: str | None = None) -> dict | None:
    """Load Signal Store record by patient_token (preferred) or patient_id.

    Args:
        patient_token: Canonical patient token
        patient_id: Legacy stable patient identifier

    Returns:
        Complete Signal Store record dict, or None if not found
    """
    resolved_id = patient_id
    if not resolved_id and patient_token:
        resolved_id = resolve_patient_id(patient_token)
    if not resolved_id:
        logger.warning("Signal Store lookup skipped: missing patient_token/patient_id")
        return None
    cache_key = f"signal_store:{resolved_id}"
    if settings.cache_enabled:
        hit, cached = cache_service.get(cache_key)
        if hit:
            return cached

    if not SIGNAL_STORE_DIR.exists():
        logger.warning(f"Signal Store directory not found: {SIGNAL_STORE_DIR}")
        if settings.cache_enabled:
            cache_service.set(cache_key, None, _resolve_ttl(settings.cache_signal_store_ttl_seconds))
        return None

    # Search recursively for record_*.json in all scenario subdirectories
    for file_path in SIGNAL_STORE_DIR.glob("**/record_*.json"):
        with open(file_path, encoding="utf-8") as f:
            try:
                record = json.load(f)
                # Check both top-level and inside hard_constraints
                actual_id = record.get("patient_id") or record.get("hard_constraints", {}).get("patient_id")
                
                if actual_id == resolved_id:
                    logger.debug(f"Found Signal Store record: {file_path.parent.name}/{file_path.name}")
                    if settings.cache_enabled:
                        cache_service.set(cache_key, record, _resolve_ttl(settings.cache_signal_store_ttl_seconds))
                    return record
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                continue

    logger.warning(f"Record not found for ID: {resolved_id}")
    if settings.cache_enabled:
        cache_service.set(cache_key, None, _resolve_ttl(settings.cache_signal_store_ttl_seconds))
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
    cache_key = _cache_key_for_path("ruleset_tier", RULESET_TIER_CONFIG_PATH)
    if settings.cache_enabled:
        hit, cached = cache_service.get(cache_key)
        if hit:
            return cached
    if not RULESET_TIER_CONFIG_PATH.exists():
        logger.error(f"Ruleset tier config not found: {RULESET_TIER_CONFIG_PATH}")
        fallback = {"tier_selection_rules": []}
        if settings.cache_enabled:
            cache_service.set(cache_key, fallback, _resolve_ttl(settings.cache_ruleset_ttl_seconds))
        return fallback

    with open(RULESET_TIER_CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    if settings.cache_enabled:
        cache_service.set(cache_key, config, _resolve_ttl(settings.cache_ruleset_ttl_seconds))
    return config


def load_ruleset_add_on_items() -> list[dict]:
    """Load add-on items from Ruleset Store sample JSON.

    Returns:
        List of add-on item dicts
    """
    cache_key = _cache_key_for_path("ruleset_add_ons", RULESET_ADD_ON_ITEMS_PATH)
    if settings.cache_enabled:
        hit, cached = cache_service.get(cache_key)
        if hit:
            return cached
    if not RULESET_ADD_ON_ITEMS_PATH.exists():
        logger.error(f"Ruleset add-on items not found: {RULESET_ADD_ON_ITEMS_PATH}")
        if settings.cache_enabled:
            cache_service.set(cache_key, [], _resolve_ttl(settings.cache_ruleset_ttl_seconds))
        return []

    with open(RULESET_ADD_ON_ITEMS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])
    if settings.cache_enabled:
        cache_service.set(cache_key, items, _resolve_ttl(settings.cache_ruleset_ttl_seconds))
    return items


def load_package_resolution_map() -> dict:
    """Load package resolution map from JSON.

    Returns:
        Package resolution map dict
    """
    cache_key = _cache_key_for_path("ruleset_package_map", PACKAGE_RESOLUTION_PATH)
    if settings.cache_enabled:
        hit, cached = cache_service.get(cache_key)
        if hit:
            return cached
    if not PACKAGE_RESOLUTION_PATH.exists():
        logger.error(f"Package resolution map not found: {PACKAGE_RESOLUTION_PATH}")
        if settings.cache_enabled:
            cache_service.set(cache_key, {}, _resolve_ttl(settings.cache_ruleset_ttl_seconds))
        return {}

    with open(PACKAGE_RESOLUTION_PATH, encoding="utf-8") as f:
        package_map = json.load(f)
    if settings.cache_enabled:
        cache_service.set(cache_key, package_map, _resolve_ttl(settings.cache_ruleset_ttl_seconds))
    return package_map


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


def load_timeline_sample() -> dict | None:
    if not TIMELINE_SAMPLE_PATH.exists():
        return None
    with open(TIMELINE_SAMPLE_PATH, encoding="utf-8") as f:
        return json.load(f)


DIAGNOSIS_TERMINOLOGY = {
    "dyslipidemia": {"icd10_code": "E78.5", "snomed_code": "13644009"},
    "hyperlipidaemia / dyslipidaemia": {"icd10_code": "E78.5", "snomed_code": "13644009"},
    "pre-diabetes": {"icd10_code": "R73.03", "snomed_code": "714628002"},
    "prediabetes": {"icd10_code": "R73.03", "snomed_code": "714628002"},
    "essential hypertension": {"icd10_code": "I10", "snomed_code": "59621000"},
    "hypertension": {"icd10_code": "I10", "snomed_code": "59621000"},
    "diabetes mellitus type 2": {"icd10_code": "E11.9", "snomed_code": "44054006"},
    "type 2 diabetes mellitus": {"icd10_code": "E11.9", "snomed_code": "44054006"},
    "chronic kidney disease": {"icd10_code": "N18.9", "snomed_code": "709044004"},
    "gout": {"icd10_code": "M10.9", "snomed_code": "90560007"},
}

SCREENING_TERMINOLOGY = {
    "colonoscopy": {"cpt_code": "45378", "snomed_code": "73761001"},
    "mammogram": {"cpt_code": "77067", "snomed_code": "71651007"},
    "pap_smear": {"cpt_code": "88175", "snomed_code": "171149006"},
    "fit_test": {"cpt_code": "82274", "snomed_code": "252437004"},
    "ldct": {"cpt_code": "71271", "snomed_code": "169069000"},
}


def _resolve_diagnosis_codes(tag: dict) -> tuple[str, str]:
    icd10_code = str(tag.get("icd10_code", "") or "")
    snomed_code = str(tag.get("snomed_code", "") or "")
    if icd10_code or snomed_code:
        return icd10_code, snomed_code
    lookup_keys = [
        str(tag.get("tag", "")).strip().lower(),
        str(tag.get("label", "")).strip().lower(),
    ]
    for key in lookup_keys:
        if not key:
            continue
        matched = DIAGNOSIS_TERMINOLOGY.get(key)
        if matched:
            return matched.get("icd10_code", ""), matched.get("snomed_code", "")
    return "", ""


def _resolve_screening_codes(gap: dict) -> tuple[str, str]:
    cpt_code = str(gap.get("cpt_code", "") or "")
    snomed_code = str(gap.get("snomed_code", "") or "")
    if cpt_code or snomed_code:
        return cpt_code, snomed_code
    key = str(gap.get("screening_id", "")).strip().lower()
    matched = SCREENING_TERMINOLOGY.get(key)
    if matched:
        return matched.get("cpt_code", ""), matched.get("snomed_code", "")
    return "", ""


def build_timeline_from_signal_store(record: dict, patient_token: str) -> dict:
    clinical_signals = record.get("clinical_signals", {})
    biomarker_trends = record.get("biomarker_trends", {})
    computed_at = record.get("computed_at", get_current_timestamp())
    pipeline_run_id = record.get("pipeline_run_id", "")
    dates: list[str] = []
    diagnoses = []
    for i, tag in enumerate(clinical_signals.get("comorbidity_tags", []), start=1):
        onset_year = tag.get("onset_year")
        if onset_year:
            date = f"{int(onset_year)}-01-01"
            dates.append(date)
        else:
            date = computed_at[:10]
            dates.append(date)
        icd10_code, snomed_code = _resolve_diagnosis_codes(tag)
        diagnoses.append(
            {
                "event_id": f"dx-{i:03d}",
                "date": date,
                "onset_year": onset_year or int(date[:4]),
                "onset_type": "chronic",
                "icd10_code": icd10_code,
                "snomed_code": snomed_code,
                "label": tag.get("label", tag.get("tag", "Condition")),
                "clinical_status": "active",
                "fhir_condition_id": "",
            }
        )
    significant_lab_events = []
    lab_counter = 1
    for lab in biomarker_trends.get("labs", []):
        history = lab.get("history", [])
        if not history:
            continue
        latest = history[-1]
        date = latest.get("date", computed_at[:10])
        dates.append(date)
        significant_lab_events.append(
            {
                "event_id": f"lab-{lab_counter:03d}",
                "date": date,
                "loinc_code": lab.get("loinc_code", ""),
                "label": lab.get("label", ""),
                "value": latest.get("value", lab.get("current_value")),
                "unit": lab.get("unit", ""),
                "interpretation": lab.get("interpretation", ""),
                "interpretation_label": lab.get("category", ""),
                "threshold_crossed": "",
                "normal_range": "",
            }
        )
        lab_counter += 1
    screening_procedure_history = []
    for i, gap in enumerate(clinical_signals.get("screening_gaps", []), start=1):
        performed = gap.get("last_performed_date")
        if not performed:
            continue
        dates.append(performed)
        cpt_code, snomed_code = _resolve_screening_codes(gap)
        screening_procedure_history.append(
            {
                "event_id": f"proc-{i:03d}",
                "date": performed,
                "days_ago": gap.get("overdue_days") or 0,
                "procedure_code": gap.get("screening_id", ""),
                "cpt_code": cpt_code,
                "snomed_code": snomed_code,
                "label": gap.get("label", ""),
                "status": "completed",
                "result_summary": "Completed",
                "fhir_procedure_id": "",
            }
        )
    earliest = min(dates) if dates else computed_at[:10]
    latest = max(dates) if dates else computed_at[:10]
    total_years_covered = round((int(latest[:4]) - int(earliest[:4])) + 1, 1)
    return {
        "patient_token": patient_token,
        "timeline_span": {
            "earliest_event_date": earliest,
            "latest_event_date": latest,
            "total_years_covered": total_years_covered,
        },
        "diagnoses": diagnoses,
        "hospitalizations": [],
        "significant_lab_events": significant_lab_events,
        "screening_procedure_history": screening_procedure_history,
        "medication_changes": [],
        "pipeline_run_id": pipeline_run_id,
        "computed_at": computed_at,
    }

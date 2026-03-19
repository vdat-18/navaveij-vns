import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SIGNAL_STORE_DIR = BASE_DIR / "assets/synthesis/generated"
RULESET_TIER_CONFIG_PATH = BASE_DIR / "assets/synthesis/rulesets/sample_ruleset_tier_config.json"
RULESET_ADD_ON_ITEMS_PATH = BASE_DIR / "assets/synthesis/rulesets/sample_add_on_items.json"
PACKAGE_RESOLUTION_PATH = BASE_DIR / "assets/synthesis/rulesets/sample_package_resolution.json"


def load_signal_store_record(patient_id: str) -> dict | None:
    """Loads Signal Store record by ID."""
    if not SIGNAL_STORE_DIR.exists():
        return None
    for path in SIGNAL_STORE_DIR.glob("**/record_*.json"):
        try:
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
                actual = rec.get("patient_id") or rec.get("hard_constraints", {}).get("patient_id")
                if actual == patient_id:
                    return rec
        except Exception:
            continue
    return None


def extract_hard_constraints(record: dict) -> dict:
    """Extracts hard constraints."""
    return record.get("hard_constraints", {})


def extract_clinical_signals(record: dict) -> dict:
    """Extracts clinical signals."""
    return record.get("clinical_signals", {})


def extract_biomarker_trends(record: dict) -> dict:
    """Extracts biomarker trends."""
    return record.get("biomarker_trends", {})


def load_ruleset_tier_config() -> dict:
    """Loads tier rules."""
    if not RULESET_TIER_CONFIG_PATH.exists():
        return {"tier_selection_rules": []}
    with open(RULESET_TIER_CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_ruleset_add_on_items() -> list[dict]:
    """Loads add-ons."""
    if not RULESET_ADD_ON_ITEMS_PATH.exists():
        return []
    with open(RULESET_ADD_ON_ITEMS_PATH, encoding="utf-8") as f:
        return json.load(f).get("items", [])


def load_package_resolution_map() -> dict:
    """Loads package map."""
    if not PACKAGE_RESOLUTION_PATH.exists():
        return {}
    with open(PACKAGE_RESOLUTION_PATH, encoding="utf-8") as f:
        return json.load(f)


def filter_add_ons_by_demographics(items: list[dict], gender: str, age: int) -> tuple[list[dict], list[dict]]:
    """Filters add-ons by gender/age."""
    filt, excl = [], []
    for i in items:
        if i.get("status") != "active":
            continue
        gc, amin, amax = i.get("gender_constraint"), i.get("age_min"), i.get("age_max")
        if gc and gc != gender:
            excl.append({"item_code": i.get("item_code"), "exclusion_reason": "gender_mismatch"})
            continue
        if (amin is not None and age < amin) or (amax is not None and age > amax):
            excl.append({"item_code": i.get("item_code"), "exclusion_reason": "age_mismatch"})
            continue
        filt.append(i)
    return filt, excl


def resolve_package(tier: str, gender: str, age: int, pkg_map: dict) -> dict | None:
    """Resolves package by tier/gender/age."""
    g_map = pkg_map.get(tier, {}).get(gender, {})
    band = None
    if "age_any" in g_map:
        band = "age_any"
    else:
        for k in g_map.keys():
            try:
                if "_to_" in k:
                    parts = k.split("_")
                    if int(parts[1]) <= age <= int(parts[3]):
                        band = k
                        break
                elif "_plus" in k and age >= int(k.split("_")[1]):
                    band = k
                    break
            except (ValueError, IndexError):
                continue
    if not band:
        band = next(iter(g_map.keys()), None)
    if not band:
        return None
    info = g_map.get(band, {})
    return {
        "tier": tier,
        "gender": gender,
        "age": age,
        "age_band": band,
        "package_name": info.get("package_name"),
        "package_code": info.get("package_code"),
        "price_thb": info.get("price_thb"),
    }


def get_current_timestamp() -> str:
    """Gets UTC timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

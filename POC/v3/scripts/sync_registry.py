import os
import json
from pathlib import Path
from loguru import logger

# Paths
SIGNAL_STORE_DIR = Path("assets/synthesis/generated")
REGISTRY_PATH = Path("assets/patient_registry.json")

# Simple mapping for display names based on scenario folder
SCENARIO_NAMES = {
    "HealthyRoutineCheckup": "Healthy Routine Checkup",
    "UncontrolledHypertension": "Uncontrolled Hypertension",
    "MetabolicSyndromeRisk": "Metabolic Syndrome Risk",
    "SeniorCancerScreeningGap": "Senior Cancer Screening Gap",
    "EarlyOnsetDiabetes": "Early Onset Diabetes",
    "ChronicKidneyDiseaseProgression": "CKD Progression",
    "Test": "Diagnostic Test"
}

# Real-sounding names to inject
THAI_FIRST_NAMES = ["Ananda", "Boon-Mee", "Chaiyo", "Darika", "Erawan", "Fai", "Ganya", "Hathai", "Iara", "Jarat"]
THAI_LAST_NAMES = ["Siriwat", "Prasert", "Wichai", "Silpa", "Kiat", "Ratana", "Charoen", "Suk", "Vongs", "Thong"]

def get_random_name(index):
    """Deterministic selection of a name based on an index."""
    first = THAI_FIRST_NAMES[index % len(THAI_FIRST_NAMES)]
    last = THAI_LAST_NAMES[(index // len(THAI_FIRST_NAMES)) % len(THAI_LAST_NAMES)]
    return f"{first} {last}"

def sync_registry():
    """Scan all generated data, inject names into JSONs if missing, and update the registry."""
    logger.info("Scanning and injecting patient names...")
    
    if not SIGNAL_STORE_DIR.exists():
        logger.error(f"Data directory not found: {SIGNAL_STORE_DIR}")
        return

    # Load existing registry
    existing_registry = []
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            existing_registry = json.load(f)
    
    token_to_name = {p["patient_token"]: p["patient_name"] for p in existing_registry if "patient_token" in p}
    
    new_registry = []
    found_tokens = set()
    files = list(SIGNAL_STORE_DIR.glob("**/record_*.json"))
    files.sort() # Stable order

    for i, file_path in enumerate(files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                record = json.load(f)
                
            token = record.get("patient_token")
            # In your schema, patient_id is inside hard_constraints
            hard_constraints = record.get("hard_constraints", {})
            patient_id = hard_constraints.get("patient_id") or record.get("patient_id")
            demographics = hard_constraints.setdefault("patient_demographics", {})
            
            if not token:
                logger.warning(f"No patient_token found in {file_path}")
                continue
                
            if token in found_tokens:
                continue
                
            found_tokens.add(token)
            
            # Determine ID and Name
            token = record.get("patient_token") or f"tok_{i:03d}"
            patient_id = record.get("patient_id") or record.get("hard_constraints", {}).get("patient_id") or f"id_{token[-8:]}"
            
            scenario_folder = file_path.parent.name
            scenario_label = SCENARIO_NAMES.get(scenario_folder, scenario_folder)
            
            # Priority 1: Hardcoded / Known names
            if token == "tok_hmac_965c8137": name = "Somchai Wichai"
            elif token == "tok_hmac_1aa1b504": name = "Kanya Prasert"
            elif token == "tok_hmac_24d93799": name = "Wichai Silpa"
            else:
                name = get_random_name(i)
                
            # Inject/Update ID and Name in JSON
            record["patient_id"] = patient_id
            hard_constraints = record.setdefault("hard_constraints", {})
            hard_constraints["patient_id"] = patient_id
            demographics = hard_constraints.setdefault("patient_demographics", {})
            demographics["name"] = name
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)
            logger.debug(f"Injected ID '{patient_id}' and name '{name}' into {file_path}")
            
            display_name = f"{name} ({scenario_label})"
            
            new_registry.append({
                "patient_id": patient_id,
                "patient_name": display_name,
                "patient_token": token
            })
            logger.info(f"Registered patient: {display_name} [{patient_id}]")
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

    # Write back to registry
    if new_registry:
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(new_registry, f, indent=4, ensure_ascii=False)
        logger.success(f"Registry updated with {len(new_registry)} patients.")
    else:
        logger.warning("No new patients found to register.")

if __name__ == "__main__":
    sync_registry()

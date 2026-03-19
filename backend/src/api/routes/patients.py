import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from loguru import logger

from src.mcp_server.utils import load_signal_store_record

router = APIRouter()
REGISTRY_PATH = Path("assets/patient_registry.json")


def load_registry():
    """Loads patient registry."""
    if not REGISTRY_PATH.exists():
        return []
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


@router.get("/")
async def list_patients():
    """Lists registered patients."""
    try:
        return load_registry()
    except Exception as e:
        logger.error(f"Registry load failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{patient_id}")
async def get_patient_details(patient_id: str):
    """Enriches patient details with demographics."""
    registry = load_registry()
    patient = next((p for p in registry if p["patient_id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    record = load_signal_store_record(patient_id)
    if record:
        demogs = record.get("hard_constraints", {}).get("patient_demographics", {})
        return {
            **patient,
            "patient_name": demogs.get("name") or patient["patient_name"],
            "age": demogs.get("age"),
            "gender": demogs.get("gender"),
            "ethnicity": demogs.get("ethnicity"),
            "birth_date": demogs.get("birth_date"),
            "phone": demogs.get("phone"),
            "email": demogs.get("email"),
            "address": demogs.get("address"),
            "mrn": demogs.get("mrn"),
        }
    return patient

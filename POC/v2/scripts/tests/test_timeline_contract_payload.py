import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    return {
        "X-Auth-User-Id": "usr-test-0001",
        "X-Auth-Role": "physician",
        "X-Auth-Scopes": "recommendation:read",
    }


def _sample_token() -> str:
    registry = json.loads(Path("assets/patient_registry.json").read_text(encoding="utf-8"))
    return registry[0]["patient_token"]


def _token_by_patient_id(patient_id: str) -> str:
    registry = json.loads(Path("assets/patient_registry.json").read_text(encoding="utf-8"))
    patient = next(item for item in registry if item["patient_id"] == patient_id)
    return patient["patient_token"]


def test_timeline_contract_has_required_sections():
    token = _sample_token()
    response = client.get(f"/api/timeline/{token}", headers=_auth_headers())
    assert response.status_code == 200
    payload = response.json()
    assert payload["patient_token"] == token
    for key in [
        "timeline_span",
        "diagnoses",
        "hospitalizations",
        "significant_lab_events",
        "screening_procedure_history",
        "medication_changes",
        "pipeline_run_id",
        "computed_at",
    ]:
        assert key in payload
    span = payload["timeline_span"]
    assert "earliest_event_date" in span
    assert "latest_event_date" in span


def test_timeline_contract_contains_terminology_fields():
    token = _token_by_patient_id("id_1a2b3c4d")
    response = client.get(f"/api/timeline/{token}", headers=_auth_headers())
    assert response.status_code == 200
    payload = response.json()

    diagnoses = payload["diagnoses"]
    assert len(diagnoses) > 0
    first_diagnosis = diagnoses[0]
    assert "icd10_code" in first_diagnosis
    assert "snomed_code" in first_diagnosis
    assert first_diagnosis["icd10_code"] or first_diagnosis["snomed_code"]

    lab_events = payload["significant_lab_events"]
    assert len(lab_events) > 0
    first_lab = lab_events[0]
    assert "loinc_code" in first_lab
    assert first_lab["loinc_code"]

    procedures = payload["screening_procedure_history"]
    assert len(procedures) > 0
    first_proc = procedures[0]
    assert "cpt_code" in first_proc
    assert "snomed_code" in first_proc
    assert first_proc["cpt_code"] or first_proc["snomed_code"]


def test_timeline_contract_invalid_token():
    response = client.get("/api/timeline/tok_hmac_not_found", headers=_auth_headers())
    assert response.status_code == 404

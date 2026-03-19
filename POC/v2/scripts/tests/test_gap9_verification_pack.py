import json
from pathlib import Path
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import contracts

client = TestClient(app)


def _auth_headers(role: str = "admin", scopes: str = "recommendation:read,monitoring:read") -> dict[str, str]:
    return {
        "X-Auth-User-Id": "usr-test-0001",
        "X-Auth-Role": role,
        "X-Auth-Scopes": scopes,
    }


def _first_patient_token() -> str:
    registry_path = Path("assets/patient_registry.json")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    return registry[0]["patient_token"]


def test_gap9_required_verification_modules_present():
    required = [
        "scripts/tests/test_api_contract_routes.py",
        "scripts/tests/test_security_rbac_contract.py",
        "scripts/tests/test_timeline_contract_payload.py",
        "scripts/tests/test_access_monitoring_contract.py",
        "scripts/tests/test_frontend_terminology_visibility.py",
        "scripts/tests/test_frontend_reliability_contract.py",
        "scripts/tests/test_end_to_end.py",
    ]
    for path in required:
        assert Path(path).exists()


def test_gap9_api_smoke_for_screen_contracts():
    token = _first_patient_token()
    contracts.get_program_ruleset = lambda _patient_token, patient_id=None: {
        "ruleset_version": "v2026.03.1",
        "rule_preliminary_tier": "Advanced",
        "resolved_package": {
            "tier": "Advanced",
            "package_name": "Platinum — Men",
            "package_code": "PLAT_M",
            "price_thb": 8700,
            "age_band": "age_35_plus",
            "gender": "male",
        },
        "add_on_library": [
            {
                "item_code": "A001",
                "label": "Sample Add-on",
                "category": "cardiac",
                "trigger_signals": ["signal_1"],
                "navavej_product": {
                    "product_name": "Product A",
                    "product_code": "PROD_A",
                    "price_thb": 1200,
                },
            }
        ],
    }
    contracts.orchestrator.generate_recommendation = AsyncMock(
        return_value={
            "ai_recommended_tier": "Advanced",
            "tier_deviation_justification": None,
            "reasoning_trace": "GAP-9 smoke",
            "add_ons": [{"item_code": "A001", "priority_level": "Yellow", "rationale": "Test rationale"}],
            "supporting_signals": ["signal_1"],
            "missing_signals": [],
            "communication_script": {
                "clinical_conclusion": "Clinical summary.",
                "health_summary": "Health summary.",
                "recommendation_explanation": "Recommendation explanation.",
                "add_on_highlights": ["Highlight"],
                "next_steps": "Next steps.",
            },
            "clinical_signals": {
                "rule_preliminary_tier": "Advanced",
                "applicable_signals": ["signal_1"],
                "signals_fired": ["signal_1"],
                "missing_signals": [],
                "risk_flags": [],
                "pipeline_run_id": "pipe_test_001",
            },
        }
    )

    recommend = client.post(
        "/api/recommend",
        json={"patient_token": token},
        headers=_auth_headers(scopes="recommendation:read"),
    )
    timeline = client.get(
        f"/api/timeline/{token}",
        headers=_auth_headers(scopes="recommendation:read"),
    )
    monitoring = client.get(
        "/api/monitoring-snapshot",
        headers=_auth_headers(role="admin", scopes="monitoring:read"),
    )
    assert recommend.status_code == 200
    assert timeline.status_code == 200
    assert monitoring.status_code == 200
    assert recommend.json()["metadata"]["patient_token"] == token
    assert timeline.json()["patient_token"] == token
    assert "snapshot_at" in monitoring.json()


def test_gap9_admin_aliases_and_mapping_contract_smoke():
    headers = _auth_headers(role="admin", scopes="monitoring:read")
    mapping_response = client.get("/api/admin/mapping-codes", headers=headers)
    assert client.get("/api/admin/monitoring/snapshot", headers=headers).status_code == 200
    assert client.get("/api/admin/audit-logs/search", headers=headers).status_code == 200
    assert client.get("/api/admin/anomaly-alerts", headers=headers).status_code == 200
    assert client.get("/api/admin/rbac", headers=headers).status_code == 200
    assert client.get("/api/admin/master-programs", headers=headers).status_code == 200
    assert mapping_response.status_code == 200
    systems = {entry["target_system"] for entry in mapping_response.json()["mappings"]}
    assert {"LOINC", "SNOMED_CT", "ICD10", "CPT"}.issubset(systems)

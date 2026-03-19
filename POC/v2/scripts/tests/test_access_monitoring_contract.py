import hashlib
import json

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def _auth_headers(role: str = "admin", scopes: str = "monitoring:read") -> dict[str, str]:
    return {
        "X-Auth-User-Id": "usr-test-0001",
        "X-Auth-Role": role,
        "X-Auth-Scopes": scopes,
    }


def _hash_from_entry(entry: dict) -> str:
    payload = {
        "prev_entry_hash": entry.get("prev_entry_hash"),
        "who": entry.get("who", {}),
        "when": entry.get("when", {}),
        "where": entry.get("where", {}),
        "what": entry.get("what", {}),
        "why": entry.get("why", {}),
        "retention_expiry": entry.get("retention_expiry"),
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def test_screen3_endpoints_allow_admin_and_dpo_roles():
    admin_headers = _auth_headers(role="admin")
    dpo_headers = _auth_headers(role="dpo")
    for endpoint in [
        "/api/monitoring-snapshot",
        "/api/anomaly-alerts",
        "/api/audit-logs",
        "/api/rbac",
        "/api/mapping-codes",
        "/api/master-programs",
    ]:
        assert client.get(endpoint, headers=admin_headers).status_code == 200
        assert client.get(endpoint, headers=dpo_headers).status_code == 200


def test_screen3_endpoints_reject_non_admin_roles():
    headers = _auth_headers(role="nurse")
    response = client.get("/api/monitoring-snapshot", headers=headers)
    assert response.status_code == 403


def test_screen3_endpoints_reject_missing_auth_context():
    response = client.get("/api/monitoring-snapshot")
    assert response.status_code == 401


def test_screen3_endpoints_reject_missing_scope():
    response = client.get("/api/monitoring-snapshot", headers=_auth_headers(role="admin", scopes="recommendation:read"))
    assert response.status_code == 403


def test_audit_entry_hash_matches_recomputed_value():
    response = client.get("/api/audit-logs", headers=_auth_headers(role="admin"))
    assert response.status_code == 200
    payload = response.json()
    assert "entries" in payload
    assert len(payload["entries"]) > 0
    entry = payload["entries"][0]
    recomputed = _hash_from_entry(entry)
    assert recomputed == entry["sha256_hash"]


def test_admin_alias_routes_exist():
    headers = _auth_headers(role="admin")
    assert client.get("/api/admin/monitoring/snapshot", headers=headers).status_code == 200
    assert client.get("/api/admin/audit-logs/search", headers=headers).status_code == 200
    assert client.get("/api/admin/anomaly-alerts", headers=headers).status_code == 200
    assert client.get("/api/admin/rbac", headers=headers).status_code == 200
    assert client.get("/api/admin/mapping-codes", headers=headers).status_code == 200
    assert client.get("/api/admin/master-programs", headers=headers).status_code == 200


def test_mapping_codes_include_core_terminology_systems():
    response = client.get("/api/mapping-codes", headers=_auth_headers(role="admin"))
    assert response.status_code == 200
    payload = response.json()
    systems = {entry["target_system"] for entry in payload["mappings"]}
    assert "LOINC" in systems
    assert "SNOMED_CT" in systems
    assert "ICD10" in systems
    assert "CPT" in systems

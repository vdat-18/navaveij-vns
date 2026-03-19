import json
from pathlib import Path
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import clinical, contracts

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


def _first_patient_id() -> str:
    registry_path = Path("assets/patient_registry.json")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    return registry[0]["patient_id"]


def test_recommend_contract_route_success():
    contracts.cache_service.clear()
    token = _first_patient_token()
    mock_result = {
        "ai_recommended_tier": "Advanced",
        "tier_deviation_justification": None,
        "reasoning_trace": "Contract route test trace",
        "add_ons": [{"item_code": "A001", "priority_level": "Yellow", "rationale": "Test rationale"}],
        "supporting_signals": ["signal_1"],
        "missing_signals": ["signal_missing_1"],
        "communication_script": {
            "clinical_conclusion": "Clinical summary.",
            "health_summary": "Health summary.",
            "recommendation_explanation": "Recommendation explanation.",
            "add_on_highlights": ["Highlight"],
            "next_steps": "Next steps.",
        },
        "clinical_signals": {
            "rule_preliminary_tier": "Advanced",
            "applicable_signals": ["signal_1", "signal_2"],
            "signals_fired": ["signal_1"],
            "missing_signals": ["signal_missing_1"],
            "risk_flags": [
                {
                    "flag_id": "signal_1",
                    "label": "High Risk Signal",
                    "severity": "High",
                    "guideline": "Test guideline",
                    "source_signals": ["signal_1"],
                }
            ],
            "pipeline_run_id": "pipe_test_001",
        },
        "recommendation_source": "AI",
        "review_required": False,
        "security_metadata": {
            "rehydration_map": {"tok_xxx": "Jane Doe"},
            "masked_ai_output": {"reasoning_trace": "masked"},
            "is_poc_demo": True,
        },
    }
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
    contracts.orchestrator.generate_recommendation = AsyncMock(return_value=mock_result)

    response = client.post("/api/recommend", json={"patient_token": token}, headers=_auth_headers(scopes="recommendation:read"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["reasoning_trace"] == "Contract route test trace"
    assert payload["rule_preliminary_tier"] == "Advanced"
    assert payload["resolved_package"]["package_code"] == "PLAT_M"
    assert payload["confidence_tier"] in {"High", "Medium", "Low"}
    assert payload["recommendation_source"] in {"AI", "RuleBased"}
    assert payload["review_required"] is False
    assert payload["communication_script"]["opening"] == "Clinical summary."
    assert payload["add_ons"][0]["label"] == "Sample Add-on"
    assert payload["security_metadata"]["rehydration_map"]["tok_xxx"] == "Jane Doe"
    assert payload["security_metadata"]["masked_ai_output"]["reasoning_trace"] == "masked"
    assert payload["metadata"]["patient_token"] == token
    assert "request_id" in payload["metadata"]
    assert payload["metadata"]["cache_status"] in {"miss", "hit"}


def test_recommend_contract_route_cache_hit_skips_second_llm_call():
    contracts.cache_service.clear()
    token = _first_patient_token()
    mock_result = {
        "ai_recommended_tier": "Advanced",
        "tier_deviation_justification": None,
        "reasoning_trace": "Cache route test trace",
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
            "pipeline_run_id": "pipe_cache_001",
        },
        "recommendation_source": "AI",
        "review_required": False,
        "security_metadata": {
            "rehydration_map": {"tok_cache": "Jane Doe"},
            "masked_ai_output": {"reasoning_trace": "masked-cache"},
            "is_poc_demo": True,
        },
    }
    contracts.get_clinical_signals = lambda _patient_token, patient_id=None: {
        "pipeline_run_id": "pipe_cache_001",
        "signals_fired": ["signal_1"],
        "missing_signals": [],
        "risk_flags": [],
    }
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
    contracts.orchestrator.generate_recommendation = AsyncMock(return_value=mock_result)

    first = client.post("/api/recommend", json={"patient_token": token}, headers=_auth_headers(scopes="recommendation:read"))
    second = client.post("/api/recommend", json={"patient_token": token}, headers=_auth_headers(scopes="recommendation:read"))

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["metadata"]["cache_status"] == "miss"
    assert second.json()["metadata"]["cache_status"] == "hit"
    assert contracts.orchestrator.generate_recommendation.await_count == 1


def test_recommend_contract_route_force_rule_based_passthrough_and_response_contract():
    contracts.cache_service.clear()
    token = _first_patient_token()
    mock_result = {
        "ai_recommended_tier": "Premium",
        "tier_deviation_justification": "Rule path selected by request",
        "reasoning_trace": "Rule path trace",
        "add_ons": [],
        "supporting_signals": ["signal_critical"],
        "missing_signals": [],
        "communication_script": {
            "clinical_conclusion": "Rule-based clinical summary.",
            "health_summary": "Rule-based health summary.",
            "recommendation_explanation": "Rule-based explanation.",
            "add_on_highlights": [],
            "next_steps": "Manual review required.",
        },
        "clinical_signals": {
            "rule_preliminary_tier": "Premium",
            "applicable_signals": ["signal_critical"],
            "signals_fired": ["signal_critical"],
            "missing_signals": [],
            "risk_flags": [],
            "pipeline_run_id": "pipe_rule_001",
        },
        "recommendation_source": "RuleBased",
        "review_required": True,
        "security_metadata": {
            "rehydration_map": {"tok_rule": "John Doe"},
            "masked_ai_output": {"reasoning_trace": "masked-rule"},
            "is_poc_demo": True,
        },
    }
    contracts.get_clinical_signals = lambda _patient_token, patient_id=None: {
        "pipeline_run_id": "pipe_rule_001",
        "signals_fired": ["signal_critical"],
        "missing_signals": [],
        "risk_flags": [],
    }
    contracts.get_program_ruleset = lambda _patient_token, patient_id=None: {
        "ruleset_version": "v2026.03.1",
        "rule_preliminary_tier": "Premium",
        "resolved_package": {
            "tier": "Premium",
            "package_name": "Diamond — Men",
            "package_code": "DIAMOND_M",
            "price_thb": 12500,
            "age_band": "age_35_plus",
            "gender": "male",
        },
        "add_on_library": [],
    }
    contracts.orchestrator.generate_recommendation = AsyncMock(return_value=mock_result)

    response = client.post(
        "/api/recommend",
        json={"patient_token": token, "force_rule_based": True},
        headers=_auth_headers(scopes="recommendation:read"),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendation_source"] == "RuleBased"
    assert payload["review_required"] is True
    assert payload["security_metadata"]["rehydration_map"]["tok_rule"] == "John Doe"
    assert payload["security_metadata"]["masked_ai_output"]["reasoning_trace"] == "masked-rule"
    contracts.orchestrator.generate_recommendation.assert_awaited_once_with(
        patient_id=_first_patient_id(),
        patient_token=token,
        force_rule_based=True,
    )


def test_recommend_contract_route_cache_partitioned_by_force_rule_based():
    contracts.cache_service.clear()
    token = _first_patient_token()

    ai_result = {
        "ai_recommended_tier": "Advanced",
        "tier_deviation_justification": None,
        "reasoning_trace": "AI path",
        "add_ons": [],
        "supporting_signals": ["signal_1"],
        "missing_signals": [],
        "communication_script": {
            "clinical_conclusion": "AI summary.",
            "health_summary": "AI health summary.",
            "recommendation_explanation": "AI explanation.",
            "add_on_highlights": [],
            "next_steps": "AI next step.",
        },
        "clinical_signals": {
            "rule_preliminary_tier": "Advanced",
            "applicable_signals": ["signal_1"],
            "signals_fired": ["signal_1"],
            "missing_signals": [],
            "risk_flags": [],
            "pipeline_run_id": "pipe_partition_001",
        },
        "recommendation_source": "AI",
        "review_required": False,
        "security_metadata": {
            "rehydration_map": {"tok_ai": "Alice"},
            "masked_ai_output": {"reasoning_trace": "masked-ai"},
            "is_poc_demo": True,
        },
    }
    rule_result = {
        **ai_result,
        "reasoning_trace": "Rule path",
        "recommendation_source": "RuleBased",
        "review_required": True,
        "security_metadata": {
            "rehydration_map": {"tok_rule": "Bob"},
            "masked_ai_output": {"reasoning_trace": "masked-rule"},
            "is_poc_demo": True,
        },
    }
    contracts.get_clinical_signals = lambda _patient_token, patient_id=None: {
        "pipeline_run_id": "pipe_partition_001",
        "signals_fired": ["signal_1"],
        "missing_signals": [],
        "risk_flags": [],
    }
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
        "add_on_library": [],
    }
    contracts.orchestrator.generate_recommendation = AsyncMock(side_effect=[ai_result, rule_result])

    ai_response = client.post(
        "/api/recommend",
        json={"patient_token": token, "force_rule_based": False},
        headers=_auth_headers(scopes="recommendation:read"),
    )
    rule_response = client.post(
        "/api/recommend",
        json={"patient_token": token, "force_rule_based": True},
        headers=_auth_headers(scopes="recommendation:read"),
    )
    rule_cached_response = client.post(
        "/api/recommend",
        json={"patient_token": token, "force_rule_based": True},
        headers=_auth_headers(scopes="recommendation:read"),
    )

    assert ai_response.status_code == 200
    assert rule_response.status_code == 200
    assert rule_cached_response.status_code == 200
    assert ai_response.json()["metadata"]["cache_status"] == "miss"
    assert rule_response.json()["metadata"]["cache_status"] == "miss"
    assert rule_cached_response.json()["metadata"]["cache_status"] == "hit"
    assert ai_response.json()["recommendation_source"] == "AI"
    assert rule_response.json()["recommendation_source"] == "RuleBased"
    assert contracts.orchestrator.generate_recommendation.await_count == 2


def test_recommend_contract_route_preserves_orchestrator_source_and_review_precedence():
    contracts.cache_service.clear()
    token = _first_patient_token()
    low_confidence_ai_result = {
        "ai_recommended_tier": "Advanced",
        "tier_deviation_justification": None,
        "reasoning_trace": "AI remains authoritative despite low computed confidence.",
        "add_ons": [],
        "supporting_signals": [],
        "missing_signals": ["signal_1", "signal_2", "signal_3"],
        "communication_script": {
            "clinical_conclusion": "AI summary.",
            "health_summary": "AI health summary.",
            "recommendation_explanation": "AI explanation.",
            "add_on_highlights": [],
            "next_steps": "AI next step.",
        },
        "clinical_signals": {
            "rule_preliminary_tier": "Advanced",
            "applicable_signals": [],
            "signals_fired": [],
            "missing_signals": ["signal_1", "signal_2", "signal_3"],
            "risk_flags": [],
            "pipeline_run_id": "pipe_precedence_001",
        },
        "recommendation_source": "AI",
        "review_required": False,
        "security_metadata": {
            "rehydration_map": {"tok_prec": "N/A"},
            "masked_ai_output": {"reasoning_trace": "masked-precedence"},
            "is_poc_demo": True,
        },
    }
    contracts.get_clinical_signals = lambda _patient_token, patient_id=None: {
        "pipeline_run_id": "pipe_precedence_001",
        "signals_fired": [],
        "missing_signals": ["signal_1", "signal_2", "signal_3"],
        "risk_flags": [],
    }
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
        "add_on_library": [],
    }
    contracts.orchestrator.generate_recommendation = AsyncMock(return_value=low_confidence_ai_result)

    response = client.post("/api/recommend", json={"patient_token": token}, headers=_auth_headers(scopes="recommendation:read"))
    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence_tier"] == "Low"
    assert payload["recommendation_source"] == "AI"
    assert payload["review_required"] is False


def test_recommend_contract_route_invalid_token():
    response = client.post(
        "/api/recommend",
        json={"patient_token": "tok_hmac_not_found"},
        headers=_auth_headers(scopes="recommendation:read"),
    )
    assert response.status_code == 404


def test_timeline_contract_route_exists():
    token = _first_patient_token()
    response = client.get(f"/api/timeline/{token}", headers=_auth_headers(scopes="recommendation:read"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["patient_token"] == token
    assert "timeline_span" in payload
    assert "diagnoses" in payload
    assert "hospitalizations" in payload
    assert "significant_lab_events" in payload
    assert "screening_procedure_history" in payload
    assert "medication_changes" in payload
    assert "pipeline_run_id" in payload
    assert "computed_at" in payload
    assert isinstance(payload["diagnoses"], list)
    assert isinstance(payload["significant_lab_events"], list)


def test_biomarker_trends_route_exists():
    token = _first_patient_token()
    response = client.get(f"/api/biomarker-trends/{token}", headers=_auth_headers(scopes="recommendation:read"))
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("patient_token") == token
    assert "bmi" in payload
    assert "blood_pressure" in payload
    assert "egfr" in payload
    assert "labs" in payload


def test_screening_gaps_route_exists():
    token = _first_patient_token()
    response = client.get(f"/api/screening-gaps/{token}", headers=_auth_headers(scopes="recommendation:read"))
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("patient_token") == token
    assert "screening_gaps" in payload
    assert "vaccination_gaps" in payload


def test_monitoring_snapshot_contract_route_exists():
    response = client.get("/api/monitoring-snapshot", headers=_auth_headers(role="admin", scopes="monitoring:read"))

    assert response.status_code == 200
    payload = response.json()
    assert "snapshot_at" in payload
    assert "active_users_now" in payload
    assert "sessions_today" in payload
    assert "patient_records_accessed_today" in payload
    assert "ai_recommendations_generated_today" in payload
    assert "alert_counts" in payload
    assert "safety_validator_failures_today" in payload


def test_audit_logs_contract_route_filters():
    response = client.get(
        "/api/audit-logs",
        params={"action_type": "View"},
        headers=_auth_headers(role="admin", scopes="monitoring:read"),
    )

    assert response.status_code == 200
    payload = response.json()
    assert "total" in payload
    assert "entries" in payload
    for entry in payload["entries"]:
        assert entry["what"]["action_type"] == "View"


def test_access_monitoring_support_routes_exist():
    monitoring_headers = _auth_headers(role="admin", scopes="monitoring:read")
    assert client.get("/api/anomaly-alerts", headers=monitoring_headers).status_code == 200
    assert client.get("/api/rbac", headers=monitoring_headers).status_code == 200
    mapping_response = client.get("/api/mapping-codes", headers=monitoring_headers)
    assert mapping_response.status_code == 200
    mapping_payload = mapping_response.json()
    assert "mappings" in mapping_payload
    assert len(mapping_payload["mappings"]) > 0
    first_mapping = mapping_payload["mappings"][0]
    for key in [
        "mapping_id",
        "local_system",
        "local_code",
        "target_system",
        "target_code",
        "target_label",
        "mapping_type",
        "status",
    ]:
        assert key in first_mapping
    assert client.get("/api/master-programs", headers=monitoring_headers).status_code == 200


def test_legacy_route_still_available():
    response = client.get("/api/v1/clinical/audit", headers=_auth_headers(scopes="recommendation:read"))
    assert response.status_code == 200


def test_legacy_recommend_adapter_path_uses_id_input():
    patient_id = _first_patient_id()
    clinical.orchestrator.generate_recommendation = AsyncMock(
        return_value={"recommendation_hash": "hash_1", "ai_recommended_tier": "Advanced"}
    )
    response = client.post(
        "/api/v1/clinical/recommend",
        json={"patient_id": patient_id},
        headers=_auth_headers(scopes="recommendation:read"),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ai_recommended_tier"] == "Advanced"

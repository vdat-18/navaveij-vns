import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.security import AuthContext, parse_roles, require_access
from src.api.routes.patients import find_patient_by_token, load_registry
from src.mcp_server.tools.biomarker_trends import get_biomarker_trends
from src.mcp_server.tools.clinical_signals import get_clinical_signals
from src.mcp_server.tools.patient_event_timeline import get_patient_event_timeline
from src.mcp_server.tools.program_ruleset import get_program_ruleset
from src.services.cache import cache_service
from src.services.orchestrator import OrchestrationManager
from shared.settings import settings

router = APIRouter()
orchestrator = OrchestrationManager()


class RecommendRequest(BaseModel):
    patient_token: str
    force_rule_based: bool = False


class RecommendResponse(BaseModel):
    ai_recommended_tier: str
    tier_deviation_justification: str | None
    add_ons: list[dict[str, Any]]
    reasoning_trace: str
    supporting_signals: list[str]
    missing_signals: list[str]
    communication_script: dict[str, Any]
    rule_preliminary_tier: str
    resolved_package: dict[str, Any]
    confidence_score: float
    confidence_tier: str
    review_required: bool
    recommendation_source: str
    recommendation_hash: str | None = None
    patient_high_alert: dict[str, Any]
    security_metadata: dict[str, Any]
    metadata: dict[str, Any]


class TimelineResponse(BaseModel):
    patient_token: str
    timeline_span: dict[str, Any]
    diagnoses: list[dict[str, Any]]
    hospitalizations: list[dict[str, Any]]
    significant_lab_events: list[dict[str, Any]]
    screening_procedure_history: list[dict[str, Any]]
    medication_changes: list[dict[str, Any]]
    pipeline_run_id: str
    computed_at: str


class MonitoringSnapshotResponse(BaseModel):
    snapshot_at: str
    refresh_interval_seconds: int
    active_users_now: int
    sessions_today: int
    patient_records_accessed_today: int
    ai_recommendations_generated_today: int
    alert_counts: dict[str, int]
    safety_validator_failures_today: int
    top_active_departments: list[dict[str, Any]]


class AuditLogsResponse(BaseModel):
    total: int
    entries: list[dict[str, Any]]


class AnomalyAlertsResponse(BaseModel):
    alerts: list[dict[str, Any]]


class RbacResponse(BaseModel):
    roles: list[dict[str, Any]]


class MappingCodesResponse(BaseModel):
    mappings: list[dict[str, Any]]


class MasterProgramsResponse(BaseModel):
    programs: list[dict[str, Any]]


MONITORING_FIXTURE_PATH = Path(__file__).resolve().parents[4] / "assets" / "monitoring.json"
MONITORING_ALLOWED_ROLES = parse_roles(settings.monitoring_allowed_roles)
RECOMMENDATION_ALLOWED_ROLES = parse_roles(settings.recommendation_allowed_roles)


def _resolve_patient_by_token(patient_token: str) -> dict[str, Any]:
    patient = find_patient_by_token(patient_token)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient token not found")
    return patient


def _patient_token_map() -> dict[str, str]:
    return {item.get("patient_id"): item.get("patient_token") for item in load_registry()}


def _read_audit_logs() -> list[dict[str, Any]]:
    return orchestrator.audit_logger.get_logs()


def _load_monitoring_fixture() -> dict[str, Any]:
    if MONITORING_FIXTURE_PATH.exists():
        with open(MONITORING_FIXTURE_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "snapshot": {
            "snapshot_at": "",
            "refresh_interval_seconds": 30,
            "active_users_now": 0,
            "sessions_today": 0,
            "patient_records_accessed_today": 0,
            "ai_recommendations_generated_today": 0,
            "alert_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "safety_validator_failures_today": 0,
            "top_active_departments": [],
        },
        "anomaly_alerts": [],
        "rbac_roles": [],
        "mapping_codes": [],
        "master_programs": [],
    }


MONITORING_FIXTURE = _load_monitoring_fixture()
require_monitoring_access = require_access(
    allowed_roles=MONITORING_ALLOWED_ROLES,
    required_scopes={scope.strip().lower() for scope in settings.monitoring_required_scopes.split(",") if scope.strip()},
)
require_recommendation_access = require_access(
    allowed_roles=RECOMMENDATION_ALLOWED_ROLES,
    required_scopes={scope.strip().lower() for scope in settings.recommendation_required_scopes.split(",") if scope.strip()},
)


def _to_ict_timestamp(utc_value: str) -> str:
    if not utc_value:
        return ""
    try:
        dt = datetime.fromisoformat(utc_value.replace("Z", "+00:00"))
    except ValueError:
        return utc_value
    local = dt.astimezone(timezone.utc).astimezone()
    return local.isoformat()


def _stable_hash_payload(entry: dict[str, Any]) -> str:
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


def _normalize_runtime_audit_entries() -> list[dict[str, Any]]:
    token_by_patient_id = _patient_token_map()
    normalized: list[dict[str, Any]] = []
    previous_hash = "0" * 64
    for index, entry in enumerate(_read_audit_logs(), start=1):
        who = entry.get("who", {})
        what = entry.get("what", {})
        why = entry.get("why", {})
        timestamp = entry.get("timestamp", "")
        patient_id = who.get("patient_id")
        patient_token = token_by_patient_id.get(patient_id)
        patient_token_masked = None
        if patient_token:
            patient_token_masked = f"{patient_token[:12]}****{patient_token[-2:]}"
        action_type = what.get("event", "Generate")
        if action_type == "PROVISIONING_DECISION":
            action_type = "Decision"
        record = {
            "entry_id": f"alog-runtime-{index:06d}",
            "prev_entry_hash": entry.get("previous_hash") or previous_hash,
            "who": {
                "user_id": who.get("physician_id") or "usr-clinician-001",
                "user_display_name": "POC Clinician",
                "user_role": "physician",
                "department": "Health Checkup Center",
            },
            "when": {
                "iso_timestamp_utc": timestamp,
                "local_timestamp_ict": _to_ict_timestamp(timestamp),
            },
            "where": {
                "service_id": "recommendation-dashboard-ui",
                "source_ip_hash": "sha256_source_ip_runtime",
                "request_id": f"req-runtime-{index:06d}",
                "user_agent_class": "web_browser",
            },
            "what": {
                "action_type": action_type,
                "resource_type": what.get("resource_type", "RecommendationOutput"),
                "patient_token": patient_token,
                "patient_token_masked": patient_token_masked,
                "model_id": entry.get("how", {}).get("model_id"),
                "template_version": "poc-v2",
                "latency_ms": None,
                "safety_validator_result": "pass",
                "recommendation_source": "AI",
            },
            "why": {
                "request_context": why.get("reasoning_trace") or why.get("notes") or "Runtime clinical action",
                "indication_code": why.get("decision") or action_type,
            },
            "retention_expiry": "2029-12-31",
            "raw": entry,
        }
        record["sha256_hash"] = _stable_hash_payload(record)
        previous_hash = record["sha256_hash"]
        normalized.append(record)
    return normalized


def _audit_dataset() -> list[dict[str, Any]]:
    runtime = _normalize_runtime_audit_entries()
    if runtime:
        return runtime
    fixture_logs = MONITORING_FIXTURE.get("audit_logs", [])
    normalized = []
    previous_hash = "0" * 64
    for item in fixture_logs:
        record = dict(item)
        record["prev_entry_hash"] = record.get("prev_entry_hash") or previous_hash
        record["sha256_hash"] = _stable_hash_payload(record)
        previous_hash = record["sha256_hash"]
        normalized.append(record)
    return normalized


def _filter_audit_entries(
    *,
    user_id: str | None,
    patient_token_prefix: str | None,
    action_type: str | None,
    resource_type: str | None,
    start_date: str | None,
    end_date: str | None,
) -> list[dict[str, Any]]:
    logs = _audit_dataset()
    results: list[dict[str, Any]] = []
    for entry in logs:
        who = entry.get("who", {})
        what = entry.get("what", {})
        when = entry.get("when", {})
        timestamp = when.get("iso_timestamp_utc", "")
        if user_id and who.get("user_id") != user_id:
            continue
        if patient_token_prefix:
            token = what.get("patient_token") or ""
            if not token.startswith(patient_token_prefix):
                continue
        if action_type and what.get("action_type") != action_type:
            continue
        if resource_type and what.get("resource_type") != resource_type:
            continue
        if start_date and timestamp < start_date:
            continue
        if end_date and timestamp > end_date:
            continue
        results.append(entry)
    return results


def _map_communication_script(script: dict[str, Any]) -> dict[str, Any]:
    opening = script.get("opening") or script.get("clinical_conclusion") or "Clinical recommendation summary."
    return {
        "opening": opening,
        "health_summary": script.get("health_summary", ""),
        "recommendation_explanation": script.get("recommendation_explanation", ""),
        "add_on_highlights": script.get("add_on_highlights", []),
        "next_steps": script.get("next_steps", ""),
    }


def _build_missing_data_alerts(missing_signals: list[str]) -> list[dict[str, str]]:
    return [
        {
            "signal_id": signal_id,
            "label": signal_id.replace("_", " ").title(),
            "recommendation_impact": "Signal input is missing and may reduce recommendation precision.",
        }
        for signal_id in missing_signals
    ]


def _build_critical_signals(clinical_signals: dict[str, Any]) -> list[dict[str, str]]:
    critical = []
    for flag in clinical_signals.get("risk_flags", []):
        severity = flag.get("severity", "")
        if severity not in {"High", "Critical"}:
            continue
        sources = ", ".join(flag.get("source_signals", []))
        critical.append(
            {
                "signal_id": flag.get("flag_id", ""),
                "label": flag.get("label", ""),
                "severity": severity,
                "clinical_note": f'{flag.get("guideline", "")} | source_signals: {sources}',
            }
        )
    return critical


def _normalize_mapping_codes(raw_mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for index, mapping in enumerate(raw_mappings, start=1):
        local_code = mapping.get("local_code", "")
        local_system = mapping.get("local_system", "")
        target_system = mapping.get("target_system") or mapping.get("standard_system", "")
        target_code = mapping.get("target_code") or mapping.get("standard_code", "")
        target_label = mapping.get("target_label") or mapping.get("display", "")
        item = {
            "mapping_id": mapping.get("mapping_id") or f"map-{index:04d}",
            "local_system": local_system,
            "local_code": local_code,
            "local_label": mapping.get("local_label") or mapping.get("display", local_code),
            "target_system": target_system,
            "target_code": target_code,
            "target_label": target_label,
            "mapping_type": mapping.get("mapping_type", "exact"),
            "status": mapping.get("status", "active"),
            "validated_by_user_id": mapping.get("validated_by_user_id", ""),
            "validated_at": mapping.get("validated_at", ""),
            "last_updated_by_user_id": mapping.get("last_updated_by_user_id", ""),
            "last_updated_at": mapping.get("last_updated_at", ""),
            "notes": mapping.get("notes", ""),
            "standard_system": mapping.get("standard_system", target_system),
            "standard_code": mapping.get("standard_code", target_code),
            "display": mapping.get("display", target_label),
        }
        normalized.append(item)
    return normalized


def _confidence_tier(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.50:
        return "Medium"
    return "Low"


def _normalize_stage2(
    *,
    patient_token: str,
    ai_output: dict[str, Any],
    ruleset: dict[str, Any],
    latency_ms: int,
) -> dict[str, Any]:
    clinical_signals = ai_output.get("clinical_signals", {})
    signals_fired = set(clinical_signals.get("signals_fired", []))
    missing_signals = ai_output.get("missing_signals", [])
    applicable_signals = clinical_signals.get("applicable_signals", [])
    rule_preliminary_tier = ruleset.get(
        "rule_preliminary_tier",
        clinical_signals.get("rule_preliminary_tier", "Standard"),
    )
    ai_tier = ai_output.get("ai_recommended_tier", "Standard")

    addon_map = {item.get("item_code"): item for item in ruleset.get("add_on_library", [])}
    enriched_add_ons = []
    for item in ai_output.get("add_ons", []):
        item_code = item.get("item_code", "")
        meta = addon_map.get(item_code, {})
        trigger_signals = meta.get("trigger_signals", [])
        enriched_add_ons.append(
            {
                "item_code": item_code,
                "priority_level": item.get("priority_level", "Yellow"),
                "rationale": item.get("rationale", ""),
                "label": meta.get("label", item_code),
                "category": meta.get("category", "other"),
                "navavej_product": meta.get(
                    "navavej_product",
                    {
                        "product_name": "",
                        "product_code": "",
                        "price_thb": None,
                    },
                ),
                "trigger_signals_matched": [s for s in trigger_signals if s in signals_fired],
            }
        )

    applicable_count = len(applicable_signals) or 1
    signal_coverage = min(len(signals_fired) / applicable_count, 1.0)
    total_signal_count = len(signals_fired) + len(missing_signals) or 1
    data_completeness = len(signals_fired) / total_signal_count
    rule_agreement = 1.0 if ai_tier == rule_preliminary_tier else 0.7
    confidence_score = round(0.4 * signal_coverage + 0.4 * data_completeness + 0.2 * rule_agreement, 3)
    confidence_tier = _confidence_tier(confidence_score)
    review_required = ai_output.get("review_required")
    if review_required is None:
        review_required = confidence_score < 0.50
    recommendation_source = ai_output.get("recommendation_source")
    if not recommendation_source:
        recommendation_source = "RuleBased" if review_required else "AI"

    critical_signals = _build_critical_signals(clinical_signals)
    missing_data_alerts = _build_missing_data_alerts(missing_signals)

    resolved_package = ruleset.get("resolved_package", {}) or {}
    resolved_package = {
        "tier": resolved_package.get("tier", ai_tier),
        "package_name": resolved_package.get("package_name", ""),
        "package_code": resolved_package.get("package_code", ""),
        "price_thb": resolved_package.get("price_thb"),
        "age_band": resolved_package.get("age_band", ""),
        "gender": resolved_package.get("gender", ""),
    }

    return {
        "ai_recommended_tier": ai_tier,
        "tier_deviation_justification": ai_output.get("tier_deviation_justification"),
        "add_ons": enriched_add_ons,
        "reasoning_trace": ai_output.get("reasoning_trace", ""),
        "supporting_signals": ai_output.get("supporting_signals", []),
        "missing_signals": missing_signals,
        "communication_script": _map_communication_script(ai_output.get("communication_script", {})),
        "rule_preliminary_tier": rule_preliminary_tier,
        "resolved_package": resolved_package,
        "confidence_score": confidence_score,
        "confidence_tier": confidence_tier,
        "review_required": review_required,
        "recommendation_source": recommendation_source,
        "recommendation_hash": ai_output.get("recommendation_hash"),
        "patient_high_alert": {
            "critical_signals": critical_signals,
            "missing_data_alerts": missing_data_alerts,
        },
        "security_metadata": ai_output.get("security_metadata", {}),
        "metadata": {
            "request_id": f"req_{uuid.uuid4().hex[:12]}",
            "patient_token": patient_token,
            "model_id": settings.llm_model,
            "template_version": "poc-v2-stage2-v1",
            "ruleset_version": ruleset.get("ruleset_version", "v2026.03.1"),
            "signal_store_pipeline_run_id": clinical_signals.get("pipeline_run_id", ""),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "latency_ms": latency_ms,
        },
    }


def _recommendation_cache_key(
    *,
    patient_token: str,
    signal_store_pipeline_run_id: str,
    ruleset_version: str,
    force_rule_based: bool,
) -> str:
    raw = json.dumps(
        {
            "patient_token": patient_token,
            "signal_store_pipeline_run_id": signal_store_pipeline_run_id,
            "ruleset_version": ruleset_version,
            "force_rule_based": force_rule_based,
            "model_id": settings.llm_model,
            "template_version": "poc-v2-stage2-v1",
            "api_auth_mode": settings.api_auth_mode,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"recommendation:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest, _auth: AuthContext = Depends(require_recommendation_access)):
    patient = _resolve_patient_by_token(request.patient_token)
    patient_id = patient["patient_id"]
    signals = get_clinical_signals(request.patient_token, patient_id=patient_id)
    pipeline_run_id = signals.get("pipeline_run_id", "")
    ruleset = get_program_ruleset(request.patient_token, patient_id=patient_id)
    cache_key = _recommendation_cache_key(
        patient_token=request.patient_token,
        signal_store_pipeline_run_id=pipeline_run_id,
        ruleset_version=ruleset.get("ruleset_version", "v2026.03.1"),
        force_rule_based=request.force_rule_based,
    )
    cache_ttl = settings.cache_recommendation_ttl_seconds or settings.cache_ttl_seconds
    cache_key_hash = cache_key.split(":", 1)[-1][:16]
    if settings.cache_enabled:
        hit, cached_payload = cache_service.get(cache_key)
        if hit:
            payload = json.loads(json.dumps(cached_payload))
            metadata = payload.get("metadata", {})
            metadata["request_id"] = f"req_{uuid.uuid4().hex[:12]}"
            metadata["generated_at"] = datetime.now(timezone.utc).isoformat()
            metadata["latency_ms"] = 0
            metadata["cache_status"] = "hit"
            metadata["cache_key_hash"] = cache_key_hash
            metadata["cache_ttl_seconds"] = cache_ttl
            payload["metadata"] = metadata
            return payload
    started_at = time.time()
    ai_output = await orchestrator.generate_recommendation(
        patient_id=patient_id,
        patient_token=request.patient_token,
        force_rule_based=request.force_rule_based,
    )
    latency_ms = int((time.time() - started_at) * 1000)
    payload = _normalize_stage2(
        patient_token=request.patient_token,
        ai_output=ai_output,
        ruleset=ruleset,
        latency_ms=latency_ms,
    )
    payload["metadata"]["cache_status"] = "miss"
    payload["metadata"]["cache_key_hash"] = cache_key_hash
    payload["metadata"]["cache_ttl_seconds"] = cache_ttl
    if settings.cache_enabled:
        cache_service.set(cache_key, payload, cache_ttl)
    return payload


@router.get("/timeline/{patient_token}", response_model=TimelineResponse)
async def timeline(patient_token: str, _auth: AuthContext = Depends(require_recommendation_access)):
    patient = _resolve_patient_by_token(patient_token)
    timeline_payload = get_patient_event_timeline(
        patient_token,
        patient_id=patient["patient_id"],
    )
    return timeline_payload


@router.get("/biomarker-trends/{patient_token}")
async def biomarker_trends(patient_token: str, _auth: AuthContext = Depends(require_recommendation_access)):
    patient = _resolve_patient_by_token(patient_token)
    return get_biomarker_trends(patient_token, patient_id=patient["patient_id"])


@router.get("/screening-gaps/{patient_token}")
async def screening_gaps(patient_token: str, _auth: AuthContext = Depends(require_recommendation_access)):
    patient = _resolve_patient_by_token(patient_token)
    signals = get_clinical_signals(patient_token, patient_id=patient["patient_id"])
    return {
        "patient_token": patient_token,
        "screening_gaps": signals.get("screening_gaps", []),
        "vaccination_gaps": signals.get("vaccination_gaps", []),
        "computed_at": signals.get("computed_at", ""),
        "pipeline_run_id": signals.get("pipeline_run_id", ""),
    }


@router.get("/monitoring-snapshot", response_model=MonitoringSnapshotResponse)
async def monitoring_snapshot(_auth: AuthContext = Depends(require_monitoring_access)):
    snapshot = dict(MONITORING_FIXTURE.get("snapshot", {}))
    snapshot["snapshot_at"] = datetime.now(timezone.utc).isoformat()
    return {
        "snapshot_at": snapshot.get("snapshot_at", ""),
        "refresh_interval_seconds": snapshot.get("refresh_interval_seconds", 30),
        "active_users_now": snapshot.get("active_users_now", 0),
        "sessions_today": snapshot.get("sessions_today", 0),
        "patient_records_accessed_today": snapshot.get("patient_records_accessed_today", 0),
        "ai_recommendations_generated_today": snapshot.get("ai_recommendations_generated_today", 0),
        "alert_counts": snapshot.get("alert_counts", {"critical": 0, "high": 0, "medium": 0, "low": 0}),
        "safety_validator_failures_today": snapshot.get("safety_validator_failures_today", 0),
        "top_active_departments": snapshot.get("top_active_departments", []),
    }


@router.get("/audit-logs", response_model=AuditLogsResponse)
async def audit_logs(
    user_id: str | None = Query(None),
    patient_token_prefix: str | None = Query(None),
    action_type: str | None = Query(None),
    resource_type: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    _auth: AuthContext = Depends(require_monitoring_access),
):
    results = _filter_audit_entries(
        user_id=user_id,
        patient_token_prefix=patient_token_prefix,
        action_type=action_type,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
    )
    return {"total": len(results), "entries": results}


@router.get("/anomaly-alerts", response_model=AnomalyAlertsResponse)
async def anomaly_alerts(_auth: AuthContext = Depends(require_monitoring_access)):
    return {"alerts": MONITORING_FIXTURE.get("anomaly_alerts", [])}


@router.get("/rbac", response_model=RbacResponse)
async def rbac(_auth: AuthContext = Depends(require_monitoring_access)):
    return {"roles": MONITORING_FIXTURE.get("rbac_roles", [])}


@router.get("/mapping-codes", response_model=MappingCodesResponse)
async def mapping_codes(_auth: AuthContext = Depends(require_monitoring_access)):
    mappings = MONITORING_FIXTURE.get("mapping_codes", [])
    return {"mappings": _normalize_mapping_codes(mappings)}


@router.get("/master-programs", response_model=MasterProgramsResponse)
async def master_programs(_auth: AuthContext = Depends(require_monitoring_access)):
    return {"programs": MONITORING_FIXTURE.get("master_programs", [])}


@router.get("/admin/monitoring/snapshot", response_model=MonitoringSnapshotResponse)
async def admin_monitoring_snapshot(_auth: AuthContext = Depends(require_monitoring_access)):
    return await monitoring_snapshot(_auth)


@router.get("/admin/audit-logs/search", response_model=AuditLogsResponse)
async def admin_audit_logs_search(
    user_id: str | None = Query(None),
    patient_token_prefix: str | None = Query(None),
    action_type: str | None = Query(None),
    resource_type: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    _auth: AuthContext = Depends(require_monitoring_access),
):
    return await audit_logs(
        user_id=user_id,
        patient_token_prefix=patient_token_prefix,
        action_type=action_type,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        _auth=_auth,
    )


@router.get("/admin/anomaly-alerts", response_model=AnomalyAlertsResponse)
async def admin_anomaly_alerts(_auth: AuthContext = Depends(require_monitoring_access)):
    return await anomaly_alerts(_auth)


@router.get("/admin/rbac", response_model=RbacResponse)
async def admin_rbac(_auth: AuthContext = Depends(require_monitoring_access)):
    return await rbac(_auth)


@router.get("/admin/mapping-codes", response_model=MappingCodesResponse)
async def admin_mapping_codes(_auth: AuthContext = Depends(require_monitoring_access)):
    return await mapping_codes(_auth)


@router.get("/admin/master-programs", response_model=MasterProgramsResponse)
async def admin_master_programs(_auth: AuthContext = Depends(require_monitoring_access)):
    return await master_programs(_auth)

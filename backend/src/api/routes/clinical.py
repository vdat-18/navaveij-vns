from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from src.api.routes.patients import load_registry
from src.services.orchestrator import OrchestrationManager

router = APIRouter()
orchestrator = OrchestrationManager()


class RecommendationRequest(BaseModel):
    """Schema for recommendation request."""

    patient_id: str
    force_rule_based: bool = False


@router.post("/recommend")
async def get_recommendation(request: RecommendationRequest):
    """Triggers AI reasoning."""
    logger.info(f"Clinical request: {request.patient_id}")
    registry = load_registry()
    patient = next((p for p in registry if p["patient_id"] == request.patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        res = await orchestrator.generate_recommendation(
            patient_id=request.patient_id, force_rule_based=request.force_rule_based
        )
        res["patient_name"] = patient["patient_name"]
        return res
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DecisionRequest(BaseModel):
    """Schema for physician decision."""

    patient_id: str
    recommendation_hash: str
    decision: str
    physician_id: str = "dr-admin-001"
    notes: str = ""


@router.post("/approve")
async def approve_recommendation(request: DecisionRequest):
    """Physician decision logging."""
    try:
        return await orchestrator.record_decision(
            patient_id=request.patient_id,
            recommendation_hash=request.recommendation_hash,
            decision=request.decision,
            physician_id=request.physician_id,
            notes=request.notes,
        )
    except Exception as e:
        logger.error(f"Decision logging failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit")
async def get_audit_logs():
    """Fetches audit logs."""
    try:
        return orchestrator.audit_logger.get_logs()
    except Exception as e:
        logger.error(f"Audit fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

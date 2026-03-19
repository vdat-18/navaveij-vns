"""Routes for clinical AI recommendations."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from loguru import logger

from src.api.security import AuthContext, parse_roles, require_access
from src.services.orchestrator import OrchestrationManager
from src.api.routes.patients import find_patient_by_id, resolve_patient_token
from shared.settings import settings

router = APIRouter()
orchestrator = OrchestrationManager()
require_recommendation_access = require_access(
    allowed_roles=parse_roles(settings.recommendation_allowed_roles),
    required_scopes={scope.strip().lower() for scope in settings.recommendation_required_scopes.split(",") if scope.strip()},
)

class RecommendationRequest(BaseModel):
    patient_id: str

@router.post("/recommend")
async def get_recommendation(request: RecommendationRequest, _auth: AuthContext = Depends(require_recommendation_access)):
    """Trigger AI reasoning for a specific patient."""
    logger.info(f"Received recommendation request for patient: {request.patient_id}")
    
    # 1. Verify patient exists in registry
    patient = find_patient_by_id(request.patient_id)
    if not patient:
        logger.warning(f"Patient {request.patient_id} not found in registry")
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_token = resolve_patient_token(request.patient_id)
    if not patient_token:
        raise HTTPException(status_code=404, detail="Patient token not found")

    try:
        result = await orchestrator.generate_recommendation(
            patient_id=request.patient_id, 
            patient_token=patient_token,
        )
        
        # 3. PII Rehydration
        result["patient_name"] = patient["patient_name"]
        
        return result
    except Exception as e:
        logger.error(f"Error during clinical orchestration for {request.patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class DecisionRequest(BaseModel):
    patient_id: str
    recommendation_hash: str
    decision: str  # "Approve" or "Reject"
    physician_id: str = "dr-admin-001"
    notes: str = ""

@router.post("/approve")
async def approve_recommendation(request: DecisionRequest, _auth: AuthContext = Depends(require_recommendation_access)):
    """Record physician's approval/rejection."""
    logger.info(f"Physician {request.physician_id} recording {request.decision} for {request.patient_id}")
    
    try:
        result = await orchestrator.record_decision(
            patient_id=request.patient_id,
            recommendation_hash=request.recommendation_hash,
            decision=request.decision,
            physician_id=request.physician_id,
            notes=request.notes
        )
        return result
    except Exception as e:
        logger.error(f"Error recording decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/audit")
async def get_audit_logs(_auth: AuthContext = Depends(require_recommendation_access)):
    """Retrieve all clinical decision logs."""
    try:
        return orchestrator.audit_logger.get_logs()
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

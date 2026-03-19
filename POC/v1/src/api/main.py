"""FastAPI Entry point for the Navaveij Clinical Recommendation Engine."""

# load_dotenv() MUST run before any baml_client import.
# baml_client/globals.py calls os.environ.copy() at module-import time to
# snapshot env vars into the BAML runtime. If load_dotenv() runs after that
# import, LLM_API_KEY / LLM_BASE_URL / LLM_MODEL will be empty and BAML will
# fall back to shell-level ANTHROPIC_* vars, sending a wrong model name to the
# proxy (e.g. the literal string "$ANTHROPIC_DEFAULT_SONNET_MODEL").
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

from src.orchestrator.core.manager import OrchestrationManager

app = FastAPI(
    title="Navaveij Clinical API",
    description="Intelligent Health Checkup Recommendation Engine",
    version="1.0.0",
)

# Initialize the orchestrator manager
manager = OrchestrationManager()


class RecommendationRequest(BaseModel):
    """Schema for a recommendation request."""

    patient_id: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "engine": "Navaveij Clinical Orchestrator"}


@app.post("/recommend")
async def get_recommendation(request: RecommendationRequest):
    """Generate a personalized clinical recommendation for a patient.

    This endpoint triggers the full ReAct loop:
    1. MCP data retrieval
    2. PII Masking
    3. BAML Inference
    4. Safety validation
    5. Audit logging
    6. PII Rehydration
    """
    logger.info(f"API Request received for patient: {request.patient_id}")

    # Delegate to Orchestration Manager
    result = await manager.generate_recommendation(request.patient_id)

    return result


if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

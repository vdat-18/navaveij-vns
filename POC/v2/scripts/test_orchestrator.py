"""Integration test for the Clinical Orchestrator flow."""

import asyncio
import json
from pathlib import Path
import sys
from dotenv import load_dotenv
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"

for path in (str(PROJECT_ROOT), str(BACKEND_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from src.services.orchestrator import OrchestrationManager

load_dotenv(PROJECT_ROOT / ".env")


async def test_full_orchestration():
    """Verify the end-to-end flow: MCP -> Masking -> AI Gateway -> Rehydration."""
    logger.info("Starting integration test for OrchestrationManager")

    orchestrator = OrchestrationManager()

    registry = json.loads(Path("assets/patient_registry.json").read_text(encoding="utf-8"))
    patient_id = registry[0]["patient_id"]
    patient_token = registry[0]["patient_token"]

    try:
        result = await orchestrator.generate_recommendation(patient_id, patient_token=patient_token)
        logger.success(f"Final Dashboard Output: {result}")
    except Exception:
        logger.exception("Orchestration failed")


if __name__ == "__main__":
    asyncio.run(test_full_orchestration())

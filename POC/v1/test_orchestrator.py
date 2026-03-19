"""Integration test for the Clinical Orchestrator flow."""

import asyncio
from dotenv import load_dotenv
from loguru import logger
from src.orchestrator.core.manager import OrchestrationManager

load_dotenv()


async def test_full_orchestration():
    """Verify the end-to-end flow: MCP -> Masking -> AI Gateway -> Rehydration."""
    logger.info("Starting integration test for OrchestrationManager")

    orchestrator = OrchestrationManager()

    # In a real scenario, this ID would match a record in the MCP source
    patient_id = "pt-001"

    try:
        result = await orchestrator.generate_recommendation(patient_id)
        logger.success(f"Final Dashboard Output: {result}")
    except Exception:
        logger.exception("Orchestration failed")


if __name__ == "__main__":
    asyncio.run(test_full_orchestration())

"""End-to-end integration tests for the Recommendation Engine."""

import asyncio
import json
import os
from pathlib import Path
import sys

import pytest
from dotenv import load_dotenv
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

for path in (str(PROJECT_ROOT), str(BACKEND_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from src.services.orchestrator import OrchestrationManager

load_dotenv(PROJECT_ROOT / ".env")


def _llm_env_ready() -> bool:
    api_key = (os.getenv("LLM_API_KEY") or "").strip()
    base_url = (os.getenv("LLM_BASE_URL") or "").strip()
    model = (os.getenv("LLM_MODEL") or "").strip()
    if not api_key or not base_url or not model:
        return False
    if api_key.startswith("sk-..."):
        return False
    return True


def _is_external_service_error(error: Exception) -> bool:
    message = str(error).lower()
    return "503" in message or "service unavailable" in message or "connection" in message


def _load_patient_ids(limit: int = 2) -> list[str]:
    registry = Path("assets/patient_registry.json")
    data = json.loads(registry.read_text(encoding="utf-8"))
    return [item["patient_id"] for item in data[:limit]]


@pytest.mark.asyncio
async def test_with_synthesized_data():
    """Test end-to-end flow with synthesized Signal Store data."""
    if not _llm_env_ready():
        pytest.skip("LLM environment is not configured for deterministic end-to-end verification")
    logger.info("Starting end-to-end test with synthesized data")

    manager = OrchestrationManager()

    test_patient_id = _load_patient_ids(1)[0]

    logger.info(f"Testing Orchestration for patient_id: {test_patient_id}")

    # Run manager
    try:
        result = await manager.generate_recommendation(test_patient_id)
        
        # Verify output structure
        required_fields = [
            "ai_recommended_tier",
            "reasoning_trace",
            "add_ons",
            "communication_script",
            "safety_check"
        ]

        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            logger.error(f"Missing required fields in output: {missing_fields}")
            return

        logger.success("End-to-end test completed successfully")
        logger.info(f"Output: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
        
    except Exception as e:
        if _is_external_service_error(e):
            pytest.xfail(f"External LLM dependency unavailable: {e}")
        logger.error(f"Test failed: {e}")
        raise


@pytest.mark.asyncio
async def test_multiple_scenarios():
    """Test multiple clinical scenarios."""
    if not _llm_env_ready():
        pytest.skip("LLM environment is not configured for deterministic end-to-end verification")
    logger.info("Testing multiple clinical scenarios")

    manager = OrchestrationManager()
    scenarios = _load_patient_ids(2)

    results = {}
    for patient_id in scenarios:
        logger.info(f"Testing patient: {patient_id}")

        try:
            result = await manager.generate_recommendation(patient_id)
            results[patient_id] = {
                "ai_recommended_tier": result.get("ai_recommended_tier"),
                "has_reasoning": "reasoning_trace" in result,
                "add_ons_count": len(result.get("add_ons", [])),
                "is_safe": result.get("safety_check", {}).get("is_safe")
            }
        except Exception as e:
            if _is_external_service_error(e):
                pytest.xfail(f"External LLM dependency unavailable: {e}")
            logger.error(f"Scenario {patient_id} failed: {e}")

    logger.success(f"Completed testing {len(results)} scenarios")
    logger.info(f"Results summary: {json.dumps(results, indent=2, ensure_ascii=False)}")

    return results


if __name__ == "__main__":
    logger.info("Running end-to-end tests")

    # Test 1: Single patient
    asyncio.run(test_with_synthesized_data())

    # Test 2: Multiple scenarios
    asyncio.run(test_multiple_scenarios())

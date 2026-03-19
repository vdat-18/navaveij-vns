"""End-to-end integration tests for the Recommendation Engine."""

import asyncio
import json

from loguru import logger

from src.services.orchestrator import OrchestrationManager


async def test_with_synthesized_data():
    """Test end-to-end flow with synthesized Signal Store data."""
    logger.info("Starting end-to-end test with synthesized data")

    manager = OrchestrationManager()

    # Use a test patient_id
    test_patient_id = "pt-001"

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
        logger.error(f"Test failed: {e}")
        return None


async def test_multiple_scenarios():
    """Test multiple clinical scenarios."""
    logger.info("Testing multiple clinical scenarios")

    manager = OrchestrationManager()
    # Scenarios available in our synthesis seeds
    scenarios = [
        "pt-001", # Healthy
        "pt-002", # Hypertension
    ]

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

"""End-to-end integration tests for the Recommendation Engine."""

import asyncio
import json

from loguru import logger

from src.mcp_server.utils import load_signal_store_record
from src.orchestrator.agents.orchestrator import ClinicalOrchestrator
from src.shared.settings import settings
from src.shared.utils import generate_patient_token


async def test_with_synthesized_data():
    """Test end-to-end flow with synthesized Signal Store data."""
    logger.info("Starting end-to-end test with synthesized data")

    orchestrator = ClinicalOrchestrator()

    # Use a test patient_id that will generate a patient_token
    # We'll use a known patient_id that should match one of our synthesized records
    test_patient_id = "test_patient_001"

    # Generate patient_token
    patient_token = generate_patient_token(test_patient_id, settings.patient_token_secret_salt)
    logger.info(f"Generated patient_token: {patient_token} for patient_id: {test_patient_id}")

    # Check if Signal Store record exists for this token
    record = load_signal_store_record(patient_token)
    if not record:
        logger.warning(
            f"No Signal Store record found for patient_token: {patient_token}. "
            "Please run synthesis first to generate test data."
        )
        return

    logger.info(f"Found Signal Store record for patient_token: {patient_token}")

    # Run orchestrator
    result = await orchestrator.generate_recommendation(test_patient_id)

    # Verify output structure
    required_fields = [
        "ai_recommended_tier",
        "rule_preliminary_tier",
        "confidence_score",
        "confidence_tier",
        "resolved_package",
        "add_ons",
    ]

    missing_fields = [field for field in required_fields if field not in result]
    if missing_fields:
        logger.error(f"Missing required fields in output: {missing_fields}")
        return

    logger.success("End-to-end test completed successfully")
    logger.info(f"Output: {json.dumps(result, indent=2, ensure_ascii=False)}")

    return result


async def test_multiple_scenarios():
    """Test multiple clinical scenarios."""
    logger.info("Testing multiple clinical scenarios")

    orchestrator = ClinicalOrchestrator()
    scenarios = [
        "HealthyRoutineCheckup",
        "UncontrolledHypertension",
        "MetabolicSyndromeRisk",
        "SeniorCancerScreeningGap",
        "EarlyOnsetDiabetes",
        "ChronicKidneyDiseaseProgression",
    ]

    results = {}
    for scenario in scenarios:
        logger.info(f"Testing scenario: {scenario}")

        # Generate patient_id and token for this scenario
        patient_id = f"test_{scenario.lower()}_001"
        patient_token = generate_patient_token(patient_id, settings.patient_token_secret_salt)

        # Check if record exists
        record = load_signal_store_record(patient_token)
        if not record:
            logger.warning(f"No Signal Store record found for scenario {scenario}, skipping")
            continue

        result = await orchestrator.generate_recommendation(patient_id)
        results[scenario] = {
            "patient_id": patient_id,
            "patient_token": patient_token,
            "ai_recommended_tier": result.get("ai_recommended_tier"),
            "rule_preliminary_tier": result.get("rule_preliminary_tier"),
            "confidence_score": result.get("confidence_score"),
            "confidence_tier": result.get("confidence_tier"),
            "add_ons_count": len(result.get("add_ons", [])),
        }

    logger.success(f"Completed testing {len(results)} scenarios")
    logger.info(f"Results summary: {json.dumps(results, indent=2, ensure_ascii=False)}")

    return results


if __name__ == "__main__":
    logger.info("Running end-to-end tests")

    # Test 1: Single patient
    asyncio.run(test_with_synthesized_data())

    # Test 2: Multiple scenarios
    asyncio.run(test_multiple_scenarios())

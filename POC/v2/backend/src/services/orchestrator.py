"""Orchestration Manager to coordinate workflows, safety, and audit."""

from typing import Any

from loguru import logger

from src.api.routes.patients import resolve_patient_token
from src.services.mcp_client import MCPClientFactory
from src.services.audit import AuditLogger
from src.services.privacy import PIIRehydrator
from src.services.safety import ClinicalSafetyGuard
from src.services.workflows.clinical import ClinicalReasoningWorkflow
from shared.settings import settings


class OrchestrationManager:
    """High-level manager responsible for coordinating life-cycles.

    Responsibilities:
    - MCP Infrastructure setup/teardown via Factory.
    - Execution of specific Workflows.
    - Post-processing (Safety Validation, Audit Logging).
    """

    def __init__(self):
        """Initialize core components."""
        self.safety_guard = ClinicalSafetyGuard()
        self.audit_logger = AuditLogger()

    async def generate_recommendation(
        self,
        patient_id: str,
        patient_token: str | None = None,
        force_rule_based: bool = False,
    ) -> dict[str, Any]:
        """Coordinate the full recommendation generation process.

        Args:
            patient_id: The patient to generate a recommendation for.
            patient_token: Optional pre-existing token (useful for synthesized data).
            force_rule_based: If True, bypass AI and use deterministic rules.

        Returns:
            A dictionary containing the recommendation and safety checks.
        """
        resolved_patient_token = patient_token or resolve_patient_token(patient_id)
        if not resolved_patient_token:
            raise ValueError(f"Patient token not found for patient_id: {patient_id}")
        logger.info(f"Manager received request for patient: {patient_id} (force_rule_based={force_rule_based})")

        async with MCPClientFactory.get_client() as session:
            # Initialize Workflow
            workflow = ClinicalReasoningWorkflow(session)

            # Execute Workflow
            context = await workflow.execute(
                patient_id,
                patient_token=resolved_patient_token,
                force_rule_based=force_rule_based,
            )

            # Post-process: Safety Validation
            logger.info("Performing safety validation")
            safety_result = await self.safety_guard.validate(context.ai_output, context.raw_context)
            context.ai_output["safety_check"] = safety_result

            # Post-process: Audit Logging
            logger.info("Recording audit log")
            recommendation_hash = self.audit_logger.log_recommendation(
                patient_id=patient_id,
                masked_context=context.masked_context,
                ai_output=context.ai_output,
                model_id=settings.llm_model,
            )

            context.ai_output["recommendation_hash"] = recommendation_hash

            # Post-process: Rehydration (Restore PII values for Frontend display)
            logger.info("Rehydrating AI output for frontend")
            rehydrator = PIIRehydrator(context.rehydration_map)
            masked_ai_output = context.ai_output.copy()
            rehydrated_output = rehydrator.rehydrate(context.ai_output)

            # Expose raw data for visualization/HUDs
            result = {
                **rehydrated_output,
                "biomarker_trends": context.masked_context.get("get_biomarker_trends", {}),
                "clinical_signals": context.masked_context.get("get_clinical_signals", {}),
            }

            # Final rehydration pass on everything for the frontend
            rehydrated_result = rehydrator.rehydrate(result)
            rehydrated_result["security_metadata"] = {
                "rehydration_map": context.rehydration_map,
                "masked_ai_output": masked_ai_output,
                "is_poc_demo": True,
            }
            return rehydrated_result

    async def record_decision(
        self,
        patient_id: str,
        recommendation_hash: str,
        decision: str,
        physician_id: str,
        notes: str = ""
    ) -> dict[str, Any]:
        """Record the final clinical decision in the immutable audit trail."""
        logger.info(f"Recording {decision} decision for patient {patient_id}")
        
        decision_hash = self.audit_logger.log_decision(
            patient_id=patient_id,
            recommendation_hash=recommendation_hash,
            decision=decision,
            physician_id=physician_id,
            notes=notes
        )
        
        return {
            "status": "success",
            "decision_hash": decision_hash,
            "patient_id": patient_id,
            "decision": decision
        }

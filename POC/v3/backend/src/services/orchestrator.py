from typing import Any

from loguru import logger
from src.services.audit import AuditLogger
from src.services.mcp_client import MCPClientFactory
from src.services.privacy import PIIRehydrator
from src.services.safety import ClinicalSafetyGuard
from src.services.workflows.clinical import ClinicalReasoningWorkflow

from shared.settings import settings


class OrchestrationManager:
    """Coordinates clinical workflows, safety checks, and audit logging."""

    def __init__(self):
        """Initializes components."""
        self.safety_guard = ClinicalSafetyGuard()
        self.audit_logger = AuditLogger()

    async def generate_recommendation(self, patient_id: str, force_rule_based: bool = False) -> dict:
        """Generates clinical recommendation with safety and audit."""
        logger.info(f"Generating recommendation for: {patient_id} (force_rule_based={force_rule_based})")

        async with MCPClientFactory.get_client() as session:
            workflow = ClinicalReasoningWorkflow(session)
            context = await workflow.execute(patient_id, force_rule_based=force_rule_based)

            logger.info(f"Safety validation (force_rule_based={force_rule_based})")
            safety_result = await self.safety_guard.validate(
                context.ai_output, context.raw_context, force_rule_based=force_rule_based
            )
            context.ai_output["safety_check"] = safety_result

            logger.info("Recording audit log")
            recommendation_hash = self.audit_logger.log_recommendation(
                patient_id=patient_id,
                masked_context=context.masked_context,
                ai_output=context.ai_output,
                model_id=settings.llm_model,
            )
            context.ai_output["recommendation_hash"] = recommendation_hash

            logger.info("Rehydrating AI output")
            rehydrator = PIIRehydrator(context.rehydration_map)
            masked_ai_output = context.ai_output.copy()
            rehydrated_output = rehydrator.rehydrate(context.ai_output)

            result = {
                **rehydrated_output,
                "biomarker_trends": context.masked_context.get("get_biomarker_trends", {}),
                "clinical_signals": context.masked_context.get("get_clinical_signals", {}),
                "security_metadata": {
                    "rehydration_map": context.rehydration_map,
                    "masked_ai_output": masked_ai_output,
                    "is_poc_demo": True,
                },
            }
            return rehydrator.rehydrate(result)

    async def record_decision(
        self,
        patient_id: str,
        recommendation_hash: str,
        decision: str,
        physician_id: str,
        notes: str = "",
        modified_tier: str | None = None,
        rating: int | None = None,
        feedback_comment: str | None = None,
    ) -> dict[str, Any]:
        """Records the final physician decision in audit trail."""
        logger.info(f"Recording {decision} for {patient_id}")

        hash_val = self.audit_logger.log_decision(
            patient_id=patient_id,
            recommendation_hash=recommendation_hash,
            decision=decision,
            physician_id=physician_id,
            notes=notes,
            modified_tier=modified_tier,
            rating=rating,
            feedback_comment=feedback_comment,
        )

        return {"status": "success", "decision_hash": hash_val, "patient_id": patient_id, "decision": decision}

"""Inference Orchestrator Engine for managing the clinical reasoning loop."""

import json
import os
from typing import Any

from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from baml_client.async_client import b
from src.mcp_server.utils import load_signal_store_record
from src.orchestrator.enrichment.output_enricher import OutputEnricher
from src.orchestrator.logger.audit import AuditLogger
from src.orchestrator.privacy.masking import PIIMasker
from src.orchestrator.privacy.rehydration import PIIRehydrator
from src.orchestrator.safety.validator import ClinicalSafetyGuard
from src.orchestrator.validation.confidence_calibrator import ConfidenceCalibrator
from src.shared.settings import settings
from src.shared.utils import generate_patient_token


class ClinicalOrchestrator:
    """Orchestrates the hybrid ReAct loop between MCP tools and AI Models."""

    def __init__(self):
        """Initialize orchestrator components and server parameters."""
        self.masker = PIIMasker()
        self.audit_logger = AuditLogger()
        self.safety_guard = ClinicalSafetyGuard()
        self.confidence_calibrator = ConfidenceCalibrator()
        self.output_enricher = OutputEnricher()

        # Configure MCP server parameters for stdio transport
        self.server_params = StdioServerParameters(
            command=settings.mcp_server_command, args=settings.mcp_server_args, env={**os.environ, "PYTHONPATH": "."}
        )

    async def run_baseline_phase(
        self, session: ClientSession, patient_id: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Execute mandatory baseline MCP tool calls and return raw and masked context.

        Args:
            session: Active MCP client session
            patient_id: FHIR patient ID or internal patient identifier

        Returns:
            Tuple of (raw_context, masked_context) dictionaries
        """
        logger.info(f"Starting Baseline Phase for patient: {patient_id}")

        # Generate patient_token for Signal Store and Ruleset Store tools
        patient_token = generate_patient_token(patient_id, settings.patient_token_secret_salt)
        logger.debug(f"Generated patient_token: {patient_token} for patient_id: {patient_id}")

        baseline_tools = [
            "get_patient_context",
            "get_hard_constraints",
            "get_clinical_signals",
            "get_biomarker_trends",
            "get_program_ruleset",
        ]

        raw_context = {}
        for tool_name in baseline_tools:
            logger.debug(f"Calling baseline tool: {tool_name}")

            # Determine tool arguments based on tool name
            if tool_name == "get_patient_context":
                kwargs = {"patient_id": patient_id}
            elif tool_name == "get_program_ruleset":
                kwargs = {"patient_token": patient_token}
            else:
                # All Signal Store tools require patient_token
                kwargs = {"patient_token": patient_token}

            result = await session.call_tool(tool_name, arguments=kwargs)
            text_result = result.content[0].text if result.content else None

            # Parse JSON if result is JSON string
            if text_result:
                parsed_result = json.loads(text_result)
                raw_context[tool_name] = parsed_result

                # Store Signal Store record reference for enrichment
                if tool_name == "get_hard_constraints" and parsed_result:
                    # Load full Signal Store record for metadata access
                    record = load_signal_store_record(patient_token)
                    if record:
                        raw_context["_signal_store_record"] = record
            else:
                raw_context[tool_name] = None

            logger.debug(f"Raw result for {tool_name}: {raw_context[tool_name]}")

        # Apply PII masking before passing to AI
        masked_context = self.masker.mask_data(raw_context)
        logger.debug(f"Masked context: {masked_context}")
        return raw_context, masked_context

    async def generate_recommendation(self, patient_id: str) -> dict[str, Any]:
        """Run the full orchestration loop to produce a clinical recommendation via BAML."""
        logger.info(f"Generating recommendation for patient: {patient_id}")

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 1. Baseline Phase
                raw_context, masked_context = await self.run_baseline_phase(session, patient_id)

                # 2. Inference Phase via BAML
                logger.info("Engaging BAML to generate recommendation")

                # Prepare context strings for BAML function
                hard_constraints_str = json.dumps(
                    raw_context.get("get_hard_constraints", {}), indent=2, ensure_ascii=False
                )
                clinical_signals_str = json.dumps(
                    raw_context.get("get_clinical_signals", {}), indent=2, ensure_ascii=False
                )
                biomarker_trends_str = json.dumps(
                    raw_context.get("get_biomarker_trends", {}), indent=2, ensure_ascii=False
                )
                program_ruleset_str = json.dumps(
                    raw_context.get("get_program_ruleset", {}), indent=2, ensure_ascii=False
                )

                # Call BAML with separate parameters (matching recommendation-output.baml signature)
                recommendation = await b.GenerateRecommendation(
                    hard_constraints=hard_constraints_str,
                    clinical_signals=clinical_signals_str,
                    biomarker_trends=biomarker_trends_str,
                    program_ruleset=program_ruleset_str,
                )

                # Convert BAML object to dict for downstream processing
                ai_output = {
                    "ai_recommended_tier": recommendation.ai_recommended_tier.value,
                    "tier_deviation_justification": getattr(recommendation, "tier_deviation_justification", None),
                    "reasoning_trace": recommendation.reasoning_trace,
                    "add_ons": [
                        {
                            "item_code": item.item_code,
                            "priority_level": item.priority_level.value,
                            "rationale": item.rationale,
                        }
                        for item in recommendation.add_ons
                    ],
                    "supporting_signals": recommendation.supporting_signals,
                    "missing_signals": recommendation.missing_signals,
                    "communication_script": {
                        "opening": recommendation.communication_script.opening,
                        "health_summary": recommendation.communication_script.health_summary,
                        "recommendation_explanation": recommendation.communication_script.recommendation_explanation,
                        "add_on_highlights": recommendation.communication_script.add_on_highlights,
                        "next_steps": recommendation.communication_script.next_steps,
                    },
                }

                # Extract data for Confidence Calibrator
                clinical_signals = raw_context.get("get_clinical_signals", {})
                signal_store_record = raw_context.get("_signal_store_record", {})
                signal_store_meta = signal_store_record.get("_meta", {})

                signals_fired_count = len(clinical_signals.get("signals_fired", []))
                applicable_signals_count = len(clinical_signals.get("applicable_signals", []))
                data_completeness_ratio = signal_store_meta.get("data_completeness_ratio", 0.0)
                rule_preliminary_tier = clinical_signals.get("rule_preliminary_tier", "Standard")

                # Compute confidence score
                confidence_score = self.confidence_calibrator.compute_confidence_score(
                    signals_fired_count=signals_fired_count,
                    applicable_signals_count=applicable_signals_count,
                    data_completeness_ratio=data_completeness_ratio,
                    ai_recommended_tier=ai_output["ai_recommended_tier"],
                    rule_preliminary_tier=rule_preliminary_tier,
                )

                confidence_tier = self.confidence_calibrator.compute_confidence_tier(confidence_score)

                ai_output["confidence_score"] = confidence_score
                ai_output["confidence_tier"] = confidence_tier

                # 3. Clinical Safety Validation (Hybrid: Rules + LLM Critic)
                safety_result = await self.safety_guard.validate(ai_output, raw_context)
                ai_output["safety_check"] = safety_result

                # 4. Enrich output with system-injected fields
                ruleset_response = raw_context.get("get_program_ruleset", {})
                enriched_output = self.output_enricher.enrich_output(
                    ai_output=ai_output,
                    clinical_signals=clinical_signals,
                    ruleset_response=ruleset_response,
                    signal_store_meta=signal_store_meta,
                )

                # Record 5-Dimensional Audit Log (immutable trace)
                self.audit_logger.log_recommendation(
                    patient_id=patient_id,
                    masked_context=masked_context,
                    ai_output=enriched_output,
                    model_id=settings.llm_model,
                )

                # Append original patient identifier back for the dashboard
                enriched_output["patient_id"] = patient_id

                rehydrator = PIIRehydrator(self.masker.get_rehydration_map())
                final_output = rehydrator.rehydrate(enriched_output)

                logger.success("Recommendation generation completed with BAML, safety validation, and enrichment")
                return final_output

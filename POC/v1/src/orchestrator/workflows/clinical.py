"""Clinical Reasoning Workflow implementation."""

import json
from typing import Any

from loguru import logger
from mcp import ClientSession

from baml_client.async_client import b
from src.orchestrator.privacy.masking import PIIMasker
from src.orchestrator.workflows.base import BaseWorkflow, WorkflowContext
from src.shared.exceptions import DataIntegrityError
from src.shared.settings import settings
from src.shared.utils import generate_patient_token


class ClinicalReasoningWorkflow(BaseWorkflow[WorkflowContext]):
    """Implements the 5-phase clinical reasoning loop.

    Phases:
    1. Fetch Baseline
    2. Analyze Signals
    3. Evaluate Trends
    4. Generate Recommendation (BAML)
    5. Finalize Context
    """

    def __init__(self, session: ClientSession):
        """Initialize with an active MCP session."""
        self.session = session
        self.masker = PIIMasker()

    async def execute(self, patient_id: str) -> WorkflowContext:
        """Execute the full clinical reasoning loop."""
        logger.info(f"Executing Clinical Workflow for patient: {patient_id}")
        context = WorkflowContext(patient_id=patient_id)

        # Generate patient_token once for all Signal Store tools
        patient_token = generate_patient_token(context.patient_id, settings.patient_token_secret_salt)

        # Phase 1: Baseline
        await self._fetch_baseline(context, patient_token)

        # Phase 2: Signals
        await self._analyze_signals(context, patient_token)

        # Phase 3: Trends
        await self._evaluate_trends(context, patient_token)

        # Mask data before sending to LLM
        context.masked_context = self.masker.mask_data(context.raw_context)

        # Phase 4: Recommendation
        await self._generate_recommendation(context, patient_token)

        # Phase 5: Finalize
        return context

    async def _fetch_baseline(self, context: WorkflowContext, patient_token: str) -> None:
        """Phase 1: Get patient profile and history."""
        logger.debug(f"Phase 1: Fetching baseline data for token: {patient_token}")

        # Tools: get_hard_constraints
        constraints = await self._call_mcp_tool("get_hard_constraints", {"patient_token": patient_token})
        context.raw_context["get_hard_constraints"] = constraints

        # Extract demographic context from hard constraints (as patient_context tool was removed)
        demographics = constraints.get("patient_demographics", {})
        context.raw_context["get_patient_context"] = {
            "gender": demographics.get("gender"),
            "age": demographics.get("age"),
            "ethnicity": demographics.get("ethnicity"),
        }

    async def _analyze_signals(self, context: WorkflowContext, patient_token: str) -> None:
        """Phase 2: Detect clinical alerts."""
        logger.debug("Phase 2: Analyzing clinical signals")
        signals = await self._call_mcp_tool("get_clinical_signals", {"patient_token": patient_token})
        context.raw_context["get_clinical_signals"] = signals

    async def _evaluate_trends(self, context: WorkflowContext, patient_token: str) -> None:
        """Phase 3: Assess biomarker velocity."""
        logger.debug("Phase 3: Evaluating biomarker trends")
        trends = await self._call_mcp_tool("get_biomarker_trends", {"patient_token": patient_token})
        context.raw_context["get_biomarker_trends"] = trends

    async def _generate_recommendation(self, context: WorkflowContext, patient_token: str) -> None:
        """Phase 4: BAML call for clinical tiering."""
        logger.debug("Phase 4: Generating recommendation via BAML")

        # Get program ruleset with patient_token
        ruleset = await self._call_mcp_tool("get_program_ruleset", {"patient_token": patient_token})
        context.raw_context["get_program_ruleset"] = ruleset

        # Mask again to include ruleset
        context.masked_context = self.masker.mask_data(context.raw_context)

        context_str = json.dumps(context.masked_context, indent=2)
        # Phase 4: Recommendation
        # function GenerateRecommendation(hard_constraints: string, clinical_signals: string, biomarker_trends: string, program_ruleset: string)
        recommendation = await b.GenerateRecommendation(
            hard_constraints=json.dumps(context.masked_context.get("get_hard_constraints"), indent=2),
            clinical_signals=json.dumps(context.masked_context.get("get_clinical_signals"), indent=2),
            biomarker_trends=json.dumps(context.masked_context.get("get_biomarker_trends"), indent=2),
            program_ruleset=json.dumps(context.masked_context.get("get_program_ruleset"), indent=2),
        )

        context.ai_output = {
            "ai_recommended_tier": recommendation.ai_recommended_tier.value,
            "tier_deviation_justification": recommendation.tier_deviation_justification,
            "reasoning_trace": recommendation.reasoning_trace,
            "add_ons": [
                {"item_code": item.item_code, "priority_level": item.priority_level.value, "rationale": item.rationale}
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

    async def _call_mcp_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Helper to call MCP tools and parse JSON output."""
        result = await self.session.call_tool(name, arguments)
        if not result.content:
            raise DataIntegrityError(f"Empty response from MCP tool: {name}")

        # FastMCP tools can return multiple content items; we typically want the first one's text
        raw_text = result.content[0].text
        return json.loads(raw_text)

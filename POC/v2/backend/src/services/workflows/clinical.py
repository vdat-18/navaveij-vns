"""Clinical Reasoning Workflow implementation."""

import json
from typing import Any

from loguru import logger
from mcp import ClientSession

from baml_client.async_client import b
from src.mcp_server.utils import resolve_package
from src.services.privacy import PIIMasker
from src.services.rules import RuleEvaluator
from src.services.workflows.base import BaseWorkflow, WorkflowContext
from shared.exceptions import DataIntegrityError


class ClinicalReasoningWorkflow(BaseWorkflow[WorkflowContext]):
    """Implements the 5-phase clinical reasoning loop.

    Phases:
    1. Fetch Baseline
    2. Analyze Signals
    3. Evaluate Trends
    4. Generate Recommendation (Rule + 3-agent BAML + fallback)
    5. Finalize Context
    """

    def __init__(self, session: ClientSession):
        """Initialize with an active MCP session."""
        self.session = session
        self.masker = PIIMasker()

    async def execute(
        self,
        patient_id: str,
        patient_token: str,
        force_rule_based: bool = False,
    ) -> WorkflowContext:
        """Execute the full clinical reasoning loop."""
        logger.info(f"Executing Clinical Workflow for patient: {patient_id} (force_rule_based={force_rule_based})")
        context = WorkflowContext(patient_id=patient_id)

        # Phase 1: Baseline
        await self._fetch_baseline(context, patient_id, patient_token)

        # Phase 2: Signals
        await self._analyze_signals(context, patient_id, patient_token)

        # Phase 3: Trends
        await self._evaluate_trends(context, patient_id, patient_token)

        # Get program ruleset (Part of Phase 4 preparation)
        ruleset = await self._call_mcp_tool("get_program_ruleset", self._mcp_args(patient_token, patient_id))
        context.raw_context["get_program_ruleset"] = ruleset

        # Mask data before sending to LLM
        # This dynamically generates the patient_token and masks name/id
        context.masked_context = self.masker.mask_data(context.raw_context)

        # Phase 4: Recommendation
        await self._generate_recommendation(context, force_rule_based=force_rule_based)

        # Phase 5: Finalize
        context.rehydration_map = self.masker.get_rehydration_map()
        return context

    async def _fetch_baseline(self, context: WorkflowContext, patient_id: str, patient_token: str) -> None:
        """Phase 1: Get patient profile and history."""
        logger.debug(f"Phase 1: Fetching baseline data for patient: {patient_id}")

        # Tools: get_hard_constraints
        constraints = await self._call_mcp_tool("get_hard_constraints", self._mcp_args(patient_token, patient_id))
        context.raw_context["get_hard_constraints"] = constraints

        # Extract demographic context from hard constraints
        demographics = constraints.get("patient_demographics", {})
        context.raw_context["get_patient_context"] = {
            "gender": demographics.get("gender"),
            "age": demographics.get("age"),
            "ethnicity": demographics.get("ethnicity"),
        }

    async def _analyze_signals(self, context: WorkflowContext, patient_id: str, patient_token: str) -> None:
        """Phase 2: Detect clinical alerts."""
        logger.debug(f"Phase 2: Analyzing clinical signals for: {patient_id}")
        signals = await self._call_mcp_tool("get_clinical_signals", self._mcp_args(patient_token, patient_id))
        context.raw_context["get_clinical_signals"] = signals

    async def _evaluate_trends(self, context: WorkflowContext, patient_id: str, patient_token: str) -> None:
        """Phase 3: Assess biomarker velocity for: {patient_id}"""
        logger.debug(f"Phase 3: Evaluating biomarker trends for: {patient_id}")
        trends = await self._call_mcp_tool("get_biomarker_trends", self._mcp_args(patient_token, patient_id))
        context.raw_context["get_biomarker_trends"] = trends

    async def _generate_recommendation(self, context: WorkflowContext, force_rule_based: bool = False) -> None:
        """Phase 4: Rule evaluation + 3-agent AI chain with rule-based fallback."""
        logger.debug(f"Phase 4: Generating recommendation (force_rule_based={force_rule_based})")

        clinical_signals = context.raw_context.get("get_clinical_signals", {})
        signals_fired = clinical_signals.get("signals_fired", [])
        rule_result = RuleEvaluator(signals_fired).evaluate()

        demographics = context.raw_context.get("get_patient_context", {})
        gender = demographics.get("gender", "other")
        age = demographics.get("age", 0)
        ruleset = context.raw_context.get("get_program_ruleset", {})
        package_resolution_map = ruleset.get("package_resolution_map", {})

        resolved_package = resolve_package(
            rule_result["rule_tier"],
            gender,
            age,
            package_resolution_map,
        )

        if force_rule_based:
            context.ai_output = self._build_rule_based_output(
                rule_result=rule_result,
                clinical_signals=clinical_signals,
                resolved_package=resolved_package,
            )
            return

        try:
            risk_profile = await b.AnalyzeClinicalRisks(
                clinical_signals=json.dumps(context.masked_context.get("get_clinical_signals"), indent=2),
                biomarker_trends=json.dumps(context.masked_context.get("get_biomarker_trends"), indent=2),
                hard_constraints=json.dumps(context.masked_context.get("get_hard_constraints"), indent=2),
                program_ruleset=json.dumps(context.masked_context.get("get_program_ruleset"), indent=2),
            )
            recommendation_plan = await b.MatchProgramRules(
                risk_profile=risk_profile,
                program_ruleset=json.dumps(context.masked_context.get("get_program_ruleset"), indent=2),
            )
            final_recommendation = await b.ComposeRecommendation(
                risk_profile=risk_profile,
                plan=recommendation_plan,
            )
            context.ai_output = self._map_final_to_ai_output(
                final=final_recommendation,
                risk_profile=risk_profile,
                rule_result=rule_result,
                demographics=demographics,
                package_resolution_map=package_resolution_map,
            )
        except Exception as exc:
            logger.exception(f"AI recommendation chain failed. Falling back to rule-based output: {exc}")
            context.ai_output = self._build_rule_based_output(
                rule_result=rule_result,
                clinical_signals=clinical_signals,
                resolved_package=resolved_package,
            )

    def _mcp_args(self, patient_token: str, patient_id: str | None = None) -> dict[str, str]:
        args: dict[str, str] = {"patient_token": patient_token}
        if patient_id:
            args["patient_id"] = patient_id
        return args

    def _map_final_to_ai_output(
        self,
        *,
        final: Any,
        risk_profile: Any,
        rule_result: dict[str, Any],
        demographics: dict[str, Any],
        package_resolution_map: dict[str, Any],
    ) -> dict[str, Any]:
        ai_tier = final.plan.ai_recommended_tier.value
        resolved_package = resolve_package(
            ai_tier,
            demographics.get("gender", "other"),
            demographics.get("age", 0),
            package_resolution_map,
        )
        policy_reasoning = getattr(final.plan, "policy_reasoning", None) or ""
        bullets = getattr(risk_profile, "clinical_summary_bullets", []) or []
        reasoning_lines = [f"- {line}" for line in bullets]
        if policy_reasoning:
            reasoning_lines.append(f"- Policy reasoning: {policy_reasoning}")

        return {
            "ai_recommended_tier": ai_tier,
            "tier_deviation_justification": final.plan.tier_deviation_justification,
            "add_ons": [
                {
                    "item_code": item.item_code,
                    "priority_level": item.priority_level.value,
                    "rationale": item.rationale,
                }
                for item in final.plan.selected_add_ons
            ],
            "reasoning_trace": "\n".join(reasoning_lines),
            "supporting_signals": risk_profile.supporting_signal_ids,
            "missing_signals": risk_profile.missing_signal_ids,
            "communication_script": {
                "clinical_conclusion": final.communication_script.clinical_conclusion,
                "health_summary": final.communication_script.health_summary,
                "recommendation_explanation": final.communication_script.recommendation_explanation,
                "add_on_highlights": final.communication_script.add_on_highlights,
                "next_steps": final.communication_script.next_steps,
            },
            "rule_preliminary_tier": rule_result["rule_tier"],
            "recommendation_source": "AI",
            "review_required": False,
            "package_name": resolved_package.get("package_name") if resolved_package else "TBD",
            "price_thb": resolved_package.get("price_thb") if resolved_package else 0,
        }

    def _build_rule_based_output(
        self,
        *,
        rule_result: dict[str, Any],
        clinical_signals: dict[str, Any],
        resolved_package: dict[str, Any] | None,
    ) -> dict[str, Any]:
        rule_tier = rule_result["rule_tier"]
        matched_signals = rule_result.get("signals_matched", [])
        matched_text = ", ".join(matched_signals) if matched_signals else "routine findings"
        return {
            "ai_recommended_tier": rule_tier,
            "tier_deviation_justification": "AI chain unavailable; deterministic rule fallback applied.",
            "add_ons": [],
            "reasoning_trace": (
                f"Rule-based fallback applied. Matched rule: {rule_result.get('applied_rule_id')} | "
                f"Condition: {rule_result.get('applied_condition')}"
            ),
            "supporting_signals": matched_signals,
            "missing_signals": clinical_signals.get("missing_signals", []),
            "communication_script": {
                "clinical_conclusion": f"Based on hospital rules, we recommend the {rule_tier} tier.",
                "health_summary": f"Current clinical findings ({matched_text}) indicate a {rule_tier} package.",
                "recommendation_explanation": (
                    "This recommendation follows deterministic rule matching while the AI chain is unavailable."
                ),
                "add_on_highlights": [],
                "next_steps": "Please confirm this recommendation with the clinical team.",
            },
            "rule_preliminary_tier": rule_tier,
            "recommendation_source": "RuleBased",
            "review_required": True,
            "package_name": resolved_package.get("package_name") if resolved_package else "TBD",
            "price_thb": resolved_package.get("price_thb") if resolved_package else 0,
        }

    async def _call_mcp_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Helper to call MCP tools and parse JSON output."""
        result = await self.session.call_tool(name, arguments)
        if not result.content:
            raise DataIntegrityError(f"Empty response from MCP tool: {name}")

        # FastMCP tools can return multiple content items; we typically want the first one's text
        raw_text = result.content[0].text
        return json.loads(raw_text)

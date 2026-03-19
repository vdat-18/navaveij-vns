import json
from typing import Any

from loguru import logger
from mcp import ClientSession
from src.mcp_server.utils import resolve_package
from src.services.privacy import PIIMasker
from src.services.rules import RuleEvaluator
from src.services.workflows.base import BaseWorkflow, WorkflowContext

from baml_client.async_client import b


class ClinicalReasoningWorkflow(BaseWorkflow[WorkflowContext]):
    """Implements clinical reasoning loop: Baseline, Signals, Trends, Recommendation."""

    def __init__(self, session: ClientSession):
        """Initializes with MCP session."""
        self.session = session
        self.masker = PIIMasker()

    async def execute(self, patient_id: str, force_rule_based: bool = False) -> WorkflowContext:
        """Executes full clinical loop."""
        logger.info(f"Executing workflow for: {patient_id}")
        context = WorkflowContext(patient_id=patient_id)

        await self._fetch_baseline(context, patient_id)
        await self._analyze_signals(context, patient_id)
        await self._evaluate_trends(context, patient_id)

        ruleset = await self._call_mcp_tool("get_program_ruleset", {"patient_id": patient_id})
        context.raw_context["get_program_ruleset"] = ruleset
        context.masked_context = self.masker.mask_data(context.raw_context)

        await self._generate_recommendation(context, force_rule_based=force_rule_based)
        context.rehydration_map = self.masker.get_rehydration_map()
        return context

    async def _fetch_baseline(self, context: WorkflowContext, patient_id: str) -> None:
        """Fetches patient profile."""
        constraints = await self._call_mcp_tool("get_hard_constraints", {"patient_id": patient_id})
        context.raw_context["get_hard_constraints"] = constraints
        demogs = constraints.get("patient_demographics", {})
        context.raw_context["get_patient_context"] = {
            "gender": demogs.get("gender"),
            "age": demogs.get("age"),
            "ethnicity": demogs.get("ethnicity"),
        }

    async def _analyze_signals(self, context: WorkflowContext, patient_id: str) -> None:
        """Detects clinical alerts."""
        signals = await self._call_mcp_tool("get_clinical_signals", {"patient_id": patient_id})
        context.raw_context["get_clinical_signals"] = signals

    async def _evaluate_trends(self, context: WorkflowContext, patient_id: str) -> None:
        """Assesses biomarker velocity."""
        trends = await self._call_mcp_tool("get_biomarker_trends", {"patient_id": patient_id})
        context.raw_context["get_biomarker_trends"] = trends

    async def _generate_recommendation(self, context: WorkflowContext, force_rule_based: bool = False) -> None:
        """Hybrid reasoning via AI + Rule Fallback."""
        signals = context.raw_context.get("get_clinical_signals", {}).get("signals_fired", [])
        rule_eval = RuleEvaluator(signals)
        rule_res = rule_eval.evaluate()

        rule_tier, rule_id, rule_cond = (
            rule_res["rule_tier"],
            rule_res["applied_rule_id"],
            rule_res["applied_condition"],
        )
        demogs = context.raw_context.get("get_patient_context", {})
        gender, age = demogs.get("gender", "other"), demogs.get("age", 0)
        res_map = context.raw_context.get("get_program_ruleset", {}).get("package_resolution_map", {})

        try:
            if force_rule_based:
                raise Exception("Forced Rule-Based Mode")

            logger.info("Agent 1: Risks...")
            risk_profile = await b.AnalyzeClinicalRisks(
                clinical_signals=json.dumps(context.masked_context.get("get_clinical_signals"), indent=2),
                biomarker_trends=json.dumps(context.masked_context.get("get_biomarker_trends"), indent=2),
                hard_constraints=json.dumps(context.masked_context.get("get_hard_constraints"), indent=2),
                program_ruleset=json.dumps(context.masked_context.get("get_program_ruleset"), indent=2),
            )
            logger.info("Agent 2: Policy...")
            plan = await b.MatchProgramRules(
                risk_profile=risk_profile,
                program_ruleset=json.dumps(context.masked_context.get("get_program_ruleset"), indent=2),
            )
            logger.info("Agent 3: Finalizing...")
            final = await b.ComposeRecommendation(risk_profile=risk_profile, recommendation_plan=plan)

            final_tier = final.plan.ai_recommended_tier.value
            final_pkg = resolve_package(final_tier, gender, age, res_map)

            context.ai_output = {
                "recommendation_source": "AI",
                "review_required": False,
                "rule_preliminary_tier": rule_tier,
                "ai_recommended_tier": final_tier,
                "package_name": final_pkg.get("package_name") if final_pkg else "TBD",
                "price_thb": final_pkg.get("price_thb") if final_pkg else 0,
                "tier_deviation_justification": final.plan.tier_deviation_justification,
                "reasoning_trace": "\n".join([f"- {b}" for b in risk_profile.clinical_summary_bullets]),
                "add_ons": [
                    {"item_code": i.item_code, "priority_level": i.priority_level.value, "rationale": i.rationale}
                    for i in final.plan.selected_add_ons
                ],
                "supporting_signals": risk_profile.supporting_signal_ids,
                "missing_signals": risk_profile.missing_signal_ids,
                "communication_script": {
                    "clinical_conclusion": final.script.clinical_conclusion,
                    "health_summary": final.script.health_summary,
                    "recommendation_explanation": final.script.recommendation_explanation,
                    "add_on_highlights": final.script.add_on_highlights,
                    "next_steps": final.script.next_steps,
                },
            }
        except Exception as e:
            logger.error(f"Fallback to RuleEvaluator: {e}")
            rule_matched = ", ".join([f"**{s}**" for s in rule_res.get("signals_matched", [])])
            trace = f"AI unavailable. Rule-based generated.\n- Rule: {rule_id}\n- Logic: {rule_cond}\n- Signals: {rule_matched if rule_matched else 'Routine findings.'}"
            final_pkg = resolve_package(rule_tier, gender, age, res_map)
            context.ai_output = {
                "recommendation_source": "RuleBased",
                "review_required": True,
                "rule_preliminary_tier": rule_tier,
                "ai_recommended_tier": rule_tier,
                "package_name": final_pkg.get("package_name") if final_pkg else "TBD",
                "price_thb": final_pkg.get("price_thb") if final_pkg else 0,
                "tier_deviation_justification": "AI failure fallback.",
                "reasoning_trace": trace,
                "add_ons": [],
                "supporting_signals": rule_res["signals_matched"],
                "missing_signals": [],
                "communication_script": {
                    "clinical_conclusion": f"Recommend {rule_tier} program.",
                    "health_summary": f"Findings suggest {rule_tier} tier.",
                    "recommendation_explanation": f"{rule_tier} provides essential screenings.",
                    "add_on_highlights": [],
                    "next_steps": "Consult with staff.",
                },
            }

    async def _call_mcp_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Calls MCP tool."""
        res = await self.session.call_tool(name, arguments)
        if not res.content:
            raise Exception(f"Empty MCP tool: {name}")
        return json.loads(res.content[0].text)

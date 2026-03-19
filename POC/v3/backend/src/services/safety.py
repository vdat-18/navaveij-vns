import json

from loguru import logger

from baml_client.async_client import b


class ClinicalSafetyGuard:
    """Validates AI outcomes via BAML Clinical Safety Critic."""

    async def validate(self, ai_output: dict, raw_context: dict, force_rule_based: bool = False) -> dict:
        """Safety validation; skips BAML if force_rule_based."""
        if force_rule_based:
            logger.info("Skipping BAML Safety Critic: Rules are pre-vetted.")
            return {
                "is_safe": True,
                "critic_score": 100,
                "findings": "Bypassed LLM Critic: Deterministic rules pre-approved.",
                "suggested_correction": None,
            }

        logger.info("Engaging BAML Clinical Safety Critic")
        ctx_s, rec_s = json.dumps(raw_context, indent=2), json.dumps(ai_output, indent=2)
        res = await b.ValidateRecommendation(context=ctx_s, recommendation=rec_s)

        out = {
            "is_safe": res.is_safe,
            "critic_score": res.critic_score,
            "findings": res.findings,
            "suggested_correction": res.suggested_correction,
        }
        if not out["is_safe"]:
            logger.warning("Safety check FAILED")
        else:
            logger.success("Safety check PASSED")
        return out

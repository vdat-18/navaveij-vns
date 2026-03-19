import json

from loguru import logger

from baml_client.async_client import b


class ClinicalSafetyGuard:
    """Validates AI recommendations using an LLM-based Clinical Safety Critic via BAML."""

    async def validate(self, ai_output: dict, raw_context: dict) -> dict:
        """Perform safety validation using an LLM-based Critic via BAML.

        Analyzes the recommendation against the raw clinical context for safety and consistency.
        """
        logger.info("Engaging BAML Clinical Safety Critic")

        context_str = json.dumps(raw_context, indent=2)
        recommendation_str = json.dumps(ai_output, indent=2)

        result = await b.ValidateRecommendation(context=context_str, recommendation=recommendation_str)

        # Convert BAML response to dict
        output = {
            "is_safe": result.is_safe,
            "critic_score": result.critic_score,
            "findings": result.findings,
            "suggested_correction": result.suggested_correction,
        }

        if not output["is_safe"]:
            logger.warning("Clinical safety validation failed via BAML Critic.")
        else:
            logger.success("Clinical safety validation passed via BAML Critic.")

        return output

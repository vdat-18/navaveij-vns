"""Deterministic Rule Engine for Program Tier Selection."""

from typing import Any

from loguru import logger

from src.mcp_server.utils import load_ruleset_tier_config


class RuleEvaluator:
    """Evaluate clinical signals against rule tiers and return the first match."""

    def __init__(self, signals_fired: list[str]):
        self.signals_fired = set(signals_fired or [])
        self.ruleset = load_ruleset_tier_config()

    def evaluate(self) -> dict[str, Any]:
        """Evaluate configured rules in priority order."""
        rules = self.ruleset.get("tier_selection_rules", [])
        sorted_rules = sorted(rules, key=lambda x: x.get("priority", 999))

        for rule in sorted_rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            tier = rule.get("tier", "Standard")
            logic = rule.get("match_logic", "ANY")
            conditions = rule.get("conditions", [])

            logger.debug(f"Evaluating rule: {rule_id} (Tier: {tier}, Logic: {logic})")

            if logic == "DEFAULT":
                return {
                    "rule_tier": tier,
                    "applied_rule_id": rule_id,
                    "applied_condition": "Fallback default",
                    "signals_matched": [],
                }

            if logic == "ANY":
                for cond in conditions:
                    matched_ids = self._evaluate_condition(cond)
                    if matched_ids:
                        return {
                            "rule_tier": tier,
                            "applied_rule_id": rule_id,
                            "applied_condition": cond.get("description", "Condition match"),
                            "signals_matched": sorted(matched_ids),
                        }

            elif logic == "COUNT_THRESHOLD":
                for cond in conditions:
                    if cond.get("type") != "signal_count_threshold":
                        continue
                    pool = set(cond.get("signal_pool", []))
                    min_count = cond.get("min_count", 0)
                    intersection = self.signals_fired.intersection(pool)
                    if len(intersection) >= min_count:
                        return {
                            "rule_tier": tier,
                            "applied_rule_id": rule_id,
                            "applied_condition": cond.get("description", f"Count >= {min_count}"),
                            "signals_matched": sorted(intersection),
                        }

        return {
            "rule_tier": "Standard",
            "applied_rule_id": "FINAL_FALLBACK",
            "applied_condition": "No rules matched",
            "signals_matched": [],
        }

    def _evaluate_condition(self, condition: dict[str, Any]) -> set[str]:
        cond_type = condition.get("type")
        signals_to_check = set(condition.get("signal_ids", []))

        if cond_type != "signal_active":
            return set()

        main_match = self.signals_fired.intersection(signals_to_check)
        if not main_match:
            return set()

        and_signals = condition.get("and_signal_active")
        if not and_signals:
            return main_match

        required_and = set(and_signals)
        if required_and.issubset(self.signals_fired):
            return main_match.union(required_and)
        return set()

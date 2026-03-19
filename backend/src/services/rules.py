import json
from pathlib import Path
from typing import Any

from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
RULESET_TIER_CONFIG_PATH = BASE_DIR / "assets/synthesis/rulesets/sample_ruleset_tier_config.json"


class RuleEvaluator:
    """Evaluates clinical signals against rules for tier selection."""

    def __init__(self, signals_fired: list[str]):
        """Initializes with patient signals."""
        self.signals_fired = set(signals_fired)
        self.ruleset = self._load_ruleset()

    def _load_ruleset(self) -> dict:
        """Loads deterministic ruleset."""
        if not RULESET_TIER_CONFIG_PATH.exists():
            logger.error(f"Rule Config NOT found: {RULESET_TIER_CONFIG_PATH}")
            return {"tier_selection_rules": []}
        try:
            with open(RULESET_TIER_CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Ruleset: {e}")
            return {"tier_selection_rules": []}

    def evaluate(self) -> dict[str, Any]:
        """Evaluates signals against rules by priority."""
        rules = self.ruleset.get("tier_selection_rules", [])
        for rule in sorted(rules, key=lambda x: x.get("priority", 999)):
            rid, tier, logic, conds = (
                rule.get("rule_id", "UNK"),
                rule.get("tier", "Standard"),
                rule.get("match_logic", "ANY"),
                rule.get("conditions", []),
            )

            if logic == "DEFAULT":
                return {
                    "rule_tier": tier,
                    "applied_rule_id": rid,
                    "applied_condition": "Fallback",
                    "signals_matched": [],
                }

            if logic == "ANY":
                for c in conds:
                    matched = self._evaluate_condition(c)
                    if matched:
                        return {
                            "rule_tier": tier,
                            "applied_rule_id": rid,
                            "applied_condition": c.get("description", "Match"),
                            "signals_matched": list(matched),
                        }

            elif logic == "COUNT_THRESHOLD":
                for c in conds:
                    if c.get("type") == "signal_count_threshold":
                        pool, min_c = set(c.get("signal_pool", [])), c.get("min_count", 0)
                        inter = self.signals_fired.intersection(pool)
                        if len(inter) >= min_c:
                            return {
                                "rule_tier": tier,
                                "applied_rule_id": rid,
                                "applied_condition": c.get("description", f"Count >= {min_c}"),
                                "signals_matched": list(inter),
                            }

        return {
            "rule_tier": "Standard",
            "applied_rule_id": "FALLBACK",
            "applied_condition": "None matched",
            "signals_matched": [],
        }

    def _evaluate_condition(self, condition: dict) -> set[str]:
        """Evaluates a single condition."""
        if condition.get("type") == "signal_active":
            main = self.signals_fired.intersection(set(condition.get("signal_ids", [])))
            if main:
                _and = condition.get("and_signal_active")
                if _and:
                    req = set(_and)
                    return main.union(req) if req.issubset(self.signals_fired) else set()
                return main
        return set()

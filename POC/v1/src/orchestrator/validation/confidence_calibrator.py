"""Confidence Calibrator for computing deterministic confidence scores."""

from loguru import logger


class ConfidenceCalibrator:
    """Computes deterministic confidence scores from observable evidence.

    According to Signal Store Contract, confidence_score is computed as:
    confidence_score = (0.4 × signal_coverage) + (0.4 × data_completeness) + (0.2 × rule_agreement)

    Where:
    - signal_coverage = len(signals_fired) / len(applicable_signals)
    - data_completeness = populated_key_fields / total_key_fields (from Signal Store _meta)
    - rule_agreement = 1.0 if ai_recommended_tier == rule_preliminary_tier else 0.7
    """

    def compute_confidence_score(
        self,
        signals_fired_count: int,
        applicable_signals_count: int,
        data_completeness_ratio: float,
        ai_recommended_tier: str,
        rule_preliminary_tier: str,
    ) -> float:
        """Compute confidence score from observable evidence.

        Args:
            signals_fired_count: Number of signals that evaluated to active
            applicable_signals_count: Total number of signals evaluated for this patient
            data_completeness_ratio: Ratio of populated fields (0.0-1.0)
            ai_recommended_tier: Tier recommended by AI ("Standard", "Advanced", "Premium")
            rule_preliminary_tier: Tier from rule-based evaluation ("Standard", "Advanced", "Premium")

        Returns:
            Confidence score in range [0.0, 1.0]
        """
        # Signal coverage ratio
        if applicable_signals_count == 0:
            signal_coverage = 0.0
        else:
            signal_coverage = signals_fired_count / applicable_signals_count

        # Data completeness (already a ratio)
        data_completeness = max(0.0, min(1.0, data_completeness_ratio))

        # Rule agreement: 1.0 if match, 0.7 if mismatch
        rule_agreement = 1.0 if ai_recommended_tier == rule_preliminary_tier else 0.7

        # Weighted average
        confidence_score = (0.4 * signal_coverage) + (0.4 * data_completeness) + (0.2 * rule_agreement)

        logger.debug(
            f"Confidence score computation: "
            f"signal_coverage={signal_coverage:.3f}, "
            f"data_completeness={data_completeness:.3f}, "
            f"rule_agreement={rule_agreement:.3f}, "
            f"confidence_score={confidence_score:.3f}"
        )

        return max(0.0, min(1.0, confidence_score))

    def compute_confidence_tier(self, confidence_score: float) -> str:
        """Derive confidence tier from confidence score.

        Args:
            confidence_score: Confidence score in range [0.0, 1.0]

        Returns:
            Confidence tier: "High" (≥0.75), "Medium" (≥0.50), "Low" (<0.50)
        """
        if confidence_score >= 0.75:
            return "High"
        elif confidence_score >= 0.50:
            return "Medium"
        else:
            return "Low"

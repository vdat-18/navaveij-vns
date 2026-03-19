"""Tool for retrieving pre-computed clinical risk signals from Signal Store."""

from loguru import logger

from src.mcp_server.utils import extract_clinical_signals, load_signal_store_record


def get_clinical_signals(patient_id: str) -> dict:
    """Retrieve pre-computed clinical risk signals and abnormality triggers.

    Returns clinical signals including risk flags, screening gaps, vaccination gaps,
    abnormal triggers, comorbidity tags, family history flags, behavioral flags,
    and symptom tags according to Signal Store Contract.

    Args:
        patient_id: Stable patient identifier

    Returns:
        Clinical signals dict matching Signal Store Contract format:
        {
            "patient_id": str,
            "rule_preliminary_tier": str,
            "overall_risk_level": str,
            "applicable_signals": [...],
            "signals_fired": [...],
            "missing_signals": [...],
            "risk_flags": [...],
            "comorbidity_tags": [...],
            "screening_gaps": [...],
            "vaccination_gaps": [...],
            "abnormal_triggers": [...],
            "family_history_flags": {...},
            "behavioral_flags": {...},
            "symptom_tags": [...],
            "computed_at": str,
            "pipeline_run_id": str
        }
    """
    logger.info(f"Retrieving clinical signals for patient_id: {patient_id}")

    record = load_signal_store_record(patient_id)
    if not record:
        logger.error(f"Signal Store record not found for patient_id: {patient_id}")
        return {
            "patient_id": patient_id,
            "rule_preliminary_tier": "Standard",
            "overall_risk_level": "Low",
            "applicable_signals": [],
            "signals_fired": [],
            "missing_signals": [],
            "risk_flags": [],
            "comorbidity_tags": [],
            "screening_gaps": [],
            "vaccination_gaps": [],
            "abnormal_triggers": [],
            "family_history_flags": {},
            "behavioral_flags": {},
            "symptom_tags": [],
            "computed_at": "",
            "pipeline_run_id": "",
        }

    signals = extract_clinical_signals(record)
    return signals

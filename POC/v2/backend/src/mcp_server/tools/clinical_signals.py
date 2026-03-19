"""Tool for retrieving pre-computed clinical risk signals from Signal Store."""

from loguru import logger

from src.mcp_server.utils import extract_clinical_signals, load_signal_store_record, resolve_patient_token


def get_clinical_signals(patient_token: str, patient_id: str | None = None) -> dict:
    """Retrieve pre-computed clinical risk signals and abnormality triggers.

    Returns clinical signals including risk flags, screening gaps, vaccination gaps,
    abnormal triggers, comorbidity tags, family history flags, behavioral flags,
    and symptom tags according to Signal Store Contract.

    Args:
        patient_token: Canonical patient token
        patient_id: Optional legacy stable patient identifier

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
    logger.info(f"Retrieving clinical signals for patient_token: {patient_token}")

    resolved_patient_id = patient_id or resolve_patient_token(patient_token)
    record = load_signal_store_record(patient_token=patient_token, patient_id=resolved_patient_id)
    if not record:
        logger.error(f"Signal Store record not found for patient_token: {patient_token}")
        return {
            "patient_token": patient_token,
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

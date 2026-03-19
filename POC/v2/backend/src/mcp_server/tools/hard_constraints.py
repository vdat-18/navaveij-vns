"""Tool for retrieving non-negotiable medical constraints from Signal Store."""

from loguru import logger

from src.mcp_server.utils import extract_hard_constraints, load_signal_store_record, resolve_patient_token


def get_hard_constraints(patient_token: str, patient_id: str | None = None) -> dict:
    """Retrieve non-negotiable medical constraints for a specific patient.

    Returns hard constraints including patient demographics, eligibility exclusions,
    active safety flags, and tier ceiling according to Signal Store Contract.

    Args:
        patient_token: Canonical patient token
        patient_id: Optional legacy stable patient identifier

    Returns:
        Hard constraints dict matching Signal Store Contract format:
        {
            "patient_token": str,
            "patient_demographics": {...},
            "eligibility_exclusions": [...],
            "active_safety_flags": [...],
            "tier_ceiling": str | null,
            "computed_at": str,
            "pipeline_run_id": str
        }
    """
    logger.info(f"Retrieving hard constraints for patient_token: {patient_token}")

    resolved_patient_id = patient_id or resolve_patient_token(patient_token)
    record = load_signal_store_record(patient_token=patient_token, patient_id=resolved_patient_id)
    if not record:
        logger.error(f"Signal Store record not found for patient_token: {patient_token}")
        return {
            "patient_token": patient_token,
            "patient_demographics": {},
            "eligibility_exclusions": [],
            "active_safety_flags": [],
            "tier_ceiling": None,
            "computed_at": "",
            "pipeline_run_id": "",
        }

    constraints = extract_hard_constraints(record)
    return constraints

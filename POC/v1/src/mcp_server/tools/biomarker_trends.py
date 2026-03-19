"""Tool for retrieving biomarker trends and velocities from Signal Store."""

from loguru import logger

from src.mcp_server.utils import extract_biomarker_trends, load_signal_store_record


def get_biomarker_trends(patient_token: str) -> dict:
    """Retrieve historical trends and velocity for key biomarkers.

    Returns biomarker trends including BMI, blood pressure, eGFR, lab values,
    ASCVD 10-year risk, and waist circumference according to Signal Store Contract.

    Args:
        patient_token: HMAC-SHA256 pseudonymous patient identifier

    Returns:
        Biomarker trends dict matching Signal Store Contract format:
        {
            "patient_token": str,
            "bmi": {...},
            "blood_pressure": {...},
            "egfr": {...},
            "labs": [...],
            "ascvd_10yr_risk": {...},
            "waist_circumference": {...} | null,
            "computed_at": str,
            "pipeline_run_id": str
        }
    """
    logger.info(f"Retrieving biomarker trends for patient_token: {patient_token}")

    record = load_signal_store_record(patient_token)
    if not record:
        logger.error(f"Signal Store record not found for patient_token: {patient_token}")
        return {
            "patient_token": patient_token,
            "bmi": {},
            "blood_pressure": {},
            "egfr": {},
            "labs": [],
            "ascvd_10yr_risk": {},
            "waist_circumference": None,
            "computed_at": "",
            "pipeline_run_id": "",
        }

    trends = extract_biomarker_trends(record)
    return trends

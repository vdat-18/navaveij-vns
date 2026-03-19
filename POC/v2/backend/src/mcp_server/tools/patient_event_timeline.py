from loguru import logger

from src.mcp_server.utils import (
    build_timeline_from_signal_store,
    get_current_timestamp,
    load_signal_store_record,
    load_timeline_sample,
    resolve_patient_token,
)


def get_patient_event_timeline(patient_token: str, patient_id: str | None = None) -> dict:
    logger.info(f"Retrieving patient event timeline for patient_token: {patient_token}")
    resolved_patient_id = patient_id or resolve_patient_token(patient_token)
    sample = load_timeline_sample()
    if sample and sample.get("patient_token") == patient_token:
        return sample
    record = load_signal_store_record(patient_token=patient_token, patient_id=resolved_patient_id)
    if not record:
        return {
            "patient_token": patient_token,
            "timeline_span": {
                "earliest_event_date": get_current_timestamp()[:10],
                "latest_event_date": get_current_timestamp()[:10],
                "total_years_covered": 1.0,
            },
            "diagnoses": [],
            "hospitalizations": [],
            "significant_lab_events": [],
            "screening_procedure_history": [],
            "medication_changes": [],
            "pipeline_run_id": "",
            "computed_at": get_current_timestamp(),
        }
    return build_timeline_from_signal_store(record, patient_token)

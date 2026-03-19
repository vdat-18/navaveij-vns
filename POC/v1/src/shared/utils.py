"""Shared utility functions for the Navaveij Recommendation Engine."""

import hashlib
import hmac


def generate_patient_token(patient_id: str, secret_salt: str) -> str:
    """Generate HMAC-SHA256 patient token from patient_id.

    According to Signal Store Contract, patient_token is computed as:
    HMAC-SHA256(fhir_patient_id, secret_salt) formatted as "tok_hmac_XXXXXXXX"
    where XXXX is the first 8 hex digits of the HMAC.

    Args:
        patient_id: FHIR patient ID or internal patient identifier
        secret_salt: Secret salt for HMAC computation (from settings)

    Returns:
        Patient token in format "tok_hmac_XXXXXXXX" (8 hex digits)
    """
    hmac_obj = hmac.new(
        secret_salt.encode("utf-8"),
        patient_id.encode("utf-8"),
        hashlib.sha256,
    )
    token_hex = hmac_obj.hexdigest()[:8]
    return f"tok_hmac_{token_hex}"

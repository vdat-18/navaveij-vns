"""PII Handling module for pseudonymization and rehydration."""

import uuid
from typing import Any
from loguru import logger

# Fields identified as PII in the Navaveij healthcare context
PII_FIELDS = {
    "name",
    "first_name",
    "last_name",
    "birth_date",
    "date_of_birth",
    "phone",
    "email",
    "address",
    "mrn",
    "fhir_patient_id",
}


class PIIMasker:
    """Handles pseudonymization of sensitive fields using request-scoped UUID mapping."""

    def __init__(self):
        """Initialize the masker with an empty rehydration map."""
        self.rehydration_map: dict[str, str] = {}

    def mask_value(self, field_name: str, value: Any) -> Any:
        """Replace a sensitive value with a UUID token and store the mapping."""
        if not isinstance(value, str) or field_name.lower() not in PII_FIELDS:
            return value

        # Use existing token if value was already masked in this session
        for token, original in self.rehydration_map.items():
            if original == value:
                return token

        token = f"tok_{uuid.uuid4().hex[:8]}"
        self.rehydration_map[token] = value
        logger.debug(f"Masked field '{field_name}' with token '{token}'")
        return token

    def mask_data(self, data: Any) -> Any:
        """Recursively mask PII fields in dictionaries and lists."""
        if isinstance(data, dict):
            return {
                key: self.mask_data(value) if key.lower() not in PII_FIELDS else self.mask_value(key, value)
                for key, value in data.items()
            }
        if isinstance(data, list):
            return [self.mask_data(item) for item in data]
        return data

    def get_rehydration_map(self) -> dict[str, str]:
        """Return the current token-to-value mapping."""
        return self.rehydration_map


class PIIRehydrator:
    """Restores original PII values into the structured AI output before dashboard delivery."""

    def __init__(self, rehydration_map: dict[str, str]):
        """Initialize the rehydrator with a specific request-scoped mapping."""
        self.rehydration_map = rehydration_map

    def rehydrate(self, data: Any) -> Any:
        """Recursively replace tokens with original values in dictionaries and lists."""
        if isinstance(data, str):
            # Try to replace the token if it's an exact match
            if original_value := self.rehydration_map.get(data):
                logger.debug(f"Rehydrated exact token '{data}' back to original value")
                return original_value
            
            # Also handle if the token is embedded in a string (e.g. reasoning trace)
            rehydrated_str = data
            for token, original in self.rehydration_map.items():
                if token in rehydrated_str:
                    rehydrated_str = rehydrated_str.replace(token, original)
            
            if rehydrated_str != data:
                 logger.debug(f"Rehydrated embedded tokens in string")
                 return rehydrated_str
            
            return data

        if isinstance(data, dict):
            return {key: self.rehydrate(value) for key, value in data.items()}

        if isinstance(data, list):
            return [self.rehydrate(item) for item in data]

        return data

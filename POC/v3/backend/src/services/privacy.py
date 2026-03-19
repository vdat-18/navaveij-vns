import uuid
from typing import Any

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
    "patient_id",
}


class PIIMasker:
    """Pseudonymizes PII fields using UUID tokens."""

    def __init__(self):
        """Initializes mapping."""
        self.rehydration_map: dict[str, str] = {}

    def mask_value(self, field: str, val: Any) -> Any:
        """Replaces sensitive value with token."""
        if not isinstance(val, str) or field.lower() not in PII_FIELDS:
            return val
        for t, orig in self.rehydration_map.items():
            if orig == val:
                return t
        token = f"tok_{uuid.uuid4().hex[:8]}"
        self.rehydration_map[token] = val
        return token

    def mask_data(self, data: Any) -> Any:
        """Recursively masks data."""
        if isinstance(data, dict):
            return {
                k: self.mask_data(v) if k.lower() not in PII_FIELDS else self.mask_value(k, v) for k, v in data.items()
            }
        return [self.mask_data(i) for i in data] if isinstance(data, list) else data

    def get_rehydration_map(self) -> dict[str, str]:
        """Returns mapping."""
        return self.rehydration_map


class PIIRehydrator:
    """Restores PII values from tokens."""

    def __init__(self, remap: dict[str, str]):
        """Initializes with mapping."""
        self.rehydration_map = remap

    def rehydrate(self, data: Any) -> Any:
        """Recursively rehydrates data."""
        if isinstance(data, str):
            if orig := self.rehydration_map.get(data):
                return orig
            res = data
            for t, o in self.rehydration_map.items():
                if t in res:
                    res = res.replace(t, o)
            return res
        if isinstance(data, dict):
            return {k: self.rehydrate(v) for k, v in data.items()}
        return [self.rehydrate(i) for i in data] if isinstance(data, list) else data

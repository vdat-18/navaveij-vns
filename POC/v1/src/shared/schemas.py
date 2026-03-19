"""Pydantic schemas for standardized clinical data exchange."""

from datetime import date

from pydantic import BaseModel


class PatientSchema(BaseModel):
    """Schema for patient demographic information."""

    id: str
    fhir_patient_id: str
    mrn: str
    name: str
    gender: str
    birth_date: date
    age: int
    ethnicity: str | None = None


class ReferenceRangeSchema(BaseModel):
    """Schema for observation reference ranges."""

    low: float | None = None
    high: float | None = None
    text: str | None = None


class ObservationComponentSchema(BaseModel):
    """Schema for multi-component observations like Blood Pressure."""

    type: str
    loinc_code: str
    value: float
    unit: str
    reference_range: ReferenceRangeSchema | None = None


class ObservationSchema(BaseModel):
    """Schema for clinical observations (vitals, labs)."""

    id: str
    type: str
    loinc_code: str
    date: date
    value: float | None = None
    unit: str | None = None
    interpretation: str | None = None
    reference_range: ReferenceRangeSchema | None = None
    components: list[ObservationComponentSchema] | None = None


class ConditionSchema(BaseModel):
    """Schema for patient clinical conditions."""

    id: str
    status: str
    verification_status: str
    code: dict
    onset_date: date | None = None
    recorded_date: date


class FamilyHistorySchema(BaseModel):
    """Schema for patient family medical history."""

    id: str
    relationship: dict
    condition: dict
    onset_age: int | None = None
    note: str | None = None


class ClinicalContextSchema(BaseModel):
    """Root schema representing the full standardized clinical context."""

    patient: PatientSchema
    observations: dict
    conditions: list[ConditionSchema] = []
    family_history: list[FamilyHistorySchema] = []
    medications: list[dict] = []

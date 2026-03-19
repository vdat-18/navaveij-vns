"""Tests for the Navaveij exception hierarchy."""

import pytest

from src.shared.exceptions import (
    ClinicalProcessError,
    DataIntegrityError,
    InfrastructureError,
    NavaveijError,
    SafetyViolationError,
)


def test_exception_hierarchy():
    """Verify that exceptions follow the expected inheritance pattern."""
    # Base level
    assert issubclass(NavaveijError, Exception)

    # Second level
    assert issubclass(ClinicalProcessError, NavaveijError)
    assert issubclass(SafetyViolationError, NavaveijError)
    assert issubclass(InfrastructureError, NavaveijError)

    # Third level
    assert issubclass(DataIntegrityError, ClinicalProcessError)


def test_exception_metadata():
    """Verify that exceptions carry trace_id and metadata."""
    trace_id = "test-trace-123"
    metadata = {"key": "value"}

    with pytest.raises(DataIntegrityError) as excinfo:
        raise DataIntegrityError("Data missing", trace_id=trace_id, metadata=metadata)

    assert str(excinfo.value) == "Data missing"
    assert excinfo.value.trace_id == trace_id
    assert excinfo.value.metadata == metadata

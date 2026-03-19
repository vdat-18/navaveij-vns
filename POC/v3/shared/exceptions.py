"""Centralized exception hierarchy for Navaveij."""

from typing import Any


class NavaveijError(Exception):
    """Base exception for all Navaveij errors."""

    def __init__(self, message: str, trace_id: str | None = None, metadata: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.trace_id = trace_id
        self.metadata = metadata or {}


class ClinicalProcessError(NavaveijError):
    """Exceptions related to the clinical reasoning process."""

    pass


class DataIntegrityError(ClinicalProcessError):
    """Raised when data from external sources (e.g. MCP) is invalid or missing."""

    pass


class WorkflowStepError(ClinicalProcessError):
    """Raised when a specific step in the reasoning workflow fails."""

    pass


class SafetyViolationError(NavaveijError):
    """Raised when a recommendation is blocked by the safety validator."""

    pass


class InfrastructureError(NavaveijError):
    """Exceptions related to external connectivity (MCP, LLM APIs)."""

    pass

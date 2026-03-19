"""Base classes for the Navaveij Workflow Engine."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


class WorkflowContext(BaseModel):
    """Standard context for storing state across workflow steps.

    This object is passed between steps and serialized/logged for audit.
    """

    patient_id: str
    raw_context: dict[str, Any] = Field(default_factory=dict)
    masked_context: dict[str, Any] = Field(default_factory=dict)
    ai_output: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


TContext = TypeVar("TContext", bound=WorkflowContext)


class BaseWorkflow(ABC, Generic[TContext]):
    """Abstract base class for all reasoning workflows.

    Provides a structured interface for executing sequential steps.
    """

    @abstractmethod
    async def execute(self, patient_id: str) -> TContext:
        """Execute the full workflow loop for a given patient.

        Args:
            patient_id: Unique identifier for the patient.

        Returns:
            The final WorkflowContext after all steps are complete.
        """
        pass

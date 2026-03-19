from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


class WorkflowContext(BaseModel):
    """Standard context for workflow state."""

    patient_id: str
    raw_context: dict[str, Any] = Field(default_factory=dict)
    masked_context: dict[str, Any] = Field(default_factory=dict)
    ai_output: dict[str, Any] = Field(default_factory=dict)
    rehydration_map: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


TContext = TypeVar("TContext", bound=WorkflowContext)


class BaseWorkflow(ABC, Generic[TContext]):
    """Abstract base for reasoning workflows."""

    @abstractmethod
    async def execute(self, patient_id: str) -> TContext:
        """Executes workflow."""
        pass

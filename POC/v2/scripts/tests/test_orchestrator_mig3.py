from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.orchestrator import OrchestrationManager
from src.services.workflows.base import WorkflowContext


class _ClientContextManager:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return None


def _build_context() -> WorkflowContext:
    return WorkflowContext(
        patient_id="id_test_001",
        raw_context={"risk": "test"},
        masked_context={
            "get_biomarker_trends": {"trend_flag": "up"},
            "get_clinical_signals": {"signals_fired": ["S1"]},
        },
        ai_output={
            "reasoning_trace": "Patient token tok_abcd1234 requires follow-up.",
            "recommendation_source": "RuleBased",
        },
        rehydration_map={"tok_abcd1234": "Jane Doe"},
    )


@pytest.mark.asyncio
async def test_orchestrator_passes_force_rule_based_to_workflow():
    context = _build_context()
    workflow = SimpleNamespace(execute=AsyncMock(return_value=context))
    session = Mock()

    with (
        patch(
            "src.services.orchestrator.MCPClientFactory.get_client",
            return_value=_ClientContextManager(session),
        ),
        patch(
            "src.services.orchestrator.ClinicalReasoningWorkflow",
            return_value=workflow,
        ),
    ):
        manager = OrchestrationManager()
        manager.safety_guard.validate = AsyncMock(return_value={"is_safe": True})
        manager.audit_logger.log_recommendation = Mock(return_value="hash_mig3")
        result = await manager.generate_recommendation(
            patient_id="id_test_001",
            patient_token="tok_hmac_test_001",
            force_rule_based=True,
        )

    workflow.execute.assert_awaited_once_with(
        "id_test_001",
        patient_token="tok_hmac_test_001",
        force_rule_based=True,
    )
    assert result["recommendation_hash"] == "hash_mig3"
    assert result["recommendation_source"] == "RuleBased"


@pytest.mark.asyncio
async def test_orchestrator_injects_security_metadata_after_final_rehydration():
    context = _build_context()
    workflow = SimpleNamespace(execute=AsyncMock(return_value=context))
    session = Mock()

    with (
        patch(
            "src.services.orchestrator.MCPClientFactory.get_client",
            return_value=_ClientContextManager(session),
        ),
        patch(
            "src.services.orchestrator.ClinicalReasoningWorkflow",
            return_value=workflow,
        ),
    ):
        manager = OrchestrationManager()
        manager.safety_guard.validate = AsyncMock(return_value={"is_safe": True})
        manager.audit_logger.log_recommendation = Mock(return_value="hash_mig3")
        result = await manager.generate_recommendation(
            patient_id="id_test_001",
            patient_token="tok_hmac_test_001",
        )

    assert result["reasoning_trace"] == "Patient token Jane Doe requires follow-up."
    assert result["biomarker_trends"] == {"trend_flag": "up"}
    assert result["clinical_signals"] == {"signals_fired": ["S1"]}
    assert result["security_metadata"]["rehydration_map"] == {"tok_abcd1234": "Jane Doe"}
    assert result["security_metadata"]["masked_ai_output"]["reasoning_trace"] == (
        "Patient token tok_abcd1234 requires follow-up."
    )
    assert result["security_metadata"]["is_poc_demo"] is True

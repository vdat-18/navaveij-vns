"""Tests for the Clinical Reasoning Workflow."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from src.services.workflows.base import WorkflowContext
from src.services.workflows.clinical import ClinicalReasoningWorkflow


@pytest.fixture
def mock_session():
    """Mock MCP Client session."""
    session = AsyncMock()
    session.call_tool = AsyncMock()
    return session


def _mock_mcp_side_effect() -> list[AsyncMock]:
    return [
        AsyncMock(
            content=[
                AsyncMock(
                    text='{"patient_demographics":{"gender":"male","age":35,"ethnicity":"asian"},"eligibility_exclusions":[]}'
                )
            ]
        ),
        AsyncMock(
            content=[
                AsyncMock(
                    text='{"signals_fired":["signal_1"],"missing_signals":["signal_missing"],"rule_preliminary_tier":"Advanced"}'
                )
            ]
        ),
        AsyncMock(content=[AsyncMock(text='{"bmi":{"current":24.5}}')]),
        AsyncMock(content=[AsyncMock(text='{"rule_preliminary_tier":"Advanced","add_on_library":[],"package_resolution_map":{}}')]),
    ]


@pytest.mark.asyncio
async def test_clinical_workflow_ai_path(mock_session):
    patient_id = "id_1aa1b504"
    patient_token = "tok_hmac_1aa1b504"
    mock_session.call_tool.side_effect = _mock_mcp_side_effect()

    risk_profile = SimpleNamespace(
        clinical_summary_bullets=["Signal 1 indicates elevated risk"],
        supporting_signal_ids=["signal_1"],
        missing_signal_ids=["signal_missing"],
    )
    plan = SimpleNamespace(
        ai_recommended_tier=SimpleNamespace(value="Advanced"),
        tier_deviation_justification="Policy-aligned escalation",
        selected_add_ons=[
            SimpleNamespace(
                item_code="AON001",
                priority_level=SimpleNamespace(value="Yellow"),
                rationale="Triggered by signal_1",
            )
        ],
        policy_reasoning="Program matrix matched elevated risk profile.",
    )
    final = SimpleNamespace(
        plan=plan,
        communication_script=SimpleNamespace(
            clinical_conclusion="Advanced tier is recommended.",
            health_summary="There is elevated metabolic risk.",
            recommendation_explanation="A higher tier improves screening coverage.",
            add_on_highlights=["AON001"],
            next_steps="Book the advanced package this month.",
        ),
    )

    with (
        patch(
            "src.services.workflows.clinical.RuleEvaluator.evaluate",
            return_value={
                "rule_tier": "Standard",
                "applied_rule_id": "RULE-STD",
                "applied_condition": "Default fallback",
                "signals_matched": [],
            },
        ),
        patch("baml_client.async_client.b.AnalyzeClinicalRisks", AsyncMock(return_value=risk_profile)),
        patch("baml_client.async_client.b.MatchProgramRules", AsyncMock(return_value=plan)),
        patch("baml_client.async_client.b.ComposeRecommendation", AsyncMock(return_value=final)),
    ):
        workflow = ClinicalReasoningWorkflow(mock_session)
        result = await workflow.execute(patient_id, patient_token=patient_token)

    assert isinstance(result, WorkflowContext)
    assert result.patient_id == patient_id
    assert result.ai_output["ai_recommended_tier"] == "Advanced"
    assert result.ai_output["recommendation_source"] == "AI"
    assert result.ai_output["review_required"] is False
    assert result.ai_output["rule_preliminary_tier"] == "Standard"
    assert result.ai_output["add_ons"][0]["item_code"] == "AON001"
    assert result.ai_output["communication_script"]["clinical_conclusion"] == "Advanced tier is recommended."
    assert mock_session.call_tool.call_count == 4
    for call in mock_session.call_tool.call_args_list:
        assert "patient_token" in call.args[1]
        assert call.args[1]["patient_token"] == patient_token


@pytest.mark.asyncio
async def test_clinical_workflow_force_rule_based(mock_session):
    patient_id = "id_1aa1b504"
    patient_token = "tok_hmac_1aa1b504"
    mock_session.call_tool.side_effect = _mock_mcp_side_effect()

    analyze_mock = AsyncMock()
    match_mock = AsyncMock()
    compose_mock = AsyncMock()

    with (
        patch(
            "src.services.workflows.clinical.RuleEvaluator.evaluate",
            return_value={
                "rule_tier": "Advanced",
                "applied_rule_id": "RULE-ADV",
                "applied_condition": "signal_1 active",
                "signals_matched": ["signal_1"],
            },
        ),
        patch("baml_client.async_client.b.AnalyzeClinicalRisks", analyze_mock),
        patch("baml_client.async_client.b.MatchProgramRules", match_mock),
        patch("baml_client.async_client.b.ComposeRecommendation", compose_mock),
    ):
        workflow = ClinicalReasoningWorkflow(mock_session)
        result = await workflow.execute(patient_id, patient_token=patient_token, force_rule_based=True)

    assert result.ai_output["ai_recommended_tier"] == "Advanced"
    assert result.ai_output["recommendation_source"] == "RuleBased"
    assert result.ai_output["review_required"] is True
    assert result.ai_output["supporting_signals"] == ["signal_1"]
    analyze_mock.assert_not_awaited()
    match_mock.assert_not_awaited()
    compose_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_clinical_workflow_ai_exception_fallback(mock_session):
    patient_id = "id_1aa1b504"
    patient_token = "tok_hmac_1aa1b504"
    mock_session.call_tool.side_effect = _mock_mcp_side_effect()

    with (
        patch(
            "src.services.workflows.clinical.RuleEvaluator.evaluate",
            return_value={
                "rule_tier": "Premium",
                "applied_rule_id": "RULE-PRM",
                "applied_condition": "high-risk combination",
                "signals_matched": ["signal_1"],
            },
        ),
        patch(
            "baml_client.async_client.b.AnalyzeClinicalRisks",
            AsyncMock(side_effect=RuntimeError("LLM unavailable")),
        ),
    ):
        workflow = ClinicalReasoningWorkflow(mock_session)
        result = await workflow.execute(patient_id, patient_token=patient_token)

    assert result.ai_output["ai_recommended_tier"] == "Premium"
    assert result.ai_output["recommendation_source"] == "RuleBased"
    assert result.ai_output["review_required"] is True
    assert "fallback" in result.ai_output["tier_deviation_justification"].lower()

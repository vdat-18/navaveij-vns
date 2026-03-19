"""Tests for the Clinical Reasoning Workflow."""

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


@pytest.mark.asyncio
async def test_clinical_workflow_execution(mock_session):
    """Verify the full execution loop of the clinical workflow with Multi-Agent support."""
    patient_id = "pt-001"

    # Mock MCP tool responses
    # 1. get_hard_constraints
    # 2. get_clinical_signals
    # 3. get_biomarker_trends
    # 4. get_program_ruleset
    mock_session.call_tool.side_effect = [
        AsyncMock(content=[AsyncMock(text='{"patient_demographics": {"gender": "female", "age": 65}}')]),
        AsyncMock(content=[AsyncMock(text='{"signals_fired": ["htn_active"]}')]),
        AsyncMock(content=[AsyncMock(text='{"bmi": {"trend": "increasing"}}')]),
        AsyncMock(content=[AsyncMock(text='{"tier_selection_rules": [], "add_on_library": []}')]),
    ]

    # Mock Agent 1: Clinical Risk Analyzer
    mock_risk_profile = AsyncMock()
    mock_risk_profile.clinical_summary_bullets = ["High BP"]
    mock_risk_profile.supporting_signal_ids = ["htn_active"]
    mock_risk_profile.missing_signal_ids = []

    # Mock Agent 2: Policy & Package Resolver
    mock_plan = AsyncMock()
    mock_plan.ai_recommended_tier.value = "Advanced"
    mock_plan.tier_deviation_justification = "Testing"
    mock_plan.selected_add_ons = []

    # Mock Agent 3: Clinical Communicator
    mock_final = AsyncMock()
    mock_final.plan = mock_plan
    mock_final.script.clinical_conclusion = "Conclusion"
    mock_final.script.health_summary = "Summary"
    mock_final.script.recommendation_explanation = "Explanation"
    mock_final.script.add_on_highlights = []
    mock_final.script.next_steps = "Next steps"

    with patch("baml_client.async_client.b.AnalyzeClinicalRisks", return_value=mock_risk_profile), \
         patch("baml_client.async_client.b.MatchProgramRules", return_value=mock_plan), \
         patch("baml_client.async_client.b.ComposeRecommendation", return_value=mock_final):
        
        workflow = ClinicalReasoningWorkflow(mock_session)
        result = await workflow.execute(patient_id)

        assert isinstance(result, WorkflowContext)
        assert result.patient_id == patient_id
        assert result.ai_output["ai_recommended_tier"] == "Advanced"
        assert result.ai_output["communication_script"]["clinical_conclusion"] == "Conclusion"
        assert mock_session.call_tool.call_count == 4

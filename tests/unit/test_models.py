import pytest
from pydantic import ValidationError

from jarvis_operator.models import (
    NeedsHumanInputDecision,
    RejectDecision,
    ToolCallDecision,
)


def test_tool_call_decision_accepts_expected_structure():
    decision = ToolCallDecision.model_validate(
        {
            "decision_type": "tool_call",
            "tool_name": "safe_cli_run",
            "arguments": {
                "command": ["python", "-m", "pytest", "tests/unit/test_state_store.py"],
                "cwd": ".",
            },
            "confidence": 0.95,
            "explanation": "The user explicitly asked to run tests.",
        }
    )

    assert decision.tool_name == "safe_cli_run"
    assert decision.arguments["cwd"] == "."


def test_reject_decision_accepts_expected_structure():
    decision = RejectDecision.model_validate(
        {
            "decision_type": "reject",
            "reason": "The requested tool is not registered.",
            "confidence": 1.0,
            "explanation": "Only registered tools may be executed.",
        }
    )

    assert decision.reason == "The requested tool is not registered."


def test_needs_human_input_decision_accepts_expected_structure():
    decision = NeedsHumanInputDecision.model_validate(
        {
            "decision_type": "needs_human_input",
            "question": "Which test path should be executed?",
            "confidence": 0.5,
            "explanation": "The request does not include a concrete target.",
        }
    )

    assert decision.question == "Which test path should be executed?"


def test_tool_call_decision_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        ToolCallDecision.model_validate(
            {
                "decision_type": "tool_call",
                "confidence": 0.95,
                "explanation": "Missing tool payload.",
            }
        )

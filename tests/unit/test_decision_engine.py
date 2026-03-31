from pathlib import Path

from jarvis_operator.decision import LLMDecisionEngine, MockDecisionEngine
from jarvis_operator.models import RejectDecision, ToolCallDecision


class StubProvider:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def generate_structured(self, prompt: str, schema: dict) -> dict:
        return self.payload


def test_mock_decision_engine_returns_tool_call_for_run_tests():
    engine = MockDecisionEngine()

    decision = engine.decide(
        "run tests tests/unit/test_state_store.py",
        workspace_root=Path(".").resolve(),
    )

    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "safe_cli_run"
    assert decision.arguments["command"] == [
        "python",
        "-m",
        "pytest",
        "tests/unit/test_state_store.py",
    ]


def test_mock_decision_engine_returns_tool_call_for_echo():
    engine = MockDecisionEngine()

    decision = engine.decide("echo hello", workspace_root=Path(".").resolve())

    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "safe_cli_run"
    assert decision.arguments["cwd"] == str(Path(".").resolve())


def test_mock_decision_engine_returns_tool_call_for_analyze_log():
    engine = MockDecisionEngine()

    decision = engine.decide(
        "analyze log fixtures/logs/sample_error.log",
        workspace_root=Path(".").resolve(),
    )

    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "safe_cli_run"
    assert decision.arguments["command"][0:2] == ["python", "-c"]

def test_mock_decision_engine_rejects_unknown_task():
    engine = MockDecisionEngine()

    decision = engine.decide("unsupported task", workspace_root=Path(".").resolve())

    assert isinstance(decision, RejectDecision)
    assert decision.reason == "No deterministic decision rule matched the task."


def test_llm_decision_engine_accepts_valid_tool_call_payload():
    engine = LLMDecisionEngine(
        StubProvider(
            {
                "decision_type": "tool_call",
                "tool_name": "safe_cli_run",
                "arguments": {"command": ["python", "-m", "pytest"], "cwd": "."},
                "confidence": 0.9,
                "explanation": "The user asked to run tests.",
            }
        )
    )

    decision = engine.decide("run tests tests", workspace_root=Path(".").resolve())

    assert isinstance(decision, ToolCallDecision)
    assert decision.tool_name == "safe_cli_run"


def test_llm_decision_engine_rejects_invalid_payload():
    engine = LLMDecisionEngine(
        StubProvider(
            {
                "decision_type": "tool_call",
                "confidence": 0.9,
                "explanation": "Missing required fields.",
            }
        )
    )

    decision = engine.decide("run tests tests", workspace_root=Path(".").resolve())

    assert isinstance(decision, RejectDecision)
    assert decision.reason == "Invalid decision output."


def test_llm_decision_engine_converts_needs_human_input_to_reject():
    engine = LLMDecisionEngine(
        StubProvider(
            {
                "decision_type": "needs_human_input",
                "question": "Which directory should be scanned?",
                "confidence": 0.4,
                "explanation": "The task is ambiguous.",
            }
        )
    )

    decision = engine.decide("analyze something", workspace_root=Path(".").resolve())

    assert isinstance(decision, RejectDecision)
    assert decision.reason == "Which directory should be scanned?"

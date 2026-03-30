import uuid
from pathlib import Path

from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def test_run_tests_use_case_executes_real_pytest_target():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)

    result = orchestrator.run_task("run tests tests/unit/test_state_store.py")

    assert result["tool_result"]["returncode"] == 0
    assert result["validation"]["success"] is True
    assert "passed" in result["tool_result"]["stdout"]


def test_run_tests_use_case_returns_failure_explanation_for_failing_test():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)
    target = Path(f"tmp_failing_test_{uuid.uuid4().hex}.py")
    target.write_text(
        "def test_failure():\n    assert False, 'boom'\n",
        encoding="utf-8",
    )

    try:
        result = orchestrator.run_task(f"run tests {target.as_posix()}")

        assert result["tool_result"]["returncode"] != 0
        assert result["validation"]["success"] is False
        assert result["failure_explanation"]["success"] is False
        assert result["failure_explanation"]["summary"] == "Test failure detected"
        assert "FAILED" in result["failure_explanation"]["details"] or "AssertionError" in result["failure_explanation"]["details"]
    finally:
        target.unlink(missing_ok=True)

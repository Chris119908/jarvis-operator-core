from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def test_run_tests_use_case_executes_real_pytest_target():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)

    result = orchestrator.run_task("run tests tests/unit/test_state_store.py")

    assert result["tool_result"]["returncode"] == 0
    assert result["validation"]["success"] is True
    assert "passed" in result["tool_result"]["stdout"]

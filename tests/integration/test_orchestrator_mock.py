from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def test_orchestrator_runs_with_configured_safe_cli_runner():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)
    result = orchestrator.run_task("echo hello")

    assert result["tool_result"]["returncode"] == 0
    assert result["validation"]["success"] is True

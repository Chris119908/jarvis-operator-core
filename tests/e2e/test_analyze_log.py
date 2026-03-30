from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def test_analyze_log_use_case_reports_error_and_warning_counts():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)

    result = orchestrator.run_task("analyze log fixtures/logs/sample_error.log")

    assert result["tool_result"]["returncode"] == 0
    assert result["validation"]["success"] is True
    assert "errors=2 warnings=1" in result["tool_result"]["stdout"]


def test_analyze_log_use_case_works_when_pytest_cwd_changes(monkeypatch):
    monkeypatch.chdir("tests")
    config = load_config("../config.example.yaml")
    orchestrator = Orchestrator.from_config(config)

    result = orchestrator.run_task("analyze log fixtures/logs/sample_error.log")

    assert result["tool_result"]["returncode"] == 0
    assert result["validation"]["success"] is True
    assert "errors=2 warnings=1" in result["tool_result"]["stdout"]

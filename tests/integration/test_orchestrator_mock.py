from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def test_orchestrator_runs_with_mock_provider():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)
    result = orchestrator.run_task("say hello")
    assert "MOCK_RESPONSE" in result

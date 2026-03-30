from pathlib import Path

from jarvis_operator.config import AppConfig
from jarvis_operator.providers.mock_provider import MockProvider
from jarvis_operator.providers.ollama_provider import OllamaProvider
from jarvis_operator.providers.openai_compatible_provider import OpenAICompatibleProvider
from jarvis_operator.tools.registry import ToolRegistry
from jarvis_operator.orchestrator import Orchestrator


class RecordingTool:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def run(self, command: list[str], cwd: str) -> dict:
        self.calls.append({"command": command, "cwd": cwd})
        return {
            "returncode": 0,
            "stdout": "echo hello\n",
            "stderr": "",
            "timed_out": False,
        }


class FailingTool:
    def run(self, command: list[str], cwd: str) -> dict:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "failed",
            "timed_out": False,
        }


def build_config(provider_type: str, model: str, base_url: str | None = None) -> AppConfig:
    return AppConfig.model_validate(
        {
            "provider": {
                "type": provider_type,
                "model": model,
                "base_url": base_url,
                "api_key_env": "OPENAI_API_KEY",
            },
            "runtime": {
                "state_dir": ".agent",
                "workspace_root": str(REPO_ROOT),
                "log_dir": "logs",
                "log_level": "INFO",
            },
            "tools": {
                "allowed_workspaces": [str(REPO_ROOT)],
                "safe_cli": {
                    "allowed_commands": ["python", "pytest", "echo", "ls", "dir"],
                    "default_timeout_seconds": 60,
                },
            },
        }
    )


def test_simple_task_execution():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider())

    result = orchestrator.run("echo hello")

    assert result["tool_result"]["returncode"] == 0
    assert result["tool_result"]["stdout"] == "echo hello\n"
    assert result["validation"]["success"] is True


def test_correct_tool_selection():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider())

    orchestrator.run("echo hello")

    assert tool.calls == [
        {
            "command": ["python", "-c", "print('echo hello')"],
            "cwd": REPO_ROOT,
        }
    ]


def test_result_structure_includes_validation():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider())

    result = orchestrator.run("echo hello")

    assert result == {
        "tool_result": {
            "returncode": 0,
            "stdout": "echo hello\n",
            "stderr": "",
            "timed_out": False,
        },
        "validation": {
            "success": True,
            "returncode": 0,
            "timed_out": False,
            "has_output": True,
            "error_detected": False,
        },
    }


def test_failure_case_includes_failed_validation():
    registry = ToolRegistry()
    registry.register("safe_cli_run", FailingTool())
    orchestrator = Orchestrator(registry, MockProvider())

    result = orchestrator.run("echo hello")

    assert result["tool_result"]["returncode"] == 1
    assert result["validation"] == {
        "success": False,
        "returncode": 1,
        "timed_out": False,
        "has_output": False,
        "error_detected": True,
    }


def test_orchestrator_logs_task_handling(caplog):
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider())

    with caplog.at_level("INFO"):
        orchestrator.run("echo hello")

    assert "Handling task: echo hello" in caplog.text
    assert "Task validation success=True" in caplog.text


def test_from_config_selects_mock_provider():
    orchestrator = Orchestrator.from_config(build_config("mock", "mock-model"))

    assert isinstance(orchestrator.provider, MockProvider)


def test_from_config_selects_ollama_provider():
    orchestrator = Orchestrator.from_config(
        build_config("ollama", "llama3", "http://ollama.local")
    )

    assert isinstance(orchestrator.provider, OllamaProvider)
    assert orchestrator.provider.get_model_name() == "llama3"


def test_from_config_selects_openai_compatible_provider():
    orchestrator = Orchestrator.from_config(
        build_config("openai_compatible", "gpt-4o-mini", "http://openai.local/v1")
    )

    assert isinstance(orchestrator.provider, OpenAICompatibleProvider)
    assert orchestrator.provider.get_model_name() == "gpt-4o-mini"


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_from_config_uses_stable_workspace_root_when_cwd_changes(monkeypatch):
    monkeypatch.chdir("tests")

    orchestrator = Orchestrator.from_config(build_config("mock", "mock-model"))

    assert orchestrator.workspace_root == REPO_ROOT

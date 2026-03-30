from pathlib import Path

from jarvis_operator.decision import BaseDecisionEngine, LLMDecisionEngine, MockDecisionEngine
from jarvis_operator.models import RejectDecision, ToolCallDecision
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


class FlakyTool:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, command: list[str], cwd: str) -> dict:
        self.calls += 1
        if self.calls == 1:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": "temporary failure",
                "timed_out": False,
            }
        return {
            "returncode": 0,
            "stdout": "echo hello\n",
            "stderr": "",
            "timed_out": False,
        }


class RecordingDecisionEngine(BaseDecisionEngine):
    def __init__(self, decision: ToolCallDecision | RejectDecision) -> None:
        self.decision = decision
        self.tasks: list[dict] = []

    def decide(self, task: str, workspace_root: Path) -> ToolCallDecision | RejectDecision:
        self.tasks.append({"task": task, "workspace_root": workspace_root})
        return self.decision

    def decide_recovery(
        self,
        task: str,
        workspace_root: Path,
        tool_result: dict,
    ) -> ToolCallDecision | RejectDecision:
        return self.decision


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
    orchestrator = Orchestrator(registry, MockProvider(), workspace_root=REPO_ROOT)

    result = orchestrator.run("echo hello")

    assert result["tool_result"]["returncode"] == 0
    assert result["tool_result"]["stdout"] == "echo hello\n"
    assert result["validation"]["success"] is True


def test_correct_tool_selection():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider(), workspace_root=REPO_ROOT)

    orchestrator.run("echo hello")

    assert tool.calls == [
        {
            "command": ["python", "-c", "print('echo hello')"],
            "cwd": str(REPO_ROOT),
        }
    ]


def test_result_structure_includes_validation():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider(), workspace_root=REPO_ROOT)

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
    orchestrator = Orchestrator(registry, MockProvider(), workspace_root=REPO_ROOT)

    result = orchestrator.run("echo hello")

    assert result["tool_result"]["returncode"] == 1
    assert result["validation"] == {
        "success": False,
        "returncode": 1,
        "timed_out": False,
        "has_output": False,
        "error_detected": True,
    }
    assert result["recovery"]["attempted"] is True


def test_orchestrator_logs_task_handling(caplog):
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider(), workspace_root=REPO_ROOT)

    with caplog.at_level("INFO"):
        orchestrator.run("echo hello")

    assert "Handling task: echo hello" in caplog.text
    assert "Task validation success=True" in caplog.text


def test_from_config_selects_mock_provider():
    orchestrator = Orchestrator.from_config(build_config("mock", "mock-model"))

    assert isinstance(orchestrator.provider, MockProvider)
    assert isinstance(orchestrator.decision_engine, MockDecisionEngine)


def test_from_config_selects_ollama_provider():
    orchestrator = Orchestrator.from_config(
        build_config("ollama", "llama3", "http://ollama.local")
    )

    assert isinstance(orchestrator.provider, OllamaProvider)
    assert isinstance(orchestrator.decision_engine, LLMDecisionEngine)
    assert orchestrator.provider.get_model_name() == "llama3"


def test_from_config_selects_openai_compatible_provider():
    orchestrator = Orchestrator.from_config(
        build_config("openai_compatible", "gpt-4o-mini", "http://openai.local/v1")
    )

    assert isinstance(orchestrator.provider, OpenAICompatibleProvider)
    assert isinstance(orchestrator.decision_engine, LLMDecisionEngine)
    assert orchestrator.provider.get_model_name() == "gpt-4o-mini"


REPO_ROOT = Path(__file__).resolve().parents[2]


class StructuredProvider:
    def __init__(self, payload) -> None:
        if isinstance(payload, list):
            self.payloads = payload
        else:
            self.payloads = [payload]
        self.calls: list[dict] = []

    def health_check(self) -> bool:
        return True

    def generate_text(self, prompt: str) -> str:
        return ""

    def generate_structured(self, prompt: str, schema: dict) -> dict:
        self.calls.append({"prompt": prompt, "schema": schema})
        index = min(len(self.calls) - 1, len(self.payloads) - 1)
        return self.payloads[index]

    def get_model_name(self) -> str:
        return "structured-provider"


def test_from_config_uses_stable_workspace_root_when_cwd_changes(monkeypatch):
    monkeypatch.chdir("tests")

    orchestrator = Orchestrator.from_config(build_config("mock", "mock-model"))

    assert orchestrator.workspace_root == REPO_ROOT


def test_orchestrator_uses_decision_engine_for_safe_cli_task():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    decision_engine = RecordingDecisionEngine(
        ToolCallDecision(
            tool_name="safe_cli_run",
            arguments={
                "command": ["python", "-c", "print('echo hello')"],
                "cwd": str(REPO_ROOT),
            },
            confidence=1.0,
            explanation="Deterministic mock decision.",
        )
    )
    orchestrator = Orchestrator(
        registry,
        MockProvider(),
        workspace_root=REPO_ROOT,
        decision_engine=decision_engine,
    )

    orchestrator.run("echo hello")

    assert decision_engine.tasks == [{"task": "echo hello", "workspace_root": REPO_ROOT}]


def test_orchestrator_executes_llm_decision_engine_tool_call():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    provider = StructuredProvider(
        {
            "decision_type": "tool_call",
            "tool_name": "safe_cli_run",
            "arguments": {
                "command": ["python", "-c", "print('echo hello')"],
                "cwd": str(REPO_ROOT),
            },
            "confidence": 0.95,
            "explanation": "The user explicitly asked to echo text.",
        }
    )
    orchestrator = Orchestrator(
        registry,
        provider,
        workspace_root=REPO_ROOT,
        decision_engine=LLMDecisionEngine(provider),
    )

    result = orchestrator.run("echo hello")

    assert tool.calls == [
        {
            "command": ["python", "-c", "print('echo hello')"],
            "cwd": str(REPO_ROOT),
        }
    ]
    assert result["validation"]["success"] is True


def test_orchestrator_rejects_invalid_llm_decision_output():
    registry = ToolRegistry()
    registry.register("safe_cli_run", RecordingTool())
    provider = StructuredProvider(
        {
            "decision_type": "tool_call",
            "confidence": 0.2,
            "explanation": "Missing required fields.",
        }
    )
    orchestrator = Orchestrator(
        registry,
        provider,
        workspace_root=REPO_ROOT,
        decision_engine=LLMDecisionEngine(provider),
    )

    try:
        orchestrator.run("echo hello")
    except ValueError as exc:
        assert str(exc) == "Invalid decision output."
    else:
        raise AssertionError("Expected ValueError for invalid LLM decision output")


def test_orchestrator_uses_provider_backed_llm_recovery_after_failure():
    registry = ToolRegistry()
    tool = FlakyTool()
    registry.register("safe_cli_run", tool)
    provider = StructuredProvider(
        [
            {
                "decision_type": "tool_call",
                "tool_name": "safe_cli_run",
                "arguments": {
                    "command": ["python", "-c", "print('first attempt')"],
                    "cwd": str(REPO_ROOT),
                },
                "confidence": 0.9,
                "explanation": "Initial structured tool call.",
            },
            {
                "decision_type": "tool_call",
                "tool_name": "safe_cli_run",
                "arguments": {
                    "command": ["python", "-c", "print('recovery attempt')"],
                    "cwd": str(REPO_ROOT),
                },
                "confidence": 0.8,
                "explanation": "One bounded recovery attempt.",
            },
        ]
    )
    orchestrator = Orchestrator(
        registry,
        provider,
        workspace_root=REPO_ROOT,
        decision_engine=LLMDecisionEngine(provider),
    )

    result = orchestrator.run("echo hello")

    assert tool.calls == 2
    assert len(provider.calls) == 2
    assert "failed operator action" in provider.calls[1]["prompt"]
    assert result["validation"]["success"] is True
    assert result["recovery"]["attempted"] is True
    assert result["recovery"]["decision"]["arguments"]["command"] == [
        "python",
        "-c",
        "print('recovery attempt')",
    ]


def test_orchestrator_raises_for_rejected_decision():
    registry = ToolRegistry()
    registry.register("safe_cli_run", RecordingTool())
    decision_engine = RecordingDecisionEngine(
        RejectDecision(
            reason="Unsupported task.",
            confidence=1.0,
            explanation="No deterministic rule matched.",
        )
    )
    orchestrator = Orchestrator(
        registry,
        MockProvider(),
        workspace_root=REPO_ROOT,
        decision_engine=decision_engine,
    )

    try:
        orchestrator.run("unsupported task")
    except ValueError as exc:
        assert str(exc) == "Unsupported task."
    else:
        raise AssertionError("Expected ValueError for rejected decision")


def test_orchestrator_applies_one_bounded_recovery_attempt():
    registry = ToolRegistry()
    tool = FlakyTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry, MockProvider(), workspace_root=REPO_ROOT)

    result = orchestrator.run("echo hello")

    assert tool.calls == 2
    assert result["validation"]["success"] is True
    assert result["recovery"]["attempted"] is True
    assert result["initial_failure"]["validation"]["success"] is False

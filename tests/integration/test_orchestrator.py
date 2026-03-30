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


def test_simple_task_execution():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry)

    result = orchestrator.run("echo hello")

    assert result["tool_result"]["returncode"] == 0
    assert result["tool_result"]["stdout"] == "echo hello\n"
    assert result["validation"]["success"] is True


def test_correct_tool_selection():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry)

    orchestrator.run("echo hello")

    assert tool.calls == [
        {
            "command": ["python", "-c", "print('echo hello')"],
            "cwd": ".",
        }
    ]


def test_result_structure_includes_validation():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry)

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
    orchestrator = Orchestrator(registry)

    result = orchestrator.run("echo hello")

    assert result["tool_result"]["returncode"] == 1
    assert result["validation"] == {
        "success": False,
        "returncode": 1,
        "timed_out": False,
        "has_output": False,
        "error_detected": True,
    }

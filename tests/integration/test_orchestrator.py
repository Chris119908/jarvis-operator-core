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


def test_simple_task_execution():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry)

    result = orchestrator.run("echo hello")

    assert result["returncode"] == 0
    assert result["stdout"] == "echo hello\n"


def test_correct_tool_selection():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry)

    orchestrator.run("echo hello")

    assert tool.calls == [{"command": ["echo", "echo hello"], "cwd": "."}]


def test_result_structure():
    registry = ToolRegistry()
    tool = RecordingTool()
    registry.register("safe_cli_run", tool)
    orchestrator = Orchestrator(registry)

    result = orchestrator.run("echo hello")

    assert result == {
        "returncode": 0,
        "stdout": "echo hello\n",
        "stderr": "",
        "timed_out": False,
    }

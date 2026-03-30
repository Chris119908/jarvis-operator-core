import pytest

from jarvis_operator.tools.registry import ToolRegistry
from jarvis_operator.tools.safe_cli_run import SafeCLIRunner


def test_tool_registry_registers_tool():
    registry = ToolRegistry()
    tool = object()

    registry.register("safe_cli_run", tool)

    assert registry._tools["safe_cli_run"] is tool


def test_tool_registry_get_returns_registered_safe_cli_run():
    registry = ToolRegistry()
    tool = SafeCLIRunner(
        allowed_commands=["python"],
        allowed_workspaces=["."],
        default_timeout_seconds=5,
    )

    registry.register("safe_cli_run", tool)

    assert registry.get("safe_cli_run") is tool


def test_tool_registry_get_unknown_tool_raises_error():
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="Unknown tool"):
        registry.get("unknown_tool")


def test_safe_cli_run_works_via_registry(tmp_path):
    registry = ToolRegistry()
    tool = SafeCLIRunner(
        allowed_commands=["python"],
        allowed_workspaces=[str(tmp_path)],
        default_timeout_seconds=5,
    )
    registry.register("safe_cli_run", tool)

    result = registry.get("safe_cli_run").run(
        ["python", "-c", "print('hello')"],
        cwd=tmp_path,
    )

    assert result == {
        "returncode": 0,
        "stdout": "hello\n",
        "stderr": "",
        "timed_out": False,
    }

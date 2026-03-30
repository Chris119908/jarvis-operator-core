from __future__ import annotations

from jarvis_operator.config import AppConfig
from jarvis_operator.tools.registry import ToolRegistry
from jarvis_operator.tools.safe_cli_run import SafeCLIRunner


class Orchestrator:
    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry

    @classmethod
    def from_config(cls, config: AppConfig) -> "Orchestrator":
        registry = ToolRegistry()
        registry.register(
            "safe_cli_run",
            SafeCLIRunner(
                allowed_commands=config.tools.safe_cli.allowed_commands,
                allowed_workspaces=config.tools.allowed_workspaces,
                default_timeout_seconds=config.tools.safe_cli.default_timeout_seconds,
            ),
        )
        return cls(registry)

    def run(self, task: str) -> dict:
        if "echo" not in task:
            raise ValueError("No tool mapping for task")

        tool = self.tool_registry.get("safe_cli_run")
        return tool.run(["echo", task], cwd=".")

    def run_task(self, task: str) -> dict:
        return self.run(task)

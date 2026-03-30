from __future__ import annotations

from jarvis_operator.config import AppConfig
from jarvis_operator.tools.registry import ToolRegistry
from jarvis_operator.tools.safe_cli_run import SafeCLIRunner
from jarvis_operator.validation.validator import Validator


class Orchestrator:
    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry
        self.validator = Validator()

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
        tool = self.tool_registry.get("safe_cli_run")

        if task.startswith("run tests "):
            target = task.removeprefix("run tests ").strip()
            tool_result = tool.run(
                ["python", "-m", "pytest", target],
                cwd=".",
            )
        elif task.startswith("analyze log "):
            target = task.removeprefix("analyze log ").strip()
            tool_result = tool.run(
                [
                    "python",
                    "-c",
                    (
                        "from pathlib import Path; "
                        f"text=Path({target!r}).read_text(encoding='utf-8'); "
                        "lines=text.splitlines(); "
                        "errors=[line for line in lines if 'ERROR' in line]; "
                        "warnings=[line for line in lines if 'WARNING' in line]; "
                        "print(f'errors={len(errors)} warnings={len(warnings)}')"
                    ),
                ],
                cwd=".",
            )
        elif "echo" in task:
            tool_result = tool.run(
                ["python", "-c", f"print({task!r})"],
                cwd=".",
            )
        else:
            raise ValueError("No tool mapping for task")

        validation = self.validator.validate(tool_result)
        return {
            "tool_result": tool_result,
            "validation": validation,
        }

    def run_task(self, task: str) -> dict:
        return self.run(task)

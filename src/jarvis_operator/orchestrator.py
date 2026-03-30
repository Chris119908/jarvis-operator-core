from __future__ import annotations

import logging

from jarvis_operator.config import AppConfig
from jarvis_operator.providers.mock_provider import MockProvider
from jarvis_operator.providers.ollama_provider import OllamaProvider
from jarvis_operator.providers.openai_compatible_provider import OpenAICompatibleProvider
from jarvis_operator.tools.registry import ToolRegistry
from jarvis_operator.tools.safe_cli_run import SafeCLIRunner
from jarvis_operator.validation.validator import Validator

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, tool_registry: ToolRegistry, provider) -> None:
        self.tool_registry = tool_registry
        self.provider = provider
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
        if config.provider.type == "mock":
            provider = MockProvider()
        elif config.provider.type == "ollama":
            provider = OllamaProvider(
                model=config.provider.model,
                base_url=config.provider.base_url or "http://localhost:11434",
            )
        elif config.provider.type == "openai_compatible":
            provider = OpenAICompatibleProvider(
                model=config.provider.model,
                base_url=config.provider.base_url or "http://localhost:8000/v1",
            )
        else:
            raise NotImplementedError(f"Provider not yet implemented: {config.provider.type}")

        return cls(registry, provider)

    def run(self, task: str) -> dict:
        logger.info("Handling task: %s", task)
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
        elif task.startswith("create project "):
            target = task.removeprefix("create project ").strip()
            tool_result = tool.run(
                [
                    "python",
                    "-c",
                    (
                        "from pathlib import Path; "
                        f"root=Path({target!r}); "
                        "(root / 'src').mkdir(parents=True, exist_ok=True); "
                        "(root / 'tests').mkdir(parents=True, exist_ok=True); "
                        "(root / 'src' / 'sample_package').mkdir(parents=True, exist_ok=True); "
                        "(root / 'pyproject.toml').write_text('[project]\\nname = \"sample-project\"\\nversion = \"0.1.0\"\\n', encoding='utf-8'); "
                        "(root / 'README.md').write_text('# Sample Project\\n', encoding='utf-8'); "
                        "(root / 'src' / 'sample_package' / '__init__.py').write_text('__all__ = []\\n', encoding='utf-8'); "
                        "print('project scaffold created')"
                    ),
                ],
                cwd=".",
            )
        elif task.startswith("generate structure "):
            remainder = task.removeprefix("generate structure ").strip()
            spec_path, output_dir = remainder.split(" -> ", maxsplit=1)
            tool_result = tool.run(
                [
                    "python",
                    "-c",
                    (
                        "from pathlib import Path; "
                        f"spec_text=Path({spec_path!r}).read_text(encoding='utf-8'); "
                        f"root=Path({output_dir!r}); "
                        "(root / 'src').mkdir(parents=True, exist_ok=True) if 'src/' in spec_text else None; "
                        "(root / 'tests').mkdir(parents=True, exist_ok=True) if 'tests/' in spec_text else None; "
                        "(root / 'pyproject.toml').write_text('', encoding='utf-8') if 'pyproject.toml' in spec_text else None; "
                        "(root / 'README.md').write_text('', encoding='utf-8') if 'README.md' in spec_text else None; "
                        "(root / 'src' / 'sample_package').mkdir(parents=True, exist_ok=True) if 'simple package module' in spec_text else None; "
                        "(root / 'src' / 'sample_package' / '__init__.py').write_text('__all__ = []\\n', encoding='utf-8') if 'simple package module' in spec_text else None; "
                        "print('structure generated')"
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
        logger.info("Task validation success=%s", validation["success"])
        return {
            "tool_result": tool_result,
            "validation": validation,
        }

    def run_task(self, task: str) -> dict:
        return self.run(task)

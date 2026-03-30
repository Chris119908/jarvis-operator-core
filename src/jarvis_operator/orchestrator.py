from __future__ import annotations

import logging
from pathlib import Path

from jarvis_operator.config import AppConfig
from jarvis_operator.decision import BaseDecisionEngine, LLMDecisionEngine, MockDecisionEngine
from jarvis_operator.models import RejectDecision, ToolCallDecision
from jarvis_operator.providers.mock_provider import MockProvider
from jarvis_operator.providers.ollama_provider import OllamaProvider
from jarvis_operator.providers.openai_compatible_provider import OpenAICompatibleProvider
from jarvis_operator.tools.registry import ToolRegistry
from jarvis_operator.tools.safe_cli_run import SafeCLIRunner
from jarvis_operator.validation.validator import Validator

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        provider,
        workspace_root: Path | None = None,
        decision_engine: BaseDecisionEngine | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.provider = provider
        self.validator = Validator()
        self.workspace_root = workspace_root or Path.cwd().resolve()
        self.decision_engine = decision_engine or MockDecisionEngine()

    @classmethod
    def from_config(cls, config: AppConfig) -> "Orchestrator":
        workspace_root = Path(config.runtime.workspace_root).resolve()
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
            decision_engine: BaseDecisionEngine = MockDecisionEngine()
        elif config.provider.type == "ollama":
            provider = OllamaProvider(
                model=config.provider.model,
                base_url=config.provider.base_url or "http://localhost:11434",
            )
            decision_engine = LLMDecisionEngine(provider)
        elif config.provider.type == "openai_compatible":
            provider = OpenAICompatibleProvider(
                model=config.provider.model,
                base_url=config.provider.base_url or "http://localhost:8000/v1",
            )
            decision_engine = LLMDecisionEngine(provider)
        else:
            raise NotImplementedError(f"Provider not yet implemented: {config.provider.type}")

        return cls(
            registry,
            provider,
            workspace_root=workspace_root,
            decision_engine=decision_engine,
        )

    def run(self, task: str) -> dict:
        logger.info("Handling task: %s", task)

        if task.startswith("analyze log "):
            target = self._resolve_repo_path(task.removeprefix("analyze log ").strip())
            lines = target.read_text(encoding="utf-8").splitlines()
            errors = [line for line in lines if "ERROR" in line]
            warnings = [line for line in lines if "WARNING" in line]
            tool_result = {
                "returncode": 0,
                "stdout": f"errors={len(errors)} warnings={len(warnings)}\n",
                "stderr": "",
                "timed_out": False,
            }
        else:
            decision = self.decision_engine.decide(task, self.workspace_root)
            if isinstance(decision, RejectDecision):
                raise ValueError(decision.reason)

            if not isinstance(decision, ToolCallDecision):
                raise ValueError("Unsupported decision type")

            tool = self.tool_registry.get(decision.tool_name)
            tool_result = tool.run(
                decision.arguments["command"],
                cwd=decision.arguments["cwd"],
            )

        validation = self.validator.validate(tool_result)
        logger.info("Task validation success=%s", validation["success"])
        result = {
            "tool_result": tool_result,
            "validation": validation,
        }
        if not validation["success"] and not task.startswith("analyze log "):
            recovery_decision = self.decision_engine.decide_recovery(
                task,
                self.workspace_root,
                tool_result,
            )
            if isinstance(recovery_decision, ToolCallDecision):
                recovery_tool = self.tool_registry.get(recovery_decision.tool_name)
                recovery_tool_result = recovery_tool.run(
                    recovery_decision.arguments["command"],
                    cwd=recovery_decision.arguments["cwd"],
                )
                recovery_validation = self.validator.validate(recovery_tool_result)
                result["recovery"] = {
                    "attempted": True,
                    "decision": recovery_decision.model_dump(),
                    "tool_result": recovery_tool_result,
                    "validation": recovery_validation,
                }
                result["initial_failure"] = {
                    "tool_result": tool_result,
                    "validation": validation,
                }
                result["tool_result"] = recovery_tool_result
                result["validation"] = recovery_validation

        if task.startswith("run tests ") and not validation["success"]:
            result["failure_explanation"] = self._build_test_failure_explanation(tool_result)
        return result

    def run_task(self, task: str) -> dict:
        return self.run(task)

    def _resolve_repo_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path.resolve()
        return (self.workspace_root / path).resolve()

    @staticmethod
    def _build_test_failure_explanation(tool_result: dict) -> dict:
        combined_output = f"{tool_result.get('stdout', '')}\n{tool_result.get('stderr', '')}"
        for line in combined_output.splitlines():
            stripped = line.strip()
            if stripped and (
                "FAILED" in stripped
                or "AssertionError" in stripped
                or stripped.startswith("E ")
            ):
                return {
                    "success": False,
                    "summary": "Test failure detected",
                    "details": stripped[:200],
                }
        return {
            "success": False,
            "summary": "Test failure detected",
            "details": combined_output.strip()[:200],
        }

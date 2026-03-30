from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import ValidationError

from jarvis_operator.models import (
    NeedsHumanInputDecision,
    RejectDecision,
    ToolCallDecision,
)
from jarvis_operator.providers.base import BaseLLMProvider


class BaseDecisionEngine(ABC):
    @abstractmethod
    def decide(self, task: str, workspace_root: Path) -> ToolCallDecision | RejectDecision:
        raise NotImplementedError

    @abstractmethod
    def decide_recovery(
        self,
        task: str,
        workspace_root: Path,
        tool_result: dict,
    ) -> ToolCallDecision | RejectDecision:
        raise NotImplementedError


class MockDecisionEngine(BaseDecisionEngine):
    def decide(self, task: str, workspace_root: Path) -> ToolCallDecision | RejectDecision:
        if task.startswith("run tests "):
            target = task.removeprefix("run tests ").strip()
            return ToolCallDecision(
                tool_name="safe_cli_run",
                arguments={
                    "command": ["python", "-m", "pytest", target],
                    "cwd": str(workspace_root),
                },
                confidence=1.0,
                explanation="The task explicitly asks to run tests.",
            )

        if task.startswith("create project "):
            target = task.removeprefix("create project ").strip()
            return ToolCallDecision(
                tool_name="safe_cli_run",
                arguments={
                    "command": [
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
                    "cwd": str(workspace_root),
                },
                confidence=1.0,
                explanation="The task explicitly asks to create a project scaffold.",
            )

        if task.startswith("generate structure "):
            remainder = task.removeprefix("generate structure ").strip()
            spec_path, output_dir = remainder.split(" -> ", maxsplit=1)
            return ToolCallDecision(
                tool_name="safe_cli_run",
                arguments={
                    "command": [
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
                    "cwd": str(workspace_root),
                },
                confidence=1.0,
                explanation="The task explicitly asks to generate a file structure.",
            )

        if "echo" in task:
            return ToolCallDecision(
                tool_name="safe_cli_run",
                arguments={
                    "command": ["python", "-c", f"print({task!r})"],
                    "cwd": str(workspace_root),
                },
                confidence=1.0,
                explanation="The task explicitly asks to echo text.",
            )

        return RejectDecision(
            reason="No deterministic decision rule matched the task.",
            confidence=1.0,
            explanation="The mock decision engine only supports the current deterministic V1 task patterns.",
        )

    def decide_recovery(
        self,
        task: str,
        workspace_root: Path,
        tool_result: dict,
    ) -> ToolCallDecision | RejectDecision:
        decision = self.decide(task, workspace_root)
        if isinstance(decision, ToolCallDecision):
            return decision

        return RejectDecision(
            reason="No bounded recovery decision is available.",
            confidence=1.0,
            explanation="The mock decision engine could not produce a deterministic recovery action.",
        )


class LLMDecisionEngine(BaseDecisionEngine):
    def __init__(self, provider: BaseLLMProvider) -> None:
        self.provider = provider

    def decide(self, task: str, workspace_root: Path) -> ToolCallDecision | RejectDecision:
        schema = {
            "decision_type": "tool_call | reject | needs_human_input",
            "tool_name": "string",
            "arguments": "object",
            "reason": "string",
            "question": "string",
            "confidence": "float",
            "explanation": "string",
        }
        prompt = (
            "Return the next operator decision as structured data. "
            f"Workspace root: {workspace_root}. "
            f"Task: {task}"
        )
        raw = self.provider.generate_structured(prompt, schema)
        if not isinstance(raw, dict):
            return self._invalid_output("The decision engine rejected non-object structured provider output.")
        decision_type = raw.get("decision_type")

        try:
            if decision_type == "tool_call":
                decision = ToolCallDecision.model_validate(raw)
                return self._validate_tool_call(decision)
            if decision_type == "reject":
                return RejectDecision.model_validate(raw)
            if decision_type == "needs_human_input":
                validated = NeedsHumanInputDecision.model_validate(raw)
                return RejectDecision(
                    reason=validated.question,
                    confidence=validated.confidence,
                    explanation=validated.explanation,
                )
        except ValidationError:
            return self._invalid_output(
                "The decision engine rejected invalid structured provider output."
            )

        return self._invalid_output(
            "The decision engine rejected unsupported structured provider output."
        )

    @staticmethod
    def _validate_tool_call(decision: ToolCallDecision) -> ToolCallDecision | RejectDecision:
        if decision.tool_name != "safe_cli_run":
            return LLMDecisionEngine._invalid_output(
                "The decision engine rejected an unregistered tool."
            )

        command = decision.arguments.get("command")
        cwd = decision.arguments.get("cwd")
        if not isinstance(command, list) or not command or not all(
            isinstance(part, str) and part for part in command
        ):
            return LLMDecisionEngine._invalid_output(
                "The decision engine rejected a tool call with an invalid command."
            )
        if not isinstance(cwd, str) or not cwd.strip():
            return LLMDecisionEngine._invalid_output(
                "The decision engine rejected a tool call with an invalid cwd."
            )
        return decision

    @staticmethod
    def _invalid_output(explanation: str) -> RejectDecision:
        return RejectDecision(
            reason="Invalid decision output.",
            confidence=1.0,
            explanation=explanation,
        )

    def decide_recovery(
        self,
        task: str,
        workspace_root: Path,
        tool_result: dict,
    ) -> ToolCallDecision | RejectDecision:
        return RejectDecision(
            reason="No bounded recovery decision is available.",
            confidence=1.0,
            explanation="The minimal LLM decision engine does not yet request follow-up recovery actions.",
        )

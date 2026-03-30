from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    message: str = ""


class BaseDecision(BaseModel):
    decision_type: Literal["tool_call", "reject", "needs_human_input"]
    confidence: float
    explanation: str


class ToolCallDecision(BaseDecision):
    decision_type: Literal["tool_call"] = "tool_call"
    tool_name: str
    arguments: dict[str, Any]


class RejectDecision(BaseDecision):
    decision_type: Literal["reject"] = "reject"
    reason: str


class NeedsHumanInputDecision(BaseDecision):
    decision_type: Literal["needs_human_input"] = "needs_human_input"
    question: str


Decision = Union[ToolCallDecision, RejectDecision, NeedsHumanInputDecision]

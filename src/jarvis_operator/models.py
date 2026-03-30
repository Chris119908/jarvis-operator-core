from __future__ import annotations

from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    message: str = ""

from __future__ import annotations


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, object] = {}

    def register(self, name: str, tool: object) -> None:
        self._tools[name] = tool

    def get(self, name: str) -> object:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

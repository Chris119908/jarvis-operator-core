from __future__ import annotations

import subprocess
from pathlib import Path


class SafeCLIRunner:
    def __init__(self, allowed_commands: list[str], allowed_workspaces: list[str], default_timeout_seconds: int = 60) -> None:
        self.allowed_commands = set(allowed_commands)
        self.allowed_workspaces = [Path(p).resolve() for p in allowed_workspaces]
        self.default_timeout_seconds = default_timeout_seconds

    def _is_workspace_allowed(self, cwd: str | Path) -> bool:
        resolved = Path(cwd).resolve()
        return any(
            resolved == allowed or allowed in resolved.parents
            for allowed in self.allowed_workspaces
        )

    def run(self, command: list[str], cwd: str | Path, timeout_seconds: int | None = None) -> dict:
        if not command:
            raise ValueError("Command must not be empty")

        if command[0] not in self.allowed_commands:
            raise PermissionError(f"Command not allowed: {command[0]}")

        if not self._is_workspace_allowed(cwd):
            raise PermissionError(f"Workspace not allowed: {cwd}")

        try:
            result = subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout_seconds or self.default_timeout_seconds,
                shell=False,
                check=False,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "returncode": None,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "timed_out": True,
            }

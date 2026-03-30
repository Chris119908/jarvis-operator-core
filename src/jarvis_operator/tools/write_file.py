from __future__ import annotations

from pathlib import Path


def _resolve_allowed_path(path: str | Path, allowed_workspaces: list[str | Path] | None) -> Path:
    resolved_path = Path(path).resolve()
    workspaces = allowed_workspaces or ["."]
    allowed_roots = [Path(workspace).resolve() for workspace in workspaces]

    if not any(resolved_path == root or root in resolved_path.parents for root in allowed_roots):
        raise PermissionError(f"Path not allowed: {path}")

    return resolved_path


def write_file(
    path: str | Path,
    content: str,
    allowed_workspaces: list[str | Path] | None = None,
) -> dict[str, int | bool]:
    resolved_path = _resolve_allowed_path(path, allowed_workspaces)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(content, encoding="utf-8")
    return {
        "success": True,
        "bytes_written": len(content.encode("utf-8")),
    }

from __future__ import annotations
from pathlib import Path

def list_dir(path: str | Path) -> list[str]:
    return sorted(p.name for p in Path(path).iterdir())

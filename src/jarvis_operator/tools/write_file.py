from __future__ import annotations
from pathlib import Path

def write_file(path: str | Path, content: str) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return len(content.encode("utf-8"))

from __future__ import annotations

def validate_non_empty(value: str) -> bool:
    return bool(value and value.strip())

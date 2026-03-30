from __future__ import annotations


def validate_non_empty(value: str) -> bool:
    return bool(value and value.strip())


class Validator:
    def validate(self, result: dict) -> dict:
        returncode = result.get("returncode")
        timed_out = bool(result.get("timed_out", False))
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")

        return {
            "success": returncode == 0 and not timed_out,
            "returncode": returncode,
            "timed_out": timed_out,
            "has_output": bool(stdout),
            "error_detected": bool(stderr),
        }

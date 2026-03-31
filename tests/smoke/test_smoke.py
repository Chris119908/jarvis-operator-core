import shutil
import subprocess
import sys
from pathlib import Path

from jarvis_operator.config import load_config


def _resolve_console_script() -> str | None:
    executable = shutil.which("jarvis-operator")
    if executable is not None:
        return executable

    scripts_path = Path(sys.executable).resolve().parent
    candidates = [
        scripts_path / "jarvis-operator",
        scripts_path / "jarvis-operator.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return None


def test_smoke_loads_config():
    config = load_config("config.example.yaml")
    assert config.provider.type == "mock"


def test_smoke_console_script_doctor_runs():
    executable = _resolve_console_script()

    assert executable is not None

    result = subprocess.run(
        [executable, "doctor"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Jarvis Operator doctor check" in result.stdout


def test_smoke_console_script_run_executes_task():
    executable = _resolve_console_script()

    assert executable is not None

    result = subprocess.run(
        [executable, "run", "echo smoke"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "tool_result" in result.stdout
    assert "validation" in result.stdout

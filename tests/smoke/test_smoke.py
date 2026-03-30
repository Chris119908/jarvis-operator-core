import shutil
import subprocess

from jarvis_operator.config import load_config


def test_smoke_loads_config():
    config = load_config("config.example.yaml")
    assert config.provider.type == "mock"


def test_smoke_console_script_doctor_runs():
    executable = shutil.which("jarvis-operator")

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
    executable = shutil.which("jarvis-operator")

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

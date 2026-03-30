import subprocess

import pytest

from jarvis_operator.tools.safe_cli_run import SafeCLIRunner


def test_safe_cli_allows_allowed_command(tmp_path):
    runner = SafeCLIRunner(
        allowed_commands=["python"],
        allowed_workspaces=[str(tmp_path)],
        default_timeout_seconds=5,
    )
    result = runner.run(["python", "-c", "print('hello')"], cwd=tmp_path)

    assert result["returncode"] == 0
    assert result["stdout"].strip() == "hello"
    assert result["stderr"] == ""
    assert result["timed_out"] is False


def test_safe_cli_blocks_forbidden_command(tmp_path):
    runner = SafeCLIRunner(
        allowed_commands=["echo"],
        allowed_workspaces=[str(tmp_path)],
        default_timeout_seconds=5,
    )

    with pytest.raises(PermissionError, match="Command not allowed"):
        runner.run(["rm", "-rf", "/"], cwd=tmp_path)


def test_safe_cli_rejects_empty_command(tmp_path):
    runner = SafeCLIRunner(
        allowed_commands=["echo"],
        allowed_workspaces=[str(tmp_path)],
        default_timeout_seconds=5,
    )

    with pytest.raises(ValueError, match="must not be empty"):
        runner.run([], cwd=tmp_path)


def test_safe_cli_blocks_disallowed_workspace(tmp_path):
    allowed_workspace = tmp_path / "allowed"
    blocked_workspace = tmp_path / "blocked"
    allowed_workspace.mkdir()
    blocked_workspace.mkdir()

    runner = SafeCLIRunner(
        allowed_commands=["echo"],
        allowed_workspaces=[str(allowed_workspace)],
        default_timeout_seconds=5,
    )

    with pytest.raises(PermissionError, match="Workspace not allowed"):
        runner.run(["echo", "hello"], cwd=blocked_workspace)


def test_safe_cli_uses_shell_false(tmp_path, monkeypatch):
    observed = {}

    def fake_run(*args, **kwargs):
        observed["command"] = args[0]
        observed["cwd"] = kwargs["cwd"]
        observed["shell"] = kwargs["shell"]
        return subprocess.CompletedProcess(args[0], 0, stdout="ok", stderr="")

    runner = SafeCLIRunner(
        allowed_commands=["echo"],
        allowed_workspaces=[str(tmp_path)],
        default_timeout_seconds=5,
    )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = runner.run(["echo", "hello"], cwd=tmp_path)

    assert observed["command"] == ["echo", "hello"]
    assert observed["cwd"] == str(tmp_path)
    assert observed["shell"] is False
    assert result == {
        "returncode": 0,
        "stdout": "ok",
        "stderr": "",
        "timed_out": False,
    }

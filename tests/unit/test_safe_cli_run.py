from jarvis_operator.tools.safe_cli_run import SafeCLIRunner


def test_safe_cli_allows_echo(tmp_path):
    runner = SafeCLIRunner(
        allowed_commands=["echo", "python"],
        allowed_workspaces=[str(tmp_path)],
        default_timeout_seconds=5,
    )
    result = runner.run(["echo", "hello"], cwd=tmp_path)
    assert result["returncode"] == 0


def test_safe_cli_blocks_forbidden_command(tmp_path):
    runner = SafeCLIRunner(
        allowed_commands=["echo"],
        allowed_workspaces=[str(tmp_path)],
        default_timeout_seconds=5,
    )

    try:
        runner.run(["rm", "-rf", "/"], cwd=tmp_path)
        assert False, "Expected PermissionError"
    except PermissionError:
        assert True

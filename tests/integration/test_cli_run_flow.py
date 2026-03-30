from jarvis_operator.cli import cmd_run


def test_cli_run_flow():
    rc = cmd_run("hello world", "config.example.yaml")
    assert rc == 0

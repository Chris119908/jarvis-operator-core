import sys

from jarvis_operator import cli


def test_build_parser_uses_expected_default_config():
    parser = cli.build_parser()
    args = parser.parse_args(["doctor"])

    assert args.command == "doctor"
    assert args.config == "config.example.yaml"


def test_main_runs_doctor_command(monkeypatch):
    called = {}

    def fake_cmd_doctor(config_path: str) -> int:
        called["config_path"] = config_path
        return 0

    monkeypatch.setattr(cli, "cmd_doctor", fake_cmd_doctor)
    monkeypatch.setattr(sys, "argv", ["jarvis-operator", "doctor"])

    assert cli.main() == 0
    assert called["config_path"] == "config.example.yaml"

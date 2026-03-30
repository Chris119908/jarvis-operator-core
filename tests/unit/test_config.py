import pytest
from pydantic import ValidationError

from jarvis_operator.config import load_config


def test_load_config_with_valid_config():
    config = load_config("config.example.yaml")

    assert config.provider.type == "mock"
    assert "python" in config.tools.safe_cli.allowed_commands


def test_load_config_with_invalid_config(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
runtime:
  state_dir: ".agent"
  workspace_root: "."
  log_dir: "logs"
  log_level: "INFO"
tools:
  allowed_workspaces:
    - "."
  safe_cli:
    allowed_commands:
      - "python"
    default_timeout_seconds: 60
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_path)


def test_load_config_with_missing_file():
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config("missing-config.yaml")

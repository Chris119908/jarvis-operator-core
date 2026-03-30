from pathlib import Path

import pytest

from jarvis_operator.config import load_config


def test_load_config():
    config = load_config("config.example.yaml")
    assert config.provider.type == "mock"
    assert "python" in config.tools.safe_cli.allowed_commands


def test_load_config_accepts_path_instance():
    config = load_config(Path("config.example.yaml"))
    assert config.runtime.state_dir == ".agent"


def test_load_config_rejects_empty_yaml(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="YAML mapping"):
        load_config(config_path)

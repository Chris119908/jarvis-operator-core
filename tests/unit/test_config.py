from jarvis_operator.config import load_config


def test_load_config():
    config = load_config("config.example.yaml")
    assert config.provider.type == "mock"
    assert "python" in config.tools.safe_cli.allowed_commands

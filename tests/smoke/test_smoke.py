from jarvis_operator.config import load_config


def test_smoke_loads_config():
    config = load_config("config.example.yaml")
    assert config.provider.type == "mock"

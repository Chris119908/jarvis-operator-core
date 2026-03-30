import pytest
import requests

from jarvis_operator.providers.ollama_provider import OllamaProvider
from jarvis_operator.providers.openai_compatible_provider import OpenAICompatibleProvider


def test_ollama_provider_exposes_placeholder_model_name():
    provider = OllamaProvider()

    assert provider.get_model_name() == "llama3"


def test_ollama_provider_surfaces_clear_runtime_error_when_unreachable(monkeypatch):
    provider = OllamaProvider()

    def fake_get(url: str, timeout: int):
        raise requests.ConnectionError("connection failed")

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(RuntimeError, match="Ollama health check failed"):
        provider.health_check()


def test_openai_compatible_provider_exposes_placeholder_model_name():
    provider = OpenAICompatibleProvider()

    assert provider.get_model_name() == "gpt-4o-mini"


def test_openai_compatible_provider_surfaces_clear_runtime_error_when_unreachable(monkeypatch):
    provider = OpenAICompatibleProvider()

    def fake_get(url: str, headers: dict, timeout: int):
        raise requests.ConnectionError("connection failed")

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(RuntimeError, match="OpenAI-compatible health check failed"):
        provider.health_check()

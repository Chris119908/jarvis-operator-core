import requests

from jarvis_operator.providers.ollama_provider import OllamaProvider


class DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_ollama_provider_health_check(monkeypatch):
    provider = OllamaProvider(model="llama3", base_url="http://ollama.local")

    def fake_get(url: str, timeout: int):
        assert url == "http://ollama.local/api/tags"
        assert timeout == 5
        return DummyResponse({"models": []})

    monkeypatch.setattr(requests, "get", fake_get)

    assert provider.health_check() is True


def test_ollama_provider_generate_text(monkeypatch):
    provider = OllamaProvider(model="llama3", base_url="http://ollama.local")

    def fake_post(url: str, json: dict, timeout: int):
        assert url == "http://ollama.local/api/generate"
        assert json == {
            "model": "llama3",
            "prompt": "hello",
            "stream": False,
        }
        assert timeout == 30
        return DummyResponse({"response": "hi there"})

    monkeypatch.setattr(requests, "post", fake_post)

    assert provider.generate_text("hello") == "hi there"


def test_ollama_provider_generate_structured(monkeypatch):
    provider = OllamaProvider(model="llama3", base_url="http://ollama.local")

    def fake_generate_text(prompt: str) -> str:
        assert "Return JSON matching this schema" in prompt
        return '{"status": "ok"}'

    monkeypatch.setattr(provider, "generate_text", fake_generate_text)

    assert provider.generate_structured("hello", {"type": "object"}) == {"status": "ok"}


def test_ollama_provider_get_model_name():
    provider = OllamaProvider(model="llama3.2")

    assert provider.get_model_name() == "llama3.2"

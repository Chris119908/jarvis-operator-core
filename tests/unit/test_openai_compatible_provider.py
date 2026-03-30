import requests

from jarvis_operator.providers.openai_compatible_provider import OpenAICompatibleProvider


class DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_openai_compatible_provider_health_check(monkeypatch):
    provider = OpenAICompatibleProvider(
        model="gpt-4o-mini",
        base_url="http://openai.local/v1",
        api_key="secret",
    )

    def fake_get(url: str, headers: dict, timeout: int):
        assert url == "http://openai.local/v1/models"
        assert headers["Authorization"] == "Bearer secret"
        assert timeout == 5
        return DummyResponse({"data": []})

    monkeypatch.setattr(requests, "get", fake_get)

    assert provider.health_check() is True


def test_openai_compatible_provider_generate_text(monkeypatch):
    provider = OpenAICompatibleProvider(
        model="gpt-4o-mini",
        base_url="http://openai.local/v1",
        api_key="secret",
    )

    def fake_post(url: str, headers: dict, json: dict, timeout: int):
        assert url == "http://openai.local/v1/chat/completions"
        assert headers["Authorization"] == "Bearer secret"
        assert json == {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "hello"}],
        }
        assert timeout == 30
        return DummyResponse(
            {
                "choices": [
                    {
                        "message": {"content": "hi there"},
                    }
                ]
            }
        )

    monkeypatch.setattr(requests, "post", fake_post)

    assert provider.generate_text("hello") == "hi there"


def test_openai_compatible_provider_generate_structured(monkeypatch):
    provider = OpenAICompatibleProvider()

    def fake_generate_text(prompt: str) -> str:
        assert "Return JSON matching this schema" in prompt
        return '{"status": "ok"}'

    monkeypatch.setattr(provider, "generate_text", fake_generate_text)

    assert provider.generate_structured("hello", {"type": "object"}) == {"status": "ok"}


def test_openai_compatible_provider_get_model_name():
    provider = OpenAICompatibleProvider(model="gpt-4.1-mini")

    assert provider.get_model_name() == "gpt-4.1-mini"

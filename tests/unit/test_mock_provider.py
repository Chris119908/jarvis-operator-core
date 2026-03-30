from jarvis_operator.providers.mock_provider import MockProvider


def test_mock_provider_health_check():
    provider = MockProvider()

    assert provider.health_check() is True


def test_mock_provider_generate_text():
    provider = MockProvider()

    assert provider.generate_text("hello") == "MOCK_RESPONSE: hello"


def test_mock_provider_generate_structured():
    provider = MockProvider()
    schema = {"name": {"type": "string"}, "count": {"type": "integer"}}

    assert provider.generate_structured("hello", schema) == {
        "status": "mocked",
        "prompt_preview": "hello",
        "schema_keys": ["name", "count"],
    }


def test_mock_provider_get_model_name():
    provider = MockProvider()

    assert provider.get_model_name() == "mock-model"

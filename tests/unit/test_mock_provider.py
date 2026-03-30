from jarvis_operator.providers.mock_provider import MockProvider


def test_mock_provider_basic():
    provider = MockProvider()
    assert provider.health_check() is True
    assert provider.get_model_name() == "mock-model"
    assert "MOCK_RESPONSE" in provider.generate_text("hello")

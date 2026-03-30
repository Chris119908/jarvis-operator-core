import pytest

from jarvis_operator.providers.ollama_provider import OllamaProvider
from jarvis_operator.providers.openai_compatible_provider import OpenAICompatibleProvider


def test_ollama_provider_exposes_placeholder_model_name():
    provider = OllamaProvider()

    assert provider.get_model_name() == "ollama-unconfigured"


def test_ollama_provider_raises_clear_not_implemented_errors():
    provider = OllamaProvider()

    with pytest.raises(NotImplementedError, match="planned but not yet implemented"):
        provider.health_check()

    with pytest.raises(NotImplementedError, match="planned but not yet implemented"):
        provider.generate_text("hello")

    with pytest.raises(NotImplementedError, match="planned but not yet implemented"):
        provider.generate_structured("hello", {"type": "object"})


def test_openai_compatible_provider_exposes_placeholder_model_name():
    provider = OpenAICompatibleProvider()

    assert provider.get_model_name() == "openai-compatible-unconfigured"


def test_openai_compatible_provider_raises_clear_not_implemented_errors():
    provider = OpenAICompatibleProvider()

    with pytest.raises(NotImplementedError, match="planned but not yet implemented"):
        provider.health_check()

    with pytest.raises(NotImplementedError, match="planned but not yet implemented"):
        provider.generate_text("hello")

    with pytest.raises(NotImplementedError, match="planned but not yet implemented"):
        provider.generate_structured("hello", {"type": "object"})

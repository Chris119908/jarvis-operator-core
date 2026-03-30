from __future__ import annotations

from typing import Any

from jarvis_operator.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def health_check(self) -> bool:
        raise NotImplementedError("OllamaProvider is planned but not yet implemented.")

    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError("OllamaProvider is planned but not yet implemented.")

    def generate_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("OllamaProvider is planned but not yet implemented.")

    def get_model_name(self) -> str:
        return "ollama-unconfigured"

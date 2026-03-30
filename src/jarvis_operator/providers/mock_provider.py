from __future__ import annotations

from typing import Any

from jarvis_operator.providers.base import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    def health_check(self) -> bool:
        return True

    def generate_text(self, prompt: str) -> str:
        return f"MOCK_RESPONSE: {prompt[:80]}"

    def generate_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "mocked",
            "prompt_preview": prompt[:80],
            "schema_keys": list(schema.keys()),
        }

    def get_model_name(self) -> str:
        return "mock-model"

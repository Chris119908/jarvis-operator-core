from __future__ import annotations

import json
from typing import Any

import requests

from jarvis_operator.providers.base import BaseLLMProvider


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "test-key",
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def health_check(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._headers,
                timeout=5,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"OpenAI-compatible health check failed: {exc}") from exc
        return True

    def generate_text(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"OpenAI-compatible text generation failed: {exc}") from exc

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def generate_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        structured_prompt = f"{prompt}\nReturn JSON matching this schema: {json.dumps(schema, sort_keys=True)}"
        text = self.generate_text(structured_prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OpenAI-compatible structured generation returned invalid JSON.") from exc

    def get_model_name(self) -> str:
        return self.model

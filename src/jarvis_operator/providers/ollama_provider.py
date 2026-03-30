from __future__ import annotations

import json
from typing import Any

import requests

from jarvis_operator.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Ollama health check failed: {exc}") from exc
        return True

    def generate_text(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Ollama text generation failed: {exc}") from exc

        data = response.json()
        return data["response"]

    def generate_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        structured_prompt = f"{prompt}\nReturn JSON matching this schema: {json.dumps(schema, sort_keys=True)}"
        text = self.generate_text(structured_prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama structured generation returned invalid JSON.") from exc

    def get_model_name(self) -> str:
        return self.model

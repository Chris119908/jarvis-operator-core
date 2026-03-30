from __future__ import annotations

from jarvis_operator.config import AppConfig
from jarvis_operator.providers.mock_provider import MockProvider


class Orchestrator:
    def __init__(self, provider) -> None:
        self.provider = provider

    @classmethod
    def from_config(cls, config: AppConfig) -> "Orchestrator":
        provider_type = config.provider.type
        if provider_type == "mock":
            provider = MockProvider()
        else:
            raise NotImplementedError(f"Provider not yet implemented: {provider_type}")
        return cls(provider)

    def run_task(self, task: str) -> str:
        return self.provider.generate_text(f"Task: {task}")

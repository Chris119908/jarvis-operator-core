# LLM_PROVIDER_SPEC.md

## Goal
The rest of the application must not depend on a specific LLM vendor.

## Base Interface
Each provider must implement:

- health_check() -> bool
- generate_text(prompt: str) -> str
- generate_structured(prompt: str, schema: dict) -> dict
- get_model_name() -> str

## Required V1 Providers
- MockProvider
- OllamaProvider
- OpenAICompatibleProvider

## Provider Rules
- MockProvider is mandatory for deterministic tests
- Real providers must fail clearly on connectivity or auth issues
- The application core must only depend on the shared interface
- Structured output may fall back to JSON parsing when needed

## Testing Requirements
- MockProvider unit tests required
- Real providers should have lightweight initialization tests only

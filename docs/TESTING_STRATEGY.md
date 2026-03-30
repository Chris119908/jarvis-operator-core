# TESTING_STRATEGY.md

## Principle
No feature is complete without automated evidence.

## Test Levels

### Unit
Every core function and class should have unit tests.

### Integration
Each workflow crossing multiple modules should have integration tests.

### End-to-End
Each V1 use case needs an E2E test.

### Smoke
A smoke check must confirm installability and startup behavior.

## Standard Commands
```bash
pytest tests/unit
pytest tests/integration
pytest tests/e2e
pytest tests/smoke
```

## Mocking
- Use MockProvider for deterministic tests
- Prefer fixtures over live LLM calls in automated test suites

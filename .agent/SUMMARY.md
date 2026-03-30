# Summary

The V2 decision layer remains green, and the first V2.2 hardening step is now in place.

Evidence captured:
- `src/jarvis_operator/models.py` includes structured decision models for `tool_call`, `reject`, and `needs_human_input`
- `src/jarvis_operator/decision.py` defines `BaseDecisionEngine`, `MockDecisionEngine`, and `LLMDecisionEngine`
- `src/jarvis_operator/orchestrator.py` routes safe_cli_run-backed tasks through the decision engine layer
- the orchestrator selects `MockDecisionEngine` for the mock provider and `LLMDecisionEngine` for real providers
- one bounded deterministic recovery attempt is now supported after a failed decision-based tool execution
- `tests/integration/test_orchestrator.py` proves that valid structured LLM decisions execute through the orchestrator and invalid structured outputs are rejected safely
- `LLMDecisionEngine` now rejects non-object provider outputs, unknown tool names, invalid command payloads, and blank `cwd` values before execution

Validation result:
- `python -m pytest tests/unit/test_decision_engine.py`
- `python -m pytest tests`

Status:
- first V2.2 hardening step completed without changing the orchestrator architecture

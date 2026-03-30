# Summary

The V2 decision layer remains green, and the bounded V2.2 recovery path is now evidenced through the orchestrator.

Evidence captured:
- `src/jarvis_operator/models.py` includes structured decision models for `tool_call`, `reject`, and `needs_human_input`
- `src/jarvis_operator/decision.py` defines `BaseDecisionEngine`, `MockDecisionEngine`, and `LLMDecisionEngine`
- `src/jarvis_operator/orchestrator.py` routes safe_cli_run-backed tasks through the decision engine layer
- the orchestrator selects `MockDecisionEngine` for the mock provider and `LLMDecisionEngine` for real providers
- one bounded deterministic recovery attempt is now supported after a failed decision-based tool execution
- `tests/integration/test_orchestrator.py` proves that valid structured LLM decisions execute through the orchestrator and invalid structured outputs are rejected safely
- `LLMDecisionEngine` now rejects non-object provider outputs, unknown tool names, invalid command payloads, and blank `cwd` values before execution
- `LLMDecisionEngine` now also requests one bounded provider-backed recovery decision and subjects that follow-up output to the same strict validation
- `tests/integration/test_orchestrator.py` now also proves that a failed first tool execution causes the orchestrator to request and execute one provider-backed LLM recovery decision

Validation result:
- `python -m pytest tests/integration/test_orchestrator.py`
- `python -m pytest tests`

Status:
- bounded V2.2 recovery path completed and evidenced without changing the orchestrator architecture

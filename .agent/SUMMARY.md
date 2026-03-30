# Summary

Current iteration wired provider selection into the runtime path.

Evidence captured:
- `src/jarvis_operator/orchestrator.py`
- `tests/integration/test_orchestrator.py`
- `tests/integration/test_orchestrator_mock.py`

Validation result:
- `python -m pytest tests/integration/test_orchestrator.py tests/integration/test_orchestrator_mock.py tests/integration/test_cli_run_flow.py`
- `python -m pytest tests`

Current focus:
- keep progressing in the smallest tested increments
- align implementation with tool contracts
- avoid scope expansion beyond the v1 docs

# Summary

Packaging/CLI smoke-test reliability issue is now fixed in strict scope.

Completed in this iteration:
- Verified `pyproject.toml` already contains the correct console script mapping: `jarvis-operator = "jarvis_operator.cli:main"`.
- Hardened smoke tests in `tests/smoke/test_smoke.py` to resolve `jarvis-operator` via `PATH` first and then fall back to the active Python scripts directory (`Path(sys.executable).parent`) including a Windows `.exe` candidate.
- Kept CLI implementation unchanged because the packaging entrypoint was already correct.

Validation evidence:
- `python -m pip install -e .` ✅
- `python -m pytest tests/smoke/test_smoke.py` ✅ (3 passed)
- `python -m pytest tests` ✅ (86 passed)

Status:
- Smoke tests no longer depend solely on ambient PATH and now pass after editable install in this environment.

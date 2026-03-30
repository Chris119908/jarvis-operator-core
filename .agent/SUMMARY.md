# Summary

Minimal pytest CI is now configured and slightly hardened for the repository.

Evidence captured:
- `.github/workflows/tests.yml`
- workflow steps aligned with `pyproject.toml`
- Python's scripts directory is exported to `PATH` before pytest runs

Validation result:
- workflow uses `python -m pip install -e .`
- workflow exposes the installed console-script location to GitHub Actions
- workflow runs `python -m pytest tests`
- matrix covers Python `3.11` and `3.12`

Status:
- branch updated with a focused CI reliability fix

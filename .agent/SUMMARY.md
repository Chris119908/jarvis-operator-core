# Summary

Minimal pytest CI is now configured for the repository.

Evidence captured:
- `.github/workflows/tests.yml`
- workflow steps aligned with `pyproject.toml`

Validation result:
- workflow uses `python -m pip install -e .`
- workflow runs `python -m pytest tests`
- matrix covers Python `3.11` and `3.12`

Status:
- branch ready for review with CI included

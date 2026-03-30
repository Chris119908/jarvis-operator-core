import shutil
import uuid
from pathlib import Path

from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def test_create_project_use_case_creates_expected_scaffold():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)
    target = Path(f".tmp_create_project_{uuid.uuid4().hex}")

    try:
        result = orchestrator.run_task(f"create project {target.as_posix()}")

        assert result["tool_result"]["returncode"] == 0
        assert result["validation"]["success"] is True
        assert (target / "src").is_dir()
        assert (target / "tests").is_dir()
        assert (target / "pyproject.toml").is_file()
        assert (target / "README.md").is_file()
        assert (target / "src" / "sample_package" / "__init__.py").is_file()
    finally:
        shutil.rmtree(target, ignore_errors=True)

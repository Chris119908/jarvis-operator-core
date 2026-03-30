import shutil
import uuid
from pathlib import Path

from jarvis_operator.config import load_config
from jarvis_operator.orchestrator import Orchestrator


def test_generate_structure_use_case_creates_structure_from_spec():
    config = load_config("config.example.yaml")
    orchestrator = Orchestrator.from_config(config)
    target = Path(f".tmp_generate_structure_{uuid.uuid4().hex}")

    try:
        task = (
            "generate structure "
            "fixtures/specs/sample_project_request.md"
            f" -> {target.as_posix()}"
        )
        result = orchestrator.run_task(task)

        assert result["tool_result"]["returncode"] == 0
        assert result["validation"]["success"] is True
        assert (target / "src").is_dir()
        assert (target / "tests").is_dir()
        assert (target / "pyproject.toml").is_file()
        assert (target / "README.md").is_file()
        assert (target / "src" / "sample_package" / "__init__.py").is_file()
    finally:
        shutil.rmtree(target, ignore_errors=True)

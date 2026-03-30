from jarvis_operator.validation.validator import Validator


def test_validator_reports_successful_execution():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": 0,
            "stdout": "ok\n",
            "stderr": "",
            "timed_out": False,
        }
    )

    assert result == {
        "success": True,
        "returncode": 0,
        "timed_out": False,
        "has_output": True,
        "error_detected": False,
    }


def test_validator_reports_failed_execution():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": 1,
            "stdout": "",
            "stderr": "",
            "timed_out": False,
        }
    )

    assert result["success"] is False
    assert result["returncode"] == 1


def test_validator_reports_timeout():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "timed_out": True,
        }
    )

    assert result["success"] is False
    assert result["timed_out"] is True


def test_validator_reports_returncode_none_as_failure():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": None,
            "stdout": "ok",
            "stderr": "",
            "timed_out": False,
        }
    )

    assert result["success"] is False
    assert result["returncode"] is None


def test_validator_detects_output():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": 0,
            "stdout": "some output",
            "stderr": "",
            "timed_out": False,
        }
    )

    assert result["has_output"] is True


def test_validator_treats_whitespace_only_stdout_as_no_output():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": 0,
            "stdout": "   \n",
            "stderr": "",
            "timed_out": False,
        }
    )

    assert result["has_output"] is False


def test_validator_detects_error_output():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": 1,
            "stdout": "",
            "stderr": "failure",
            "timed_out": False,
        }
    )

    assert result["error_detected"] is True


def test_validator_treats_whitespace_only_stderr_as_no_error_output():
    validator = Validator()

    result = validator.validate(
        {
            "returncode": 1,
            "stdout": "",
            "stderr": "   \n",
            "timed_out": False,
        }
    )

    assert result["error_detected"] is False

import pytest

from jarvis_operator.tools.list_dir import list_dir
from jarvis_operator.tools.read_file import read_file
from jarvis_operator.tools.write_file import write_file


def test_read_file_reads_content_within_allowed_workspace(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="utf-8")

    assert read_file(file_path, allowed_workspaces=[tmp_path]) == "hello"


def test_read_file_blocks_paths_outside_allowed_workspace(tmp_path):
    blocked_path = tmp_path.parent / "outside.txt"
    blocked_path.write_text("blocked", encoding="utf-8")

    with pytest.raises(PermissionError, match="Path not allowed"):
        read_file(blocked_path, allowed_workspaces=[tmp_path])


def test_read_file_raises_for_missing_file_within_allowed_workspace(tmp_path):
    missing_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        read_file(missing_path, allowed_workspaces=[tmp_path])


def test_write_file_returns_success_and_bytes_written(tmp_path):
    file_path = tmp_path / "output.txt"

    result = write_file(file_path, "hello", allowed_workspaces=[tmp_path])

    assert result == {"success": True, "bytes_written": 5}
    assert file_path.read_text(encoding="utf-8") == "hello"


def test_write_file_blocks_invalid_path(tmp_path):
    blocked_path = tmp_path.parent / "outside.txt"

    with pytest.raises(PermissionError, match="Path not allowed"):
        write_file(blocked_path, "blocked", allowed_workspaces=[tmp_path])


def test_list_dir_lists_files_in_allowed_workspace(tmp_path):
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")

    assert list_dir(tmp_path, allowed_workspaces=[tmp_path]) == ["a.txt", "b.txt"]


def test_list_dir_handles_empty_directory(tmp_path):
    assert list_dir(tmp_path, allowed_workspaces=[tmp_path]) == []


def test_list_dir_blocks_paths_outside_allowed_workspace(tmp_path):
    with pytest.raises(PermissionError, match="Path not allowed"):
        list_dir(tmp_path.parent, allowed_workspaces=[tmp_path])

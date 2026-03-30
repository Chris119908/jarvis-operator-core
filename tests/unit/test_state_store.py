import json

import pytest

from jarvis_operator.state.store import StateStore


def test_state_store_roundtrip(tmp_path):
    store = StateStore(tmp_path)
    data = {"hello": "world"}
    store.save_state(data)
    assert store.load_state() == data


def test_state_store_returns_empty_dict_when_state_file_is_missing(tmp_path):
    store = StateStore(tmp_path)

    assert store.load_state() == {}


def test_state_store_raises_json_decode_error_for_broken_state_file(tmp_path):
    store = StateStore(tmp_path)
    store.state_file.write_text("{broken json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        store.load_state()

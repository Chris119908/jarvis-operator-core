from jarvis_operator.state.store import StateStore


def test_state_store_roundtrip(tmp_path):
    store = StateStore(tmp_path)
    data = {"hello": "world"}
    store.save_state(data)
    assert store.load_state() == data

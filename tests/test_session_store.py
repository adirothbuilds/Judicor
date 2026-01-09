from judicor.session import store


def test_save_and_load_attached_incident(temp_session_store):
    store.save_attached_incident(5)
    assert store.load_attached_incident() == 5


def test_clear_session(temp_session_store):
    store.save_attached_incident(2)
    store.clear_session()
    assert store.load_attached_incident() is None


def test_load_invalid_file_returns_none(temp_session_store):
    temp_session_store.BASE_DIR.mkdir(exist_ok=True)
    temp_session_store.SESSION_FILE.write_text("not-json")

    assert temp_session_store.load_attached_incident() is None

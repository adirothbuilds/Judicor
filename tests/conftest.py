import pytest

import judicor.session.store as session_store
import judicor.identity.store as identity_store
import judicor.session.timeline_store as timeline_store


@pytest.fixture
def temp_session_store(monkeypatch, tmp_path):
    base = tmp_path / ".judicor"
    monkeypatch.setattr(session_store, "BASE_DIR", base)
    monkeypatch.setattr(
        session_store, "SESSION_FILE", base / "session.json"
    )
    return session_store


@pytest.fixture
def temp_identity_store(monkeypatch, tmp_path):
    base = tmp_path / ".judicor"
    monkeypatch.setattr(identity_store, "BASE_DIR", base)
    monkeypatch.setattr(
        identity_store, "IDENTITY_FILE", base / "identity.json"
    )
    return identity_store


@pytest.fixture
def temp_timeline_store(monkeypatch, tmp_path):
    base = tmp_path / ".judicor" / "incidents"
    monkeypatch.setattr(timeline_store, "BASE_DIR", base)
    return timeline_store

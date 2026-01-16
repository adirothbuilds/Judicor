import pytest

import judicor.session.store as session_store
import judicor.identity.store as identity_store
import judicor.session.timeline_store as timeline_store
import judicor.session.incident_store as incident_store
import judicor.session.history_store as history_store
import judicor.control_plane.app as control_plane_app


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


@pytest.fixture
def temp_incident_store(monkeypatch, tmp_path):
    base = tmp_path / ".judicor" / "incidents"
    monkeypatch.setattr(incident_store, "BASE_DIR", base)
    return incident_store


@pytest.fixture
def temp_history_store(monkeypatch, tmp_path):
    base = tmp_path / ".judicor" / "incidents"
    monkeypatch.setattr(history_store, "BASE_DIR", base)
    return history_store


@pytest.fixture
def temp_control_plane_storage(monkeypatch, tmp_path):
    base = tmp_path / ".judicor" / "incidents"
    monkeypatch.setattr(incident_store, "BASE_DIR", base)
    monkeypatch.setattr(timeline_store, "BASE_DIR", base)
    monkeypatch.setattr(history_store, "BASE_DIR", base)
    # Ensure FastAPI module references use patched stores
    monkeypatch.setattr(control_plane_app.incident_store, "BASE_DIR", base)
    monkeypatch.setattr(control_plane_app.timeline_store, "BASE_DIR", base)
    monkeypatch.setattr(control_plane_app.history_store, "BASE_DIR", base)
    return base

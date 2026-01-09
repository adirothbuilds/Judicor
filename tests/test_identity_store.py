from datetime import datetime, timezone

from judicor.identity import store
from judicor.identity.model import Identity


def _sample_identity():
    return Identity(
        user_id="id",
        name="Name",
        email="email@example.com",
        org="Org",
        hostname="host",
        os_user="user",
        fingerprint="fp",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def test_save_and_load_identity(temp_identity_store):
    identity = _sample_identity()

    store.save_identity(identity)
    loaded = store.load_identity()

    assert loaded is not None
    assert loaded.name == identity.name
    assert loaded.email == identity.email
    assert loaded.created_at == identity.created_at


def test_load_corrupted_identity_returns_none(temp_identity_store):
    temp_identity_store.BASE_DIR.mkdir(exist_ok=True)
    temp_identity_store.IDENTITY_FILE.write_text("invalid")

    assert temp_identity_store.load_identity() is None

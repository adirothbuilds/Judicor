import importlib

import pytest


def test_create_judicor_client_default(monkeypatch, temp_session_store):
    monkeypatch.delenv("JUDICOR_CLIENT_TYPE", raising=False)
    import judicor.client.factory as factory

    importlib.reload(factory)
    from judicor.client.implementations.dummy import DummyJudicorClient

    assert isinstance(factory.create_judicor_client(), DummyJudicorClient)


def test_create_judicor_client_unknown(monkeypatch, temp_session_store):
    monkeypatch.setenv("JUDICOR_CLIENT_TYPE", "unknown")
    import judicor.client.factory as factory

    importlib.reload(factory)

    with pytest.raises(ValueError):
        factory.create_judicor_client()

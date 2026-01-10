import importlib

import pytest

from judicor.ai.roles import AgentRole


def test_create_ai_reasoner_default_dummy(monkeypatch):
    monkeypatch.delenv("JUDICOR_AI_PROVIDER", raising=False)
    import judicor.ai.factory as factory

    importlib.reload(factory)
    from judicor.ai.implementations.dummy import DummyAIReasoner

    assert isinstance(
        factory.create_ai_reasoner(AgentRole.INVESTIGATOR), DummyAIReasoner
    )


def test_create_ai_reasoner_gemini(monkeypatch):
    monkeypatch.setenv("JUDICOR_AI_PROVIDER", "gemini")
    import judicor.ai.factory as factory

    importlib.reload(factory)

    class FakeReasoner:
        def __init__(self, role):
            self.role = role

    monkeypatch.setattr(factory, "GeminiAIReasoner", FakeReasoner)

    assert isinstance(
        factory.create_ai_reasoner(AgentRole.INVESTIGATOR), FakeReasoner
    )


def test_create_ai_reasoner_unknown(monkeypatch):
    monkeypatch.setenv("JUDICOR_AI_PROVIDER", "unknown")
    import judicor.ai.factory as factory

    importlib.reload(factory)

    with pytest.raises(ValueError):
        factory.create_ai_reasoner(AgentRole.INVESTIGATOR)

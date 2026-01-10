from types import SimpleNamespace

from judicor.ai.implementations import gemini
from judicor.ai.roles import AgentRole
from judicor.domain.models import Incident, IncidentState


class _Response:
    def __init__(self, text: str):
        self.text = text


class _StubModels:
    def __init__(
        self, response_text: str | None = None, error: Exception | None = None
    ):
        self.response_text = response_text
        self.error = error

    def generate_content(self, model: str, contents: str):
        if self.error:
            raise self.error
        return _Response(self.response_text or "")


class _StubClient:
    def __init__(
        self, response_text: str | None = None, error: Exception | None = None
    ):
        self.models = _StubModels(response_text=response_text, error=error)


def test_gemini_reasoner_success(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    monkeypatch.setattr(
        gemini, "genai", SimpleNamespace(Client=lambda: _StubClient("answer"))
    )

    reasoner = gemini.GeminiAIReasoner(role=AgentRole.INVESTIGATOR)
    incident = Incident(id=1, title="title", state=IncidentState.ACTIVE)

    result = reasoner.ask(incident, "question")

    assert result.success
    assert result.answer == "answer"
    assert result.confidence == 1.0


def test_gemini_reasoner_failure(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    error = RuntimeError("fail")
    monkeypatch.setattr(
        gemini,
        "genai",
        SimpleNamespace(Client=lambda: _StubClient(error=error)),
    )

    reasoner = gemini.GeminiAIReasoner(role=AgentRole.INVESTIGATOR)
    incident = Incident(id=1, title="title", state=IncidentState.ACTIVE)

    result = reasoner.ask(incident, "question")

    assert not result.success
    assert result.message == "fail"

from dataclasses import dataclass

from judicor.client.implementations.dummy import DummyJudicorClient
from judicor.domain.models import Incident
from judicor.domain.messages import NO_INCIDENT_ATTACHED
from judicor.domain.results import AskResult


@dataclass
class _StubReasoner:
    answer: str = "ok"
    confidence: float = 0.9

    def ask(self, incident: Incident, question: str) -> AskResult:
        return AskResult(
            success=True,
            answer=f"{self.answer}-{incident.id}",
            confidence=self.confidence,
            reasoning="r",
        )


def test_list_and_attach_incident(temp_session_store):
    client = DummyJudicorClient(reasoner=_StubReasoner())

    incidents = client.list_incidents()
    assert len(incidents) == 2

    attach = client.attach_incident(1)
    assert attach.success
    assert attach.incident_id == 1

    missing = client.attach_incident(99)
    assert not missing.success


def test_ask_and_policy_flow(temp_session_store):
    client = DummyJudicorClient(
        reasoner=_StubReasoner(answer="answer", confidence=0.95)
    )
    client.attach_incident(1)

    result = client.ask_ai("q")
    assert result.success
    assert result.answer == "answer-1"


def test_ask_without_attachment(temp_session_store):
    client = DummyJudicorClient(reasoner=_StubReasoner())
    result = client.ask_ai("q")
    assert not result.success
    assert result.message == NO_INCIDENT_ATTACHED


def test_status_and_detach(temp_session_store):
    client = DummyJudicorClient(reasoner=_StubReasoner())
    status = client.status_incident()
    assert not status.success

    client.attach_incident(1)
    status = client.status_incident()
    assert status.success
    assert "Dummy Incident 1" in status.summary

    detach = client.detach_incident()
    assert detach.success
    assert client.current_incident is None


def test_resolve_and_trigger(temp_session_store):
    client = DummyJudicorClient(reasoner=_StubReasoner())
    resolve = client.resolve_incident()
    assert not resolve.success

    client.attach_incident(1)
    resolve = client.resolve_incident()
    assert resolve.success

    created = client.trigger()
    assert created.success
    assert created.incident_id == 3

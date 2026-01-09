from judicor.ai.implementations.dummy import DummyAIReasoner
from judicor.domain.models import Incident, IncidentState


def test_dummy_reasoner_returns_static_answer():
    reasoner = DummyAIReasoner()
    incident = Incident(id=1, title="t", state=IncidentState.ACTIVE)

    result = reasoner.ask(incident, "question")

    assert result.success
    assert "Dummy analysis" in result.answer
    assert result.confidence == 0.9
    assert result.reasoning == "Static dummy reasoning"

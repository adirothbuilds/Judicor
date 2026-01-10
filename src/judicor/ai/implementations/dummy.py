# src/judicor/ai/implementations/dummy.py

from judicor.ai.interface import AIReasoner
from judicor.domain.models import Incident
from judicor.domain.results import AskResult


class DummyAIReasoner(AIReasoner):
    """Fake AI for local testing."""

    def __init__(self, role=None):
        self.role = role

    def ask(self, incident: Incident, question: str) -> AskResult:
        role = getattr(self.role, "value", self.role) or "generic"
        return AskResult(
            success=True,
            answer=f"Dummy {role} response for incident {incident.id}",
            confidence=0.9,
            reasoning="Static dummy reasoning",
        )

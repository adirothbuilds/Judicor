# src/judicor/ai/implementations/dummy.py

from judicor.ai.interface import AIReasoner
from judicor.domain.models import Incident
from judicor.domain.results import AskResult


class DummyAIReasoner(AIReasoner):
    """Fake AI for local testing."""

    def ask(self, incident: Incident, question: str) -> AskResult:
        return AskResult(
            success=True,
            answer=f"Dummy analysis for incident {incident.id}",
            confidence=0.9,
            reasoning="Static dummy reasoning",
        )

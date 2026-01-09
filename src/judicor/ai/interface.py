# src/judicor/ai/interface.py

from abc import ABC, abstractmethod
from judicor.domain.results import AskResult
from judicor.domain.models import Incident


class AIReasoner(ABC):
    """
    Interface for AI Reasoner engines.

    Responsible ONLY for producing a reasoning response.
    Must NOT contain policy, validation, or enforcement logic.
    """

    @abstractmethod
    def ask(self, incident: Incident, question: str) -> AskResult:
        """Generate a resoning response for a given incident"""
        pass

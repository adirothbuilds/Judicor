#  src/judicor/client/interface.py

from abc import ABC, abstractmethod
from judicor.domain.results import (
    Result,
    AttachResult,
    AskResult,
    TriggerResult,
    StatusResult,
)


class JudicorClient(ABC):
    """
    Base interface for Judicor clients.

    Methods:
        - list_incidents: List all incidents.
        - attach_incident: Attach to an active incident session by ID.
        - detach_incident: Detach from the currently attached incident session.
        - ask_ai: Ask a question to the AI assistant
            about the currently attached incident.
        - status_incident: Check the status of the current session.
        - resolve_incident: Resolve the currently attached incident
            and close the session.
        - trigger: Trigger to create a new incident session.
    """

    @abstractmethod
    def list_incidents(self):
        """List all incidents."""
        pass

    @abstractmethod
    def attach_incident(self, incident_id: int) -> AttachResult:
        """Attach to an active incident session by ID."""
        pass

    @abstractmethod
    def detach_incident(self) -> Result:
        """Detach from the currently attached incident session."""
        pass

    @abstractmethod
    def ask_ai(self, question: str) -> AskResult:
        """
        Ask a question to the AI assistant
        about the currently attached incident.
        """
        pass

    @abstractmethod
    def status_incident(self) -> StatusResult:
        """Check the status of the current session."""
        pass

    @abstractmethod
    def resolve_incident(self) -> Result:
        """Resolve the currently attached incident and close the session."""
        pass

    @abstractmethod
    def trigger(self) -> TriggerResult:
        """Trigger to create a new incident session."""
        pass

# src/judicor/client/implementations/dummy.py

from typing import Dict, Optional, List

from judicor.client.interface import JudicorClient
from judicor.domain.models import Incident
from judicor.domain.messages import NO_INCIDENT_ATTACHED
from judicor.domain.results import (
    Result,
    AttachResult,
    AskResult,
    TriggerResult,
    StatusResult,
)


class DummyJudicorClient(JudicorClient):
    """
    Dummy implementation of the JudicorClient interface.
    Used for local testing and development.
    """

    def __init__(self) -> None:
        self.current_incident: Optional[Incident] = None
        self.incidents: Dict[int, Incident] = {
            1: Incident(id=1, title="Dummy Incident 1", status="active"),
            2: Incident(id=2, title="Dummy Incident 2", status="resolved"),
        }

    def list_incidents(self) -> List[Incident]:
        """List all incidents."""
        return list(self.incidents.values())

    def attach_incident(self, incident_id: int) -> AttachResult:
        """Attach to an active incident session by ID."""
        incident = self.incidents.get(incident_id)
        if not incident:
            return AttachResult(success=False, message="Incident not found")

        self.current_incident = incident
        return AttachResult(success=True, incident_id=incident_id)

    def detach_incident(self) -> Result:
        """Detach from the currently attached incident session."""
        if self.current_incident is None:
            return Result(success=False, message=NO_INCIDENT_ATTACHED)

        self.current_incident = None
        return Result(success=True, message="Detached successfully")

    def ask_ai(self, question: str) -> AskResult:
        """Ask a question to the AI assistant about the attached incident."""
        if self.current_incident is None:
            return AskResult(success=False, message=NO_INCIDENT_ATTACHED)

        return AskResult(
            success=True,
            answer="This is a dummy answer.",
            confidence=0.9,
            reasoning="Dummy reasoning trace.",
        )

    def status_incident(self) -> StatusResult:
        """Check the status of the current incident session."""
        if self.current_incident is None:
            return StatusResult(
                success=False,
                state="none",
                summary=NO_INCIDENT_ATTACHED,
            )

        return StatusResult(
            success=True,
            state=self.current_incident.status,
            summary=f"{self.current_incident.title} is {self.current_incident.status}",
        )

    def resolve_incident(self) -> Result:
        """Resolve the currently attached incident and close the session."""
        if self.current_incident is None:
            return Result(success=False, message=NO_INCIDENT_ATTACHED)

        self.current_incident.status = "resolved"
        incident_id = self.current_incident.id
        self.current_incident = None

        return Result(
            success=True,
            message=f"Incident {incident_id} resolved successfully",
        )

    def trigger(self) -> TriggerResult:
        """Trigger creation of a new incident session."""
        new_incident_id = max(self.incidents.keys(), default=0) + 1

        self.incidents[new_incident_id] = Incident(
            id=new_incident_id,
            title=f"Dummy Incident {new_incident_id}",
            status="active",
        )

        return TriggerResult(success=True, incident_id=new_incident_id)

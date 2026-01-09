from datetime import datetime, timezone
from typing import Dict, List

from judicor.domain.models import Incident, IncidentState


ALLOWED_TRANSITIONS: Dict[IncidentState, List[IncidentState]] = {
    IncidentState.CREATED: [IncidentState.ACTIVE],
    IncidentState.ACTIVE: [
        IncidentState.INVESTIGATING,
        IncidentState.RESOLVED,
    ],
    IncidentState.INVESTIGATING: [IncidentState.RESOLVED],
    IncidentState.RESOLVED: [IncidentState.ARCHIVED],
    IncidentState.ARCHIVED: [],
}


def transition_incident_state(
    incident: Incident, target: IncidentState
) -> None:
    allowed = ALLOWED_TRANSITIONS.get(incident.state, [])
    if target not in allowed:
        raise ValueError(
            f"Illegal transition from {incident.state.value} to {target.value}"
        )

    incident.state = target
    incident.updated_at = datetime.now(timezone.utc)

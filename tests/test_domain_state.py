import pytest

from judicor.domain.models import Incident, IncidentState
from judicor.domain.state import transition_incident_state


def test_valid_transition_updates_state():
    incident = Incident(id=1, title="t")
    transition_incident_state(incident, IncidentState.ACTIVE)
    assert incident.state is IncidentState.ACTIVE


def test_invalid_transition_raises():
    incident = Incident(id=1, title="t", state=IncidentState.RESOLVED)
    with pytest.raises(ValueError):
        transition_incident_state(incident, IncidentState.ACTIVE)

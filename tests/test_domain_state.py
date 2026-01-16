import pytest

from datetime import datetime, timezone

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


def test_transition_updates_timestamp():
    incident = Incident(
        id=1,
        title="t",
        state=IncidentState.CREATED,
        created_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )

    before = incident.updated_at
    transition_incident_state(incident, IncidentState.ACTIVE)

    assert incident.state is IncidentState.ACTIVE
    assert incident.updated_at > before

from judicor.domain.models import IncidentState
from judicor.session import incident_store


def test_create_and_list_incidents(temp_incident_store):
    incident_store.create_incident("One", IncidentState.CREATED)
    incident_store.create_incident("Two", IncidentState.ACTIVE)

    incidents = incident_store.list_incidents()
    assert len(incidents) == 2
    assert incidents[0].title == "One"
    assert incidents[1].state is IncidentState.ACTIVE


def test_load_and_update_state(temp_incident_store):
    inc = incident_store.create_incident("Three", IncidentState.CREATED)
    loaded = incident_store.load_incident(inc.id)
    assert loaded is not None
    assert loaded.state is IncidentState.CREATED

    incident_store.update_state(loaded, IncidentState.ACTIVE)
    reloaded = incident_store.load_incident(inc.id)
    assert reloaded.state is IncidentState.ACTIVE

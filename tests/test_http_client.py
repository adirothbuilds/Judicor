from fastapi.testclient import TestClient

from judicor.client.implementations.http import HttpJudicorClient
from judicor.control_plane.app import app


def test_http_client_flow(monkeypatch, temp_control_plane_storage):
    monkeypatch.setenv("JUDICOR_API_KEY", "k")
    test_client = TestClient(app)

    # Patch requests.Session with TestClient's request for isolation
    class _SessWrapper:
        def __init__(self, tc):
            self.tc = tc

        def get(self, url, headers=None):
            return self.tc.get(
                url.replace(str(self.tc.base_url), ""), headers=headers
            )

        def post(self, url, json=None, headers=None):
            return self.tc.post(
                url.replace(str(self.tc.base_url), ""),
                json=json,
                headers=headers,
            )

    client = HttpJudicorClient(base_url=test_client.base_url, api_key="k")
    client.session = _SessWrapper(test_client)

    # Trigger
    trig = client.trigger()
    assert trig.success
    incident_id = trig.incident_id

    # List
    incidents = client.list_incidents()
    assert any(i.id == incident_id for i in incidents)

    # Attach + status
    assert client.attach_incident(incident_id).success
    status = client.status_incident()
    assert status.success

    # Resolve
    result = client.resolve_incident()
    assert result.success

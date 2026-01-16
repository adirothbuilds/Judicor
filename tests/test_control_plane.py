from fastapi.testclient import TestClient

from judicor.control_plane.app import app


def test_control_plane_incident_flow(monkeypatch, temp_control_plane_storage):
    monkeypatch.setenv("JUDICOR_API_KEY", "k")
    client = TestClient(app)

    # Health
    resp = client.get("/health")
    assert resp.status_code == 200

    headers = {"X-API-Key": "k"}

    # Create
    resp = client.post(
        "/incidents", json={"title": "CP Incident"}, headers=headers
    )
    assert resp.status_code == 200
    incident_id = resp.json()["id"]

    # Get
    resp = client.get(f"/incidents/{incident_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "CP Incident"

    # Timeline append
    resp = client.post(
        f"/incidents/{incident_id}/timeline",
        json={"event_type": "note", "message": "checking"},
        headers=headers,
    )
    assert resp.status_code == 200

    # Resolve
    resp = client.post(
        f"/incidents/{incident_id}/resolve",
        json={"resolution": "fixed"},
        headers=headers,
    )
    assert resp.status_code == 200

    # List
    resp = client.get("/incidents", headers=headers)
    assert resp.status_code == 200
    assert any(item["id"] == incident_id for item in resp.json())

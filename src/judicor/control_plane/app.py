import os
from fastapi import Depends, FastAPI, Header, HTTPException, status

from judicor.domain.models import IncidentState
from judicor.ai.roles import AgentRole
from judicor.session import incident_store, timeline_store, history_store

app = FastAPI(title="Judicor Control Plane")


def _get_api_key() -> str:
    return os.getenv("JUDICOR_API_KEY", "secret-key")


async def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != _get_api_key():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/incidents", dependencies=[Depends(require_api_key)])
async def list_incidents():
    return [
        {
            "id": inc.id,
            "title": inc.title,
            "state": inc.state.value,
            "created_at": inc.created_at.isoformat(),
            "updated_at": inc.updated_at.isoformat(),
        }
        for inc in incident_store.list_incidents()
    ]


@app.post("/incidents", dependencies=[Depends(require_api_key)])
async def create_incident(payload: dict):
    title = payload.get("title", "Untitled Incident")
    incident = incident_store.create_incident(
        title=title, initial_state=IncidentState.CREATED
    )

    timeline_store.append_event(
        incident.id, "created", f"Incident {incident.id} created"
    )
    try:
        from judicor.domain.state import transition_incident_state

        transition_incident_state(incident, IncidentState.ACTIVE)
        incident_store.save_incident(incident)
        timeline_store.append_event(
            incident.id, "state_change", "Incident moved to active"
        )
    except Exception:
        pass

    return {
        "id": incident.id,
        "title": incident.title,
        "state": incident.state.value,
    }


@app.get("/incidents/{incident_id}", dependencies=[Depends(require_api_key)])
async def get_incident(incident_id: int):
    incident = incident_store.load_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    summary = history_store.load_summary(incident_id) or ""
    timeline = [e.to_json() for e in timeline_store.load_timeline(incident_id)]

    return {
        "id": incident.id,
        "title": incident.title,
        "state": incident.state.value,
        "created_at": incident.created_at.isoformat(),
        "updated_at": incident.updated_at.isoformat(),
        "summary": summary,
        "timeline": timeline,
    }


@app.post(
    "/incidents/{incident_id}/resolve", dependencies=[Depends(require_api_key)]
)
async def resolve_incident(incident_id: int, payload: dict | None = None):
    from judicor.domain.state import transition_incident_state

    incident = incident_store.load_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    try:
        transition_incident_state(incident, IncidentState.RESOLVED)
        incident_store.save_incident(incident)
        timeline_store.append_event(
            incident_id, "state_change", "Incident resolved via control plane"
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    resolution = (payload or {}).get("resolution")
    if resolution:
        history_store.append_entry(
            incident_id,
            role=AgentRole.RESOLVER,
            content=str(resolution),
        )
        history_store.set_summary(incident_id, str(resolution))

    return {
        "id": incident.id,
        "state": incident.state.value,
        "message": "Incident resolved",
    }


@app.post(
    "/incidents/{incident_id}/timeline",
    dependencies=[Depends(require_api_key)],
)
async def append_timeline(incident_id: int, payload: dict):
    incident = incident_store.load_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    event_type = payload.get("event_type", "custom")
    message = payload.get("message", "")
    timeline_store.append_event(incident_id, event_type, message)
    return {"status": "ok"}

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from judicor.domain.models import Incident, IncidentState
from judicor.domain.state import transition_incident_state
from judicor.session.utils import parse_dt, secure_write_json

BASE_DIR = Path.home() / ".judicor" / "incidents"


def _incident_path(incident_id: int) -> Path:
    return BASE_DIR / str(incident_id) / "incident.json"


def save_incident(incident: Incident) -> None:
    payload = asdict(incident)
    payload["state"] = incident.state.value
    payload["created_at"] = incident.created_at.isoformat()
    payload["updated_at"] = incident.updated_at.isoformat()
    secure_write_json(_incident_path(incident.id), payload)


def load_incident(incident_id: int) -> Optional[Incident]:
    path = _incident_path(incident_id)
    if not path.exists():
        return None
    try:
        return _read_incident(path)
    except Exception:
        return None


def list_incidents() -> List[Incident]:
    if not BASE_DIR.exists():
        return []
    incidents: List[Incident] = []
    for path in BASE_DIR.glob("*/incident.json"):
        try:
            incidents.append(_read_incident(path))
        except Exception:
            continue
    incidents.sort(key=lambda i: i.id)
    return incidents


def create_incident(title: str, initial_state: IncidentState) -> Incident:
    incident_id = _next_incident_id()
    incident = Incident(id=incident_id, title=title, state=initial_state)
    save_incident(incident)
    return incident


def update_state(incident: Incident, target: IncidentState) -> Incident:
    transition_incident_state(incident, target)
    save_incident(incident)
    return incident


def _next_incident_id() -> int:
    existing = [int(p.parent.name) for p in BASE_DIR.glob("*/incident.json")]
    return max(existing, default=0) + 1


def _deserialize_incident(data: Dict) -> Incident:
    return Incident(
        id=int(data["id"]),
        title=data["title"],
        state=IncidentState(data.get("state", IncidentState.CREATED.value)),
        created_at=parse_dt(data.get("created_at")),
        updated_at=parse_dt(data.get("updated_at")),
    )


def _read_incident(path: Path) -> Incident:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return _deserialize_incident(data)

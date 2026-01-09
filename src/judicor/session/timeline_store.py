import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

BASE_DIR = Path.home() / ".judicor" / "incidents"


@dataclass
class TimelineEvent:
    incident_id: int
    event_type: str
    message: str
    timestamp: datetime

    def to_json(self) -> dict:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @staticmethod
    def from_json(data: dict) -> "TimelineEvent":
        return TimelineEvent(
            incident_id=int(data["incident_id"]),
            event_type=data["event_type"],
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


def _timeline_path(incident_id: int) -> Path:
    return BASE_DIR / str(incident_id) / "timeline.json"


def append_event(incident_id: int, event_type: str, message: str) -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    path = _timeline_path(incident_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    events = load_timeline(incident_id)
    event = TimelineEvent(
        incident_id=incident_id,
        event_type=event_type,
        message=message,
        timestamp=datetime.now(timezone.utc),
    )
    events.append(event)

    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.to_json() for e in events], f, indent=2)


def load_timeline(incident_id: int) -> List[TimelineEvent]:
    path = _timeline_path(incident_id)
    if not path.exists():
        return []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return [TimelineEvent.from_json(item) for item in data]
    except Exception:
        return []

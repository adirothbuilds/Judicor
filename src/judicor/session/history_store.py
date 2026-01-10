import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from judicor.ai.roles import AgentRole
from judicor.session.utils import ensure_dir, parse_dt, secure_write_json

BASE_DIR = Path.home() / ".judicor" / "incidents"


@dataclass
class HistoryEntry:
    incident_id: int
    role: AgentRole
    content: str
    timestamp: datetime

    def to_json(self) -> dict:
        data = asdict(self)
        data["role"] = self.role.value
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @staticmethod
    def from_json(data: dict) -> "HistoryEntry":
        return HistoryEntry(
            incident_id=int(data["incident_id"]),
            role=AgentRole(data["role"]),
            content=data["content"],
            timestamp=parse_dt(data["timestamp"]),
        )


def _history_path(incident_id: int) -> Path:
    return BASE_DIR / str(incident_id) / "history.json"


def append_entry(incident_id: int, role: AgentRole, content: str) -> None:
    entries = load_history(incident_id)
    entry = HistoryEntry(
        incident_id=incident_id,
        role=role,
        content=content,
        timestamp=datetime.now(timezone.utc),
    )
    entries.append(entry)

    path = _history_path(incident_id)
    ensure_dir(path.parent)
    secure_write_json(path, [e.to_json() for e in entries])


def load_history(incident_id: int) -> List[HistoryEntry]:
    path = _history_path(incident_id)
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return [HistoryEntry.from_json(item) for item in data]
    except Exception:
        return []


def set_summary(incident_id: int, summary: str) -> None:
    path = _summary_path(incident_id)
    ensure_dir(path.parent)
    secure_write_json(path, {"summary": summary})


def load_summary(incident_id: int) -> Optional[str]:
    path = _summary_path(incident_id)
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("summary")
    except Exception:
        return None


def _summary_path(incident_id: int) -> Path:
    return BASE_DIR / str(incident_id) / "summary.json"

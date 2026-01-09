# src/judicor/session/store.py

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

BASE_DIR = Path.home() / ".judicor"
SESSION_FILE = BASE_DIR / "session.json"


def save_attached_incident(incident_id: int) -> None:
    BASE_DIR.mkdir(exist_ok=True)

    payload = {
        "attached_incident_id": incident_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_attached_incident() -> Optional[int]:
    if not SESSION_FILE.exists():
        return None

    try:
        with open(SESSION_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        return int(raw["attached_incident_id"])
    except Exception:
        return None


def clear_session() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()

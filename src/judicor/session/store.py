# src/judicor/session/store.py

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Tuple

from judicor.session.utils import ensure_dir, parse_dt, secure_write_json

BASE_DIR = Path.home() / ".judicor"
SESSION_FILE = BASE_DIR / "session.json"


def save_attached_incident(incident_id: int) -> None:
    ensure_dir(BASE_DIR)

    payload = {
        "attached_incident_id": incident_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    secure_write_json(SESSION_FILE, payload)


def load_attached_incident() -> Optional[int]:
    if not SESSION_FILE.exists():
        return None

    try:
        with open(SESSION_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        return int(raw["attached_incident_id"])
    except Exception:
        return None


def load_session() -> Optional[Tuple[int, datetime]]:
    if not SESSION_FILE.exists():
        return None

    try:
        with open(SESSION_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        attached = int(raw["attached_incident_id"])
        updated_at = parse_dt(raw.get("updated_at"))
        return attached, updated_at
    except Exception:
        return None


def clear_session() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()

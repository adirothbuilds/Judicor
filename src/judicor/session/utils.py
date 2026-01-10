import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def ensure_dir(path: Path, mode: int = 0o700) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(mode)
    except PermissionError:
        pass


def secure_write_json(path: Path, data: Any, mode: int = 0o600) -> None:
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    try:
        path.chmod(mode)
    except PermissionError:
        pass


def parse_dt(value) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.now(timezone.utc)

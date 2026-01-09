import json
from pathlib import Path
from datetime import datetime
from json import JSONDecodeError

from judicor.identity.model import Identity

BASE_DIR = Path.home() / ".judicor"
IDENTITY_FILE = BASE_DIR / "identity.json"


def save_identity(identity: Identity) -> None:
    """
    Persist identity to ~/.judicor/identity.json

    Security:
    - ~/.judicor       -> 700 (owner only)
    - identity.json    -> 600 (owner read/write)

    Datetime is stored in ISO-8601 format (UTC).
    """
    # Ensure base directory exists with strict permissions
    BASE_DIR.mkdir(mode=0o700, exist_ok=True)

    payload = {
        **identity.__dict__,
        "created_at": identity.created_at.isoformat(),
    }

    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # Enforce strict file permissions (important on shared systems)
    try:
        IDENTITY_FILE.chmod(0o600)
    except PermissionError:
        # Best-effort hardening; do not fail CLI if chmod is not allowed
        pass


def load_identity() -> Identity | None:
    """
    Load identity from ~/.judicor/identity.json

    Returns None if:
    - file does not exist
    - file is corrupted
    - schema is incompatible
    """
    if not IDENTITY_FILE.exists():
        return None

    try:
        with open(IDENTITY_FILE, encoding="utf-8") as f:
            raw = json.load(f)

        raw["created_at"] = datetime.fromisoformat(raw["created_at"])
        return Identity(**raw)

    except (JSONDecodeError, KeyError, ValueError):
        # Identity file exists but is corrupted or incompatible
        return None

# src/judicor/identity/model.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Identity:
    user_id: str
    name: str
    email: str
    org: Optional[str]
    hostname: str
    os_user: str
    fingerprint: str
    created_at: datetime

# src/judicor/domain/models.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class IncidentState(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


@dataclass
class Incident:
    id: int
    title: str
    state: IncidentState = IncidentState.CREATED
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def status(self) -> str:
        return self.state.value

    def set_state(self, state: IncidentState) -> None:
        self.state = state
        self.updated_at = datetime.now(timezone.utc)

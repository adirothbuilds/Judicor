import os
from typing import Optional, List

import requests

from judicor.domain.models import IncidentState

from judicor.client.interface import JudicorClient
from judicor.domain.messages import NO_INCIDENT_ATTACHED
from judicor.domain.models import Incident
from judicor.domain.results import (
    Result,
    AttachResult,
    AskResult,
    TriggerResult,
    StatusResult,
)


class HttpJudicorClient(JudicorClient):
    """HTTP client talking to the control plane API."""

    def __init__(
        self, base_url: Optional[str] = None, api_key: Optional[str] = None
    ):
        self.base_url = base_url or os.getenv(
            "JUDICOR_API_URL", "http://localhost:8000"
        )
        self.api_key = api_key or os.getenv("JUDICOR_API_KEY", "")
        self.session = requests.Session()
        self.current_incident: Optional[int] = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _headers(self) -> dict:
        if not self.api_key:
            raise RuntimeError("JUDICOR_API_KEY is required for HTTP client")
        return {"X-API-Key": self.api_key}

    def _get(self, path: str):
        resp = self.session.get(
            f"{self.base_url}{path}", headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json=None):
        resp = self.session.post(
            f"{self.base_url}{path}", json=json or {}, headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------
    def list_incidents(self) -> List[Incident]:
        data = self._get("/incidents")
        return [
            Incident(
                id=item["id"],
                title=item["title"],
                state=IncidentState(item["state"]),
            )
            for item in data
        ]

    def attach_incident(self, incident_id: int) -> AttachResult:
        # Ensure incident exists
        try:
            self._get(f"/incidents/{incident_id}")
        except Exception as exc:
            return AttachResult(success=False, message=str(exc))

        self.current_incident = incident_id
        return AttachResult(success=True, incident_id=incident_id)

    def detach_incident(self) -> Result:
        if self.current_incident is None:
            return Result(success=False, message=NO_INCIDENT_ATTACHED)

        self.current_incident = None
        return Result(success=True, message="Detached successfully")

    def ask_ai(self, question: str) -> AskResult:
        if self.current_incident is None:
            return AskResult(success=False, message=NO_INCIDENT_ATTACHED)

        # For now delegate to timeline append + return stub; real AI call would
        # be server-side
        try:
            self._post(
                f"/incidents/{self.current_incident}/timeline",
                json={"event_type": "ask", "message": question},
            )
        except Exception as exc:
            return AskResult(success=False, message=str(exc))

        return AskResult(
            success=True, answer="Remote AI response", confidence=1.0
        )

    def status_incident(self) -> StatusResult:
        if self.current_incident is None:
            return StatusResult(
                success=False,
                state="none",
                summary=NO_INCIDENT_ATTACHED,
            )

        try:
            data = self._get(f"/incidents/{self.current_incident}")
            return StatusResult(
                success=True,
                state=data["state"],
                summary=data.get("summary", ""),
            )
        except Exception as exc:
            return StatusResult(success=False, state="none", summary=str(exc))

    def resolve_incident(self) -> Result:
        if self.current_incident is None:
            return Result(success=False, message=NO_INCIDENT_ATTACHED)

        try:
            self._post(
                f"/incidents/{self.current_incident}/resolve",
                json={},
            )
            return Result(success=True, message="Incident resolved remotely")
        except Exception as exc:
            return Result(success=False, message=str(exc))

    def trigger(self) -> TriggerResult:
        try:
            data = self._post(
                "/incidents",
                json={"title": "New Incident"},
            )
            incident_id = data["id"]
            return TriggerResult(success=True, incident_id=incident_id)
        except Exception as exc:
            return TriggerResult(success=False, message=str(exc))

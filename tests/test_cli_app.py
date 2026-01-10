from typer.testing import CliRunner

from judicor.cli import app
from judicor.domain.models import Incident, IncidentState


class _StubClient:
    def __init__(self):
        self.calls = []

    def list_incidents(self):
        self.calls.append("list")
        return [Incident(id=1, title="Title", state=IncidentState.ACTIVE)]

    def attach_incident(self, incident_id: int):
        self.calls.append(f"attach:{incident_id}")
        from judicor.domain.results import AttachResult

        return AttachResult(success=True, incident_id=incident_id)

    def detach_incident(self):
        self.calls.append("detach")
        from judicor.domain.results import Result

        return Result(success=True, message="detached")

    def ask_ai(self, question: str):
        self.calls.append(f"ask:{question}")
        from judicor.domain.results import AskResult

        return AskResult(success=True, answer="answer", confidence=0.9)

    def status_incident(self):
        self.calls.append("status")
        from judicor.domain.results import StatusResult

        return StatusResult(success=True, state="active", summary="ok")

    def resolve_incident(self):
        self.calls.append("resolve")
        from judicor.domain.results import Result

        return Result(success=True, message="resolved")

    def trigger(self):
        self.calls.append("trigger")
        from judicor.domain.results import TriggerResult

        return TriggerResult(success=True, incident_id=2)


def test_list_command_uses_client(monkeypatch):
    runner = CliRunner()
    client = _StubClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["list"])

    assert result.exit_code == 0
    assert "ID: 1" in result.stdout
    assert client.calls == ["list"]


def test_context_command(monkeypatch):
    runner = CliRunner()
    client = _StubClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["context"])

    assert result.exit_code == 0
    assert "Attached incident state" in result.stdout

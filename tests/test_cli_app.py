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


class _FailingClient(_StubClient):
    def attach_incident(self, incident_id: int):
        from judicor.domain.results import AttachResult

        return AttachResult(success=False, message="Incident not found")

    def detach_incident(self):
        from judicor.domain.results import Result

        return Result(success=False, message="No incident attached")

    def ask_ai(self, question: str):
        from judicor.domain.results import AskResult

        return AskResult(success=False, message="No incident attached")

    def status_incident(self):
        from judicor.domain.results import StatusResult

        return StatusResult(
            success=False,
            state="none",
            summary="No incident attached",
            message="No incident attached",
        )

    def resolve_incident(self):
        from judicor.domain.results import Result

        return Result(success=False, message="No incident attached")

    def trigger(self):
        from judicor.domain.results import TriggerResult

        return TriggerResult(success=False, message="backend down")


def test_ask_command_exits_on_failure(monkeypatch):
    runner = CliRunner()
    client = _FailingClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["ask", "why?"])

    assert result.exit_code == 1
    assert "No incident attached" in result.stdout


def test_context_command_exits_on_missing_session(monkeypatch):
    runner = CliRunner()
    client = _FailingClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["context"])

    assert result.exit_code == 1
    assert "No incident attached" in result.stdout


def test_status_command_exits_on_missing_session(monkeypatch):
    runner = CliRunner()
    client = _FailingClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["status"])

    assert result.exit_code == 1
    assert "No incident attached" in result.stdout


def test_attach_command_exits_on_failure(monkeypatch):
    runner = CliRunner()
    client = _FailingClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["attach", "99"])

    assert result.exit_code == 1
    assert "Incident not found" in result.stdout


def test_detach_command_exits_on_failure(monkeypatch):
    runner = CliRunner()
    client = _FailingClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["detach"])

    assert result.exit_code == 1
    assert "No incident attached" in result.stdout


def test_resolve_command_exits_on_failure(monkeypatch):
    runner = CliRunner()
    client = _FailingClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["resolve"])

    assert result.exit_code == 1
    assert "No incident attached" in result.stdout


def test_trigger_command_exits_on_failure(monkeypatch):
    runner = CliRunner()
    client = _FailingClient()
    monkeypatch.setattr(app, "get_client", lambda: client)

    result = runner.invoke(app.app, ["trigger"])

    assert result.exit_code == 1
    assert "backend down" in result.stdout

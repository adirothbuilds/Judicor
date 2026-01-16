# src/judicor/cli/app.py

"""
CLI application for Judicor.
"""

import typer
from judicor.client.factory import create_judicor_client

app = typer.Typer(
    name="judicor",
    help=(
        "Judicor — AI-assisted incident judgment engine for "
        "DevOps and SRE teams."
    ),
)

# -----------------------------------------------------------------------------
# Client lifecycle (singleton per CLI process)
# -----------------------------------------------------------------------------

_client_instance = None


def get_client():
    global _client_instance
    if _client_instance is None:
        try:
            # using factory to create client based on env JUDICOR_CLIENT_TYPE
            _client_instance = create_judicor_client()
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1)
    return _client_instance


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------


@app.command("init")
def init():
    """Initialize Judicor identity for this machine."""
    from judicor.identity.init_flow import run_init

    run_init()


@app.command("list")
def list_incidents():
    """List all incidents."""
    client = get_client()
    incidents = client.list_incidents()

    if not incidents:
        typer.echo("No incidents found.")
        return

    for incident in incidents:
        typer.echo(
            f"ID: {incident.id}, "
            f"Title: {incident.title}, "
            f"State: {incident.status}"
        )


@app.command("attach")
def attach_incident(incident_id: int):
    """Attach to an active incident session by ID."""
    client = get_client()
    result = client.attach_incident(incident_id)

    if result.success:
        typer.echo(f"Attached to incident {incident_id}.")
    else:
        typer.echo(f"Failed to attach: {result.message}")
        raise typer.Exit(code=1)


@app.command("detach")
def detach_incident():
    """Detach from the currently attached incident session."""
    client = get_client()
    result = client.detach_incident()

    if result.success:
        typer.echo("Detached from incident.")
    else:
        typer.echo(f"Failed to detach: {result.message}")
        raise typer.Exit(code=1)


@app.command("ask")
def ask_ai(question: str):
    """Ask a question to the AI assistant about the current incident."""
    client = get_client()
    result = client.ask_ai(question)

    if not result.success:
        typer.echo(f"AI could not answer: {result.message}")
        raise typer.Exit(code=1)

    typer.echo(f"Answer: {result.answer}")

    if result.confidence is not None:
        typer.echo(f"Confidence: {result.confidence:.2f}")

    if result.reasoning:
        typer.echo(f"Reasoning: {result.reasoning}")


@app.command("status")
def status_incident():
    """Check the status of the current session."""
    client = get_client()
    result = client.status_incident()

    if result.success:
        typer.echo(f"State: {result.state}")
        typer.echo(f"Summary: {result.summary}")
    else:
        typer.echo(f"Failed to fetch status: {result.message}")
        raise typer.Exit(code=1)


@app.command("context")
def context():
    """Show current session context."""
    client = get_client()
    status = client.status_incident()

    if not status.success:
        typer.echo("No incident attached.")
        raise typer.Exit(code=1)

    typer.echo(f"Attached incident state: {status.state}")
    typer.echo(f"Summary: {status.summary}")


@app.command("resolve")
def resolve_incident():
    """Resolve the currently attached incident and close the session."""
    client = get_client()
    result = client.resolve_incident()

    if result.success:
        typer.echo("Incident resolved successfully.")
    else:
        typer.echo(f"Failed to resolve incident: {result.message}")
        raise typer.Exit(code=1)


@app.command("trigger")
def trigger():
    """Trigger creation of a new incident session."""
    client = get_client()
    result = client.trigger()

    if result.success:
        typer.echo(f"New incident created: {result.incident_id}")
    else:
        typer.echo(f"Failed to create incident: {result.message}")
        raise typer.Exit(code=1)


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------


def main():
    app()


if __name__ == "__main__":
    main()

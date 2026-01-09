# src/judicor/identity/init_flow.py

import getpass
import hashlib
import socket
from datetime import datetime, timezone
from typing import Optional

import typer

from judicor.identity.model import Identity
from judicor.identity.store import save_identity, load_identity


def _generate_fingerprint(hostname: str, os_user: str) -> str:
    """
    Generate a stable fingerprint for this machine/user combination.
    """
    raw = f"{hostname}:{os_user}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def run_init() -> None:
    """
    Interactive initialization flow for Judicor CLI.

    Collects identity information for the current OS user and machine,
    generates a stable fingerprint, and persists it under ~/.judicor/.
    """

    existing = load_identity()
    if existing:
        typer.echo("⚠ Judicor is already initialized for this user.")
        typer.echo(
            f"  User: {existing.name} <{existing.email}>\n"
            f"  Host: {existing.hostname}\n"
            f"  Created: {existing.created_at}"
        )
        if not typer.confirm("Do you want to overwrite the existing identity?"):
            typer.echo("Initialization aborted.")
            raise typer.Exit(code=1)

    typer.echo("Welcome to Judicor.\n")
    typer.echo(
        "This CLI will be associated with your local system user.\n"
        "The information is used for accountability and audit purposes.\n"
    )

    # ------------------------------------------------------------------
    # Collect inputs
    # ------------------------------------------------------------------

    name = typer.prompt("Full name").strip()
    email = typer.prompt("Email").strip()
    org: Optional[str] = typer.prompt(
        "Organization (optional)", default="", show_default=False
    ).strip() or None

    # ------------------------------------------------------------------
    # System-derived values
    # ------------------------------------------------------------------

    hostname = socket.gethostname()
    os_user = getpass.getuser()
    fingerprint = _generate_fingerprint(hostname, os_user)

    identity = Identity(
        user_id=email,  # stable, human-meaningful identifier
        name=name,
        email=email,
        org=org,
        hostname=hostname,
        os_user=os_user,
        fingerprint=fingerprint,
        created_at=datetime.now(timezone.utc),
    )

    # ------------------------------------------------------------------
    # Persist
    # ------------------------------------------------------------------

    save_identity(identity)

    typer.echo("\n✔ Judicor identity initialized successfully.")
    typer.echo(f"  User: {identity.name} <{identity.email}>")
    typer.echo(f"  Host: {identity.hostname}")
    typer.echo(f"  Fingerprint: {identity.fingerprint}")
    typer.echo("  Location: ~/.judicor/identity.json\n")
    typer.echo(
        "You can now use Judicor CLI to manage incident sessions.\n"
        "Run `judicor --help` to see available commands."
    )
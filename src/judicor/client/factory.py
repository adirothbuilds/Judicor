# src/judicor/client/factory.py

import os

from judicor.client.interface import JudicorClient
from judicor.client.implementations.dummy import DummyJudicorClient
from judicor.client.implementations.http import HttpJudicorClient

DEFAULT_CLIENT_TYPE = "dummy"


def create_judicor_client() -> JudicorClient:
    """
    Factory function to create a JudicorClient instance
    based on the `JUDICOR_CLIENT_TYPE` environment variable.

    Returns:
        JudicorClient: An instance of a JudicorClient implementation.

    Raises:
        ValueError: If the specified client type is unknown.
    """
    client_type = os.getenv("JUDICOR_CLIENT_TYPE", DEFAULT_CLIENT_TYPE).lower()

    if client_type == "dummy":
        return DummyJudicorClient()
    if client_type == "http":
        return HttpJudicorClient()
    else:
        raise ValueError(f"Unknown Judicor client type: {client_type}")

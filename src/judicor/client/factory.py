# src/judicor/client/factory.py

from judicor.client.interface import JudicorClient
from judicor.client.implementations.dummy import DummyJudicorClient


def create_judicor_client(type: str) -> JudicorClient:
    """
    Factory function to create a JudicorClient instance,
    based on the specified type.

    Args:
        type (str): The type of client to create. Currently supports 'dummy'.

    Returns:
        JudicorClient: An instance of a JudicorClient implementation.

    Raises:
        ValueError: If an unsupported client type is specified.
    """
    if type == "dummy":
        return DummyJudicorClient()
    else:
        raise ValueError(f"Unsupported client type: {type}")

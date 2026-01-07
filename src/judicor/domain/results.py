# src/judicor/domain/results.py

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Result:
    """
    Base result type for all Judicor operations.

    Represents the outcome of a domain-level action, independent of
    transport (CLI, HTTP) or execution environment.

    Attributes:
        success (bool): Whether the operation completed successfully.
        message (Optional[str]): Optional human-readable message
            providing additional context or error details.
    """

    success: bool
    message: Optional[str] = None


@dataclass
class AttachResult(Result):
    """
    Result of attaching to an incident session.

    Attributes:
        incident_id (Optional[int]): Identifier of the incident
            session that was attached, if successful.
    """

    incident_id: Optional[int] = None


@dataclass
class AskResult(Result):
    """
    Result of an AI-assisted reasoning query within an incident session.

    Attributes:
        answer (Optional[Any]): The answer produced by the reasoning engine.
            Kept generic to allow future structured responses.
        confidence (Optional[float]): Confidence score representing the
            engine's certainty in the answer (0.0-1.0).
        reasoning (Optional[str]): Optional explanation or reasoning trace
            behind the answer.
    """

    answer: Optional[Any] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None

    def __post_init__(self):
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be a float between 0.0 and 1.0")


@dataclass
class TriggerResult(Result):
    """
    Result of triggering a new incident session.

    Attributes:
        incident_id (Optional[int]): Identifier of the newly created
            incident session, if successful.
    """

    incident_id: Optional[int] = None


@dataclass
class StatusResult(Result):
    """
    Result representing the current state of an incident session.

    Attributes:
        state (Optional[str]): Current lifecycle state of the incident
            (e.g. OPEN, INVESTIGATING, RESOLVED).
        summary (Optional[str]): Short human-readable summary of the
            incident's current status.
    """

    state: Optional[str] = None
    summary: Optional[str] = None

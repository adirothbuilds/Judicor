# src/judicor/domain/models.py

from dataclasses import dataclass


@dataclass
class Incident:
    id: int
    title: str
    status: str

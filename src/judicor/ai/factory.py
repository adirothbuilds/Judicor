# src/judicor/ai/factory.py

import os

from judicor.ai.interface import AIReasoner
from judicor.ai.implementations.dummy import DummyAIReasoner
from judicor.ai.implementations.gemini import GeminiAIReasoner

DEFAULT_AI_PROVIDER = "dummy"


def create_ai_reasoner() -> AIReasoner:
    ai_reasoner_type = os.getenv(
        "JUDICOR_AI_PROVIDER", DEFAULT_AI_PROVIDER
    ).lower()

    if ai_reasoner_type == "dummy":
        return DummyAIReasoner()
    elif ai_reasoner_type == "gemini":
        return GeminiAIReasoner()
    else:
        raise ValueError(
            f"Unknown Judicor ai reasoner type: {ai_reasoner_type}"
        )

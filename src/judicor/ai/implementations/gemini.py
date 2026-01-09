# src/judicor/ai/implementations/gemini.py

import os
from google import genai

from judicor.ai.interface import AIReasoner
from judicor.domain.models import Incident
from judicor.domain.results import AskResult


class GeminiAIReasoner(AIReasoner):
    """
    Gemini-based AI reasoner.

    Responsible ONLY for:
    - Building a prompt
    - Sending it to Gemini
    - Returning raw output (no validation / policy)
    """

    def __init__(self, model: str = "gemini-3-flash-preview"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")

        # Client picks API key from env
        self.client = genai.Client()
        self.model = model

    def ask(self, incident: Incident, question: str) -> AskResult:
        prompt = self._build_prompt(incident, question)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        except Exception as exc:  # pragma: no cover - upstream client errors
            return AskResult(success=False, message=str(exc))

        text = (getattr(response, "text", "") or "").strip()

        return AskResult(
            True,
            answer=text,
            # Gemini SDK does not provide a native probability score; default to 1.0
            confidence=1.0,
            reasoning=None,
        )

    def _build_prompt(self, incident: Incident, question: str) -> str:
        return f"""
You are an AI assistant helping investigate a production incident.

Incident:
- ID: {incident.id}
- Title: {incident.title}
- Status: {incident.status}

Question:
{question}

Answer clearly and concisely.
"""

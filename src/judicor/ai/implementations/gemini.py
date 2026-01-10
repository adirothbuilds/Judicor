# src/judicor/ai/implementations/gemini.py

import os
from google import genai

from judicor.ai.interface import AIReasoner
from judicor.ai.roles import AgentRole
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

    def __init__(self, role: AgentRole, model: str = "gemini-3-flash-preview"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")

        # Client picks API key from env
        self.client = genai.Client()
        self.model = model
        self.role = role

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
            # Gemini SDK lacks native probability score; default to 1.0
            confidence=1.0,
            reasoning=None,
        )

    def _build_prompt(self, incident: Incident, question: str) -> str:
        if self.role == AgentRole.ANALYZER:
            instruction = "Analyze the incident and highlight likely causes."
        elif self.role == AgentRole.INVESTIGATOR:
            instruction = (
                "Investigate using given context and return concise findings."
            )
        elif self.role == AgentRole.SUMMARIZER:
            instruction = (
                "Produce a concise rolling summary capturing key findings "
                "and current state."
            )
        elif self.role == AgentRole.RESOLVER:
            instruction = (
                "Provide closure reasoning with root cause and "
                "resolution steps."
            )
        else:
            instruction = "Provide helpful reasoning."

        return f"""
You are an AI assistant helping investigate a production incident.

Role: {self.role.value}
Instruction: {instruction}

Incident:
- ID: {incident.id}
- Title: {incident.title}
- State: {incident.status}

Context:
{question}

Respond concisely and stay within your role.
"""

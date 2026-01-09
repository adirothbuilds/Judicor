# src/judicor/ai/policy.py

from judicor.domain.results import AskResult


class ReasoningPolicy:
    """
    Applies judgment and validation rules on AI reasoning outputs.
    """

    MIN_CONFIDENCE = 0.6

    def evaluate(self, result: AskResult) -> AskResult:
        if not result.success:
            return result

        if result.confidence is None:
            return AskResult(
                success=False,
                message="AI response missing confidence score",
            )

        if result.confidence < self.MIN_CONFIDENCE:
            return AskResult(
                success=False,
                message=(
                    "AI confidence below acceptable threshold "
                    f"({result.confidence:.2f})"
                ),
                answer=result.answer,
                confidence=result.confidence,
                reasoning=result.reasoning,
            )

        return result

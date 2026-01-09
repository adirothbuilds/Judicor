from judicor.ai.policy import ReasoningPolicy
from judicor.domain.results import AskResult


def test_policy_returns_failure_unchanged_on_error():
    policy = ReasoningPolicy()
    result = AskResult(success=False, message="boom")
    assert policy.evaluate(result) is result


def test_policy_rejects_missing_confidence():
    policy = ReasoningPolicy()
    result = AskResult(success=True, answer="hi")
    evaluated = policy.evaluate(result)
    assert not evaluated.success
    assert evaluated.message == "AI response missing confidence score"


def test_policy_rejects_low_confidence():
    policy = ReasoningPolicy()
    result = AskResult(success=True, answer="hi", confidence=0.5, reasoning="r")
    evaluated = policy.evaluate(result)
    assert not evaluated.success
    assert "below acceptable" in evaluated.message
    assert evaluated.answer == "hi"
    assert evaluated.reasoning == "r"


def test_policy_accepts_sufficient_confidence():
    policy = ReasoningPolicy()
    result = AskResult(success=True, answer="ok", confidence=0.9)
    evaluated = policy.evaluate(result)
    assert evaluated is result

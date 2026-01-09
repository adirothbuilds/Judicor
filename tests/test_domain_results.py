import pytest

from judicor.domain.results import AskResult


def test_ask_result_confidence_bounds():
    assert AskResult(success=True, confidence=0.0).confidence == 0.0
    assert AskResult(success=True, confidence=1.0).confidence == 1.0


def test_ask_result_confidence_out_of_range():
    with pytest.raises(ValueError):
        AskResult(success=True, confidence=1.5)

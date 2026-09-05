"""Unit tests for the eval scoring functions."""

from __future__ import annotations

from app.eval.dataset import EvalQuestion
from app.eval.metrics import (
    first_number,
    is_correct,
    numeric_match,
    rate,
    retrieval_hit,
    text_match,
)
from app.schemas import Answer, Citation


def _question(**overrides) -> EvalQuestion:
    """Build an EvalQuestion with sensible defaults, overriding as needed."""
    base = dict(
        id="q",
        question="?",
        answer="",
        answer_type="text",
        gold_doc="doc.pdf",
        gold_page=1,
        requires_visual=False,
        unanswerable=False,
    )
    base.update(overrides)
    return EvalQuestion(**base)


def _answer(**overrides) -> Answer:
    base = dict(mode="text", answer="", confidence=0.0, abstained=False)
    base.update(overrides)
    return Answer(**base)


def test_first_number_strips_currency_units_and_commas():
    assert first_number("$42 million") == 42.0
    assert first_number("revenue was 1,500 units") == 1500.0
    assert first_number("no digits here") is None


def test_numeric_match_within_tolerance():
    assert numeric_match("about 42.5", 42.0, tolerance=0.02) is True  # ~1.2% off
    assert numeric_match("about 50", 42.0, tolerance=0.02) is False
    assert numeric_match("no number", 42.0, tolerance=0.02) is False


def test_numeric_match_handles_zero_gold():
    assert numeric_match("0.01", 0.0, tolerance=0.02) is True
    assert numeric_match("5", 0.0, tolerance=0.02) is False


def test_text_match_is_normalised_containment():
    assert text_match("Headquartered in Denver, Colorado.", "denver") is True
    assert text_match("The capital is Paris.", "London") is False


def test_is_correct_unanswerable_requires_abstention():
    q = _question(unanswerable=True, gold_page=None)
    assert is_correct(q, _answer(abstained=True)) is True
    # Answering an unanswerable question is wrong even if it "looks" plausible.
    assert is_correct(q, _answer(abstained=False, answer="something")) is False


def test_is_correct_abstaining_on_answerable_is_wrong():
    q = _question(answer_type="text", answer="denver")
    assert is_correct(q, _answer(abstained=True, answer="denver")) is False


def test_is_correct_dispatches_numeric_vs_text():
    numeric_q = _question(answer_type="numeric", answer="42", value=42.0, tolerance=0.02)
    assert is_correct(numeric_q, _answer(answer="revenue was 42 million")) is True

    text_q = _question(answer_type="text", answer="Denver")
    assert is_correct(text_q, _answer(answer="It is in Denver.")) is True
    assert is_correct(text_q, _answer(answer="It is in Boston.")) is False


def test_retrieval_hit_checks_gold_page_in_citations():
    q = _question(gold_page=2)
    cite = Citation(
        document_id="d",
        document_title="t",
        page_number=2,
        image_url="/storage/x.png",
        score=0.9,
    )
    assert retrieval_hit(q, [cite]) is True
    assert retrieval_hit(q, []) is False
    # No gold page defined -> cannot be a hit.
    assert retrieval_hit(_question(gold_page=None), [cite]) is False


def test_rate_rounds_and_handles_zero_total():
    assert rate(1, 3) == 0.3333
    assert rate(0, 0) == 0.0

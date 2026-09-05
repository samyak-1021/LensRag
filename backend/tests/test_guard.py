"""Unit tests for the hallucination guard."""

from __future__ import annotations

from app.services.guard import INSUFFICIENT_MESSAGE, apply_guard


def test_passes_through_when_grounded():
    abstained, answer, confidence = apply_guard(0.8, "Revenue was 42 million.", min_score=0.25)
    assert abstained is False
    assert answer == "Revenue was 42 million."
    assert confidence == 0.8


def test_abstains_on_low_retrieval_score():
    # Best passage scored below the threshold -> abstain regardless of model text.
    abstained, answer, confidence = apply_guard(0.10, "A confident wrong answer.", min_score=0.25)
    assert abstained is True
    assert answer == INSUFFICIENT_MESSAGE
    assert confidence == 0.1


def test_abstains_when_model_self_reports_insufficient():
    # Strong retrieval but the model said it couldn't answer -> still abstain.
    abstained, answer, _ = apply_guard(0.9, "Insufficient information.", min_score=0.25)
    assert abstained is True
    assert answer == INSUFFICIENT_MESSAGE


def test_confidence_is_rounded_top_score():
    _, _, confidence = apply_guard(0.123456, "grounded answer", min_score=0.05)
    assert confidence == 0.1235  # round(top_score, 4)


def test_answer_is_stripped_when_grounded():
    _, answer, _ = apply_guard(0.5, "  padded answer  ", min_score=0.25)
    assert answer == "padded answer"

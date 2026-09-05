"""Scoring functions for the eval harness.

Kept dependency-free and deterministic. Correctness is judged per question type:
numeric (within tolerance), text/choice (normalised containment), and unanswerable
(correct only if the system abstained — this is how we score the guard).
"""

from __future__ import annotations

import re

from app.eval.dataset import EvalQuestion
from app.schemas import Answer, Citation

_NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def first_number(text: str) -> float | None:
    """Extract the first numeric value from a string, ignoring $, %, commas, units."""
    match = _NUMBER_RE.search(text.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group().replace(",", ""))
    except ValueError:
        return None


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def numeric_match(prediction: str, value: float, tolerance: float) -> bool:
    pred = first_number(prediction)
    if pred is None:
        return False
    if value == 0:
        return abs(pred) <= tolerance
    return abs(pred - value) / abs(value) <= tolerance


def text_match(prediction: str, gold: str) -> bool:
    return _normalise(gold) in _normalise(prediction)


def is_correct(question: EvalQuestion, answer: Answer) -> bool:
    if question.unanswerable:
        return answer.abstained  # abstaining is the right call
    if answer.abstained:
        return False
    if question.answer_type == "numeric" and question.value is not None:
        return numeric_match(answer.answer, question.value, question.tolerance)
    return text_match(answer.answer, question.answer)


def retrieval_hit(question: EvalQuestion, citations: list[Citation]) -> bool:
    """True if the gold page appears among the retrieved citations (recall@k)."""
    if question.gold_page is None:
        return False
    return any(c.page_number == question.gold_page for c in citations)


def rate(correct: int, total: int) -> float:
    return round(correct / total, 4) if total else 0.0

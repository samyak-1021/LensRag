"""Tests that the committed evaluation dataset loads into typed questions."""

from __future__ import annotations

from app.config import BACKEND_DIR
from app.eval.dataset import EvalQuestion, load_questions

QA_PATH = BACKEND_DIR / "data" / "eval" / "qa.jsonl"


def test_loads_the_real_qa_dataset():
    questions = load_questions(QA_PATH)
    # The committed chart/table-QA set is sizeable (>100 questions).
    assert len(questions) > 100
    assert all(isinstance(q, EvalQuestion) for q in questions)


def test_every_question_has_the_expected_fields():
    questions = load_questions(QA_PATH)
    q = questions[0]
    # Spot-check the dataclass surface the harness relies on.
    for field in (
        "id",
        "question",
        "answer",
        "answer_type",
        "gold_doc",
        "requires_visual",
        "unanswerable",
    ):
        assert hasattr(q, field)
    assert q.answer_type in {"numeric", "text", "choice"}


def test_dataset_contains_visual_and_unanswerable_questions():
    # The set is designed to exercise both the visual path and the guard.
    questions = load_questions(QA_PATH)
    assert any(q.requires_visual for q in questions)
    assert any(q.unanswerable for q in questions)

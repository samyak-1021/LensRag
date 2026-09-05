"""Load the chart/table-QA evaluation set (``data/eval/qa.jsonl``)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvalQuestion:
    id: str
    question: str
    answer: str  # human-readable gold answer
    answer_type: str  # "numeric" | "text" | "choice"
    gold_doc: str  # source PDF filename (resolves to a document at run time)
    gold_page: int | None  # 1-based page the answer lives on (None if unanswerable)
    requires_visual: bool  # True when the value only exists inside a chart/table image
    unanswerable: bool  # True when the doc does not contain the answer (guard test)
    value: float | None = None  # parsed numeric gold (for numeric matching)
    tolerance: float = 0.02  # relative tolerance for numeric matching


def load_questions(path: Path) -> list[EvalQuestion]:
    questions: list[EvalQuestion] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        raw = json.loads(line)
        questions.append(EvalQuestion(**raw))
    return questions

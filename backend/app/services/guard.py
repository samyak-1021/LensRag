"""Hallucination guard.

The single most common failure of "chat with your PDF" is confidently inventing
an answer that isn't in the document. The guard makes the system abstain instead
when either signal says grounding is weak:

1. Retrieval grounding — the best retrieved passage/page scores below a threshold.
2. Model self-report — the LLM followed the prompt and said "insufficient".

Abstention is a first-class, *measured* outcome (see the eval harness): on
unanswerable questions, abstaining is the correct answer.
"""

from __future__ import annotations

INSUFFICIENT_MESSAGE = (
    "I couldn't find enough information in the document(s) to answer this "
    "confidently. Try rephrasing, or check that the relevant page was uploaded."
)


def _looks_insufficient(text: str) -> bool:
    lowered = text.strip().lower()
    return lowered.startswith("insufficient") or "insufficient information" in lowered


def apply_guard(
    top_score: float, model_text: str, min_score: float
) -> tuple[bool, str, float]:
    """Return ``(abstained, answer, confidence)``.

    Confidence is the top retrieval score (0..1) — an honest, grounding-based
    signal rather than a made-up number.
    """
    confidence = round(float(top_score), 4)
    if top_score < min_score or _looks_insufficient(model_text):
        return True, INSUFFICIENT_MESSAGE, confidence
    return False, model_text.strip(), confidence

"""Pydantic request/response schemas — the API contract shared with the frontend."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["text", "visual", "compare"]


# ---------------------------------------------------------------- Documents ---
class DocumentOut(BaseModel):
    id: str
    filename: str
    title: str
    num_pages: int
    size_bytes: int
    status: str
    error: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PageOut(BaseModel):
    page_number: int
    image_url: str
    width: int
    height: int
    has_text: bool

    class Config:
        from_attributes = True


class DocumentDetail(DocumentOut):
    pages: list[PageOut] = []


# -------------------------------------------------------------------- Query ---
class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_id: str | None = None  # None = search across all documents
    mode: Mode = "visual"
    top_k: int | None = None


class Citation(BaseModel):
    """A provenance pointer: which page (and region) an answer came from."""

    document_id: str
    document_title: str
    page_number: int
    image_url: str
    score: float
    snippet: str = ""
    # Normalised [x0, y0, x1, y1] in 0..1 — the highlighted region on the page image.
    bbox: list[float] | None = None


class Answer(BaseModel):
    mode: Mode
    answer: str
    confidence: float
    abstained: bool
    citations: list[Citation] = []
    latency_ms: int = 0
    provider: str = ""


class CompareAnswer(BaseModel):
    """Side-by-side text-RAG vs visual-RAG — the recall-gap demonstration."""

    question: str
    text: Answer
    visual: Answer


# --------------------------------------------------------------------- Eval ---
class EvalMetric(BaseModel):
    label: str
    text: float
    visual: float


class EvalSummary(BaseModel):
    generated_at: datetime | None = None
    is_real_run: bool = False  # True only when real Gemini/ColPali produced it
    num_questions: int
    metrics: list[EvalMetric]  # recall@k, answer accuracy, chart-QA accuracy, ...
    guard_abstention_rate: float
    notes: str = ""

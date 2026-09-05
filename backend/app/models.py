"""SQLAlchemy ORM models.

A document is split into pages; each page yields text chunks (for text-RAG) and a
rendered image (for visual-RAG + cited-region highlighting). Embeddings are stored
as JSON so the schema is identical on SQLite and Postgres.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(UTC)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(String(512))
    title: Mapped[str] = mapped_column(String(512), default="")
    num_pages: Mapped[int] = mapped_column(Integer, default=0)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    # "processing" -> "ready" -> "failed"
    status: Mapped[str] = mapped_column(String(32), default="processing")
    error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    pages: Mapped[list[Page]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    chunks: Mapped[list[Chunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    page_number: Mapped[int] = mapped_column(Integer)  # 1-based
    image_path: Mapped[str] = mapped_column(String(1024))  # relative to storage dir
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text, default="")  # extracted text (may be sparse)
    # Single embedding representing the whole page — powers visual-RAG retrieval.
    embedding: Mapped[list[float] | None] = mapped_column(JSON, default=None)

    document: Mapped[Document] = relationship(back_populates="pages")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    page_number: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(JSON)  # text-RAG vector
    # Normalised [x0, y0, x1, y1] location of this chunk on its page image, used
    # to draw the cited-region highlight. None if the text couldn't be located.
    bbox: Mapped[list[float] | None] = mapped_column(JSON, default=None)

    document: Mapped[Document] = relationship(back_populates="chunks")


class QueryLog(Base):
    """Lightweight record of each question — powers the dashboard activity feed."""

    __tablename__ = "query_logs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    document_id: Mapped[str | None] = mapped_column(String(32), default=None)
    question: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(16))  # text | visual | compare
    answer: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    abstained: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

"""Vector retrieval.

At demo scale (tens of documents, a few thousand vectors) an exact numpy cosine
search is both simplest and fastest. The seam is deliberately thin: swapping in a
pgvector / Qdrant ANN index for 100k+ vectors means replacing just these two
functions — the callers are unaware of the backend. See DESIGN.md for the
trade-off. Embeddings are pre-normalised, so cosine similarity is a dot product.
"""

from __future__ import annotations

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chunk, Page


def _cosine_top_k(
    query: list[float], matrix: np.ndarray, k: int
) -> tuple[list[int], list[float]]:
    """Return (indices, scores) of the top-k rows in ``matrix`` by cosine similarity."""
    if matrix.shape[0] == 0:
        return [], []
    q = np.asarray(query, dtype=np.float32)
    sims = matrix @ q  # dot product == cosine for normalised vectors
    k = min(k, sims.shape[0])
    # argpartition gets the top-k unordered in O(n), then we sort just those k.
    top = np.argpartition(-sims, k - 1)[:k]
    top = top[np.argsort(-sims[top])]
    # Clamp to [0, 1]; tiny negatives can appear from float error.
    return top.tolist(), [float(max(0.0, min(1.0, sims[i]))) for i in top]


async def search_chunks(
    session: AsyncSession, query_vec: list[float], document_id: str | None, k: int
) -> list[tuple[Chunk, float]]:
    """Top-k text chunks for text-RAG."""
    stmt = select(Chunk)
    if document_id:
        stmt = stmt.where(Chunk.document_id == document_id)
    rows = list((await session.scalars(stmt)).all())
    if not rows:
        return []
    matrix = np.asarray([r.embedding for r in rows], dtype=np.float32)
    idx, scores = _cosine_top_k(query_vec, matrix, k)
    return [(rows[i], s) for i, s in zip(idx, scores, strict=True)]


async def search_pages(
    session: AsyncSession, query_vec: list[float], document_id: str | None, k: int
) -> list[tuple[Page, float]]:
    """Top-k pages for the mock visual retriever (page-embedding proxy)."""
    stmt = select(Page).where(Page.embedding.is_not(None))
    if document_id:
        stmt = stmt.where(Page.document_id == document_id)
    rows = list((await session.scalars(stmt)).all())
    if not rows:
        return []
    matrix = np.asarray([r.embedding for r in rows], dtype=np.float32)
    idx, scores = _cosine_top_k(query_vec, matrix, k)
    return [(rows[i], s) for i, s in zip(idx, scores, strict=True)]

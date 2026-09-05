"""RAG orchestration: retrieve -> generate -> guard -> attach citations.

Three entry points power the product:
* ``answer_text``    — the plain text-RAG baseline (what everyone ships).
* ``answer_visual``  — retrieve pages as images, answer with a VLM (reads charts).
* ``answer_compare`` — run both for the same question, side by side. This is the
  recall-gap demonstration that proves the visual path is worth it.
"""

from __future__ import annotations

import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Document, Page
from app.schemas import Answer, Citation, CompareAnswer
from app.services.embeddings import get_embedder
from app.services.guard import apply_guard
from app.services.providers import get_provider
from app.services.retrieval import search_chunks
from app.services.visual import get_visual_retriever


def _image_url(image_path: str) -> str:
    """Public URL for a stored page image (served from the /storage mount)."""
    return f"/storage/{image_path}"


async def _docs_by_id(session: AsyncSession, ids: set[str]) -> dict[str, Document]:
    if not ids:
        return {}
    rows = (await session.scalars(select(Document).where(Document.id.in_(ids)))).all()
    return {d.id: d for d in rows}


async def _pages_by_key(
    session: AsyncSession, keys: set[tuple[str, int]]
) -> dict[tuple[str, int], Page]:
    """Look up pages by (document_id, page_number) for chunk citations."""
    lookup: dict[tuple[str, int], Page] = {}
    for doc_id, page_number in keys:
        page = (
            await session.scalars(
                select(Page).where(
                    Page.document_id == doc_id, Page.page_number == page_number
                )
            )
        ).first()
        if page:
            lookup[(doc_id, page_number)] = page
    return lookup


async def answer_text(
    session: AsyncSession, question: str, document_id: str | None, top_k: int
) -> Answer:
    started = time.perf_counter()
    settings = get_settings()
    provider = get_provider()

    query_vec = get_embedder().embed([question])[0]
    hits = await search_chunks(session, query_vec, document_id, top_k)

    contexts = [chunk.text for chunk, _ in hits]
    model_text = await provider.answer(question, contexts)
    top_score = hits[0][1] if hits else 0.0
    abstained, final_answer, confidence = apply_guard(
        top_score, model_text, settings.guard_min_score
    )

    docs = await _docs_by_id(session, {c.document_id for c, _ in hits})
    pages = await _pages_by_key(session, {(c.document_id, c.page_number) for c, _ in hits})
    citations = [
        Citation(
            document_id=chunk.document_id,
            document_title=docs[chunk.document_id].title,
            page_number=chunk.page_number,
            image_url=_image_url(pages[(chunk.document_id, chunk.page_number)].image_path),
            score=round(score, 4),
            snippet=_truncate(chunk.text),
            bbox=chunk.bbox,
        )
        for chunk, score in hits
        if (chunk.document_id, chunk.page_number) in pages
    ]
    return Answer(
        mode="text",
        answer=final_answer,
        confidence=confidence,
        abstained=abstained,
        citations=citations,
        latency_ms=int((time.perf_counter() - started) * 1000),
        provider=provider.name,
    )


async def answer_visual(
    session: AsyncSession, question: str, document_id: str | None, top_k: int
) -> Answer:
    started = time.perf_counter()
    settings = get_settings()
    provider = get_provider()
    retriever = get_visual_retriever()

    hits = await retriever.search(session, question, document_id, top_k)

    contexts = [page.text for page, _ in hits]
    image_paths = [str(settings.storage_dir / page.image_path) for page, _ in hits]
    model_text = await provider.answer(question, contexts, image_paths=image_paths)
    top_score = hits[0][1] if hits else 0.0
    abstained, final_answer, confidence = apply_guard(
        top_score, model_text, settings.guard_min_score
    )

    docs = await _docs_by_id(session, {p.document_id for p, _ in hits})
    citations = [
        Citation(
            document_id=page.document_id,
            document_title=docs[page.document_id].title,
            page_number=page.page_number,
            image_url=_image_url(page.image_path),
            score=round(score, 4),
            snippet=_truncate(page.text),
            bbox=None,  # real ColPali can return the top patch region here
        )
        for page, score in hits
    ]
    return Answer(
        mode="visual",
        answer=final_answer,
        confidence=confidence,
        abstained=abstained,
        citations=citations,
        latency_ms=int((time.perf_counter() - started) * 1000),
        provider=provider.name,
    )


async def answer_compare(
    session: AsyncSession, question: str, document_id: str | None, top_k: int
) -> CompareAnswer:
    text = await answer_text(session, question, document_id, top_k)
    visual = await answer_visual(session, question, document_id, top_k)
    return CompareAnswer(question=question, text=text, visual=visual)


def _truncate(text: str, limit: int = 240) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"

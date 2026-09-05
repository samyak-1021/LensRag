"""PDF ingestion: PDF bytes -> page images + text -> chunks -> embeddings -> DB.

Uses PyMuPDF (fitz) to both render each page to a PNG (for visual-RAG and the
cited-region highlight) and extract its text (for the text-RAG baseline). Each
chunk's location on the page is recorded so answers can highlight exactly where
they came from.
"""

from __future__ import annotations

import pymupdf  # PyMuPDF
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Chunk, Document, Page
from app.services.chunking import chunk_text
from app.services.embeddings import get_embedder

_RENDER_DPI = 120  # legible page images without bloating disk usage


def _normalise_bbox(rect: pymupdf.Rect, page_rect: pymupdf.Rect) -> list[float]:
    """Convert an absolute PDF rect to a normalised [x0, y0, x1, y1] in 0..1."""
    w = page_rect.width or 1.0
    h = page_rect.height or 1.0
    return [rect.x0 / w, rect.y0 / h, rect.x1 / w, rect.y1 / h]


async def ingest_pdf(
    session: AsyncSession, pdf_bytes: bytes, filename: str
) -> Document:
    """Parse, render, embed and persist a PDF. Returns the ready Document."""
    settings = get_settings()
    embedder = get_embedder()

    document = Document(
        filename=filename, size_bytes=len(pdf_bytes), status="processing"
    )
    session.add(document)
    await session.flush()  # assigns document.id

    doc_dir = settings.storage_dir / document.id
    doc_dir.mkdir(parents=True, exist_ok=True)

    try:
        pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:  # noqa: BLE001 - surface parse failures to the UI
        document.status = "failed"
        document.error = f"Could not open PDF: {exc}"
        await session.commit()
        return document

    document.title = (pdf.metadata or {}).get("title") or filename
    document.num_pages = pdf.page_count

    for page_index, page in enumerate(pdf):
        page_number = page_index + 1
        pixmap = page.get_pixmap(dpi=_RENDER_DPI)
        rel_path = f"{document.id}/page-{page_number}.png"
        pixmap.save(str(settings.storage_dir / rel_path))

        text = page.get_text("text")
        page_row = Page(
            document_id=document.id,
            page_number=page_number,
            image_path=rel_path,
            width=pixmap.width,
            height=pixmap.height,
            text=text,
            embedding=embedder.embed([text])[0],  # proxy page embedding
        )
        session.add(page_row)

        # Chunk the page text; locate each chunk on the page for highlighting.
        for chunk in chunk_text(
            text,
            target=settings.chunk_target_tokens,
            overlap=settings.chunk_overlap_tokens,
        ):
            needle = " ".join(chunk.split()[:8])
            rects = page.search_for(needle) if needle else []
            bbox = _normalise_bbox(rects[0], page.rect) if rects else None
            session.add(
                Chunk(
                    document_id=document.id,
                    page_number=page_number,
                    text=chunk,
                    embedding=embedder.embed([chunk])[0],
                    bbox=bbox,
                )
            )

    pdf.close()
    document.status = "ready"
    await session.commit()
    await session.refresh(document)
    return document

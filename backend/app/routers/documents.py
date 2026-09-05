"""Document upload / list / detail / delete."""

from __future__ import annotations

import shutil

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import delete, select

from app.config import get_settings
from app.deps import SessionDep
from app.models import Chunk, Document, Page
from app.schemas import DocumentDetail, DocumentOut, PageOut
from app.services.ingest import ingest_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut, status_code=201)
async def upload_document(session: SessionDep, file: UploadFile) -> Document:
    name = file.filename or "document.pdf"
    if not name.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    return await ingest_pdf(session, pdf_bytes, name)


@router.get("", response_model=list[DocumentOut])
async def list_documents(session: SessionDep) -> list[Document]:
    rows = await session.scalars(select(Document).order_by(Document.created_at.desc()))
    return list(rows.all())


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(session: SessionDep, document_id: str) -> DocumentDetail:
    document = await session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    pages = await session.scalars(
        select(Page).where(Page.document_id == document_id).order_by(Page.page_number)
    )
    page_out = [
        PageOut(
            page_number=p.page_number,
            image_url=f"/storage/{p.image_path}",
            width=p.width,
            height=p.height,
            has_text=bool(p.text.strip()),
        )
        for p in pages.all()
    ]
    return DocumentDetail(**DocumentOut.model_validate(document).model_dump(), pages=page_out)


@router.delete("/{document_id}", status_code=204)
async def delete_document(session: SessionDep, document_id: str) -> None:
    document = await session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    # Remove child rows explicitly (portable across SQLite/Postgres), then the doc.
    await session.execute(delete(Chunk).where(Chunk.document_id == document_id))
    await session.execute(delete(Page).where(Page.document_id == document_id))
    await session.execute(delete(Document).where(Document.id == document_id))
    await session.commit()
    shutil.rmtree(get_settings().storage_dir / document_id, ignore_errors=True)

"""Question answering: text-RAG, visual-RAG, and the side-by-side comparison."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.deps import SessionDep
from app.models import QueryLog
from app.schemas import Answer, CompareAnswer, QueryRequest
from app.services.rag import answer_compare, answer_text, answer_visual

router = APIRouter(prefix="/query", tags=["query"])


async def _log(session: SessionDep, req: QueryRequest, answer: Answer) -> None:
    session.add(
        QueryLog(
            document_id=req.document_id,
            question=req.question,
            mode=req.mode,
            answer=answer.answer,
            confidence=answer.confidence,
            abstained=answer.abstained,
        )
    )
    await session.commit()


@router.post("", response_model=Answer)
async def query(session: SessionDep, req: QueryRequest) -> Answer:
    if req.mode == "compare":
        raise HTTPException(
            status_code=400, detail="Use POST /query/compare for compare mode."
        )
    top_k = req.top_k or get_settings().retrieval_top_k
    if req.mode == "visual":
        answer = await answer_visual(session, req.question, req.document_id, top_k)
    else:
        answer = await answer_text(session, req.question, req.document_id, top_k)
    await _log(session, req, answer)
    return answer


@router.post("/compare", response_model=CompareAnswer)
async def query_compare(session: SessionDep, req: QueryRequest) -> CompareAnswer:
    top_k = req.top_k or get_settings().retrieval_top_k
    result = await answer_compare(session, req.question, req.document_id, top_k)
    await _log(session, req, result.visual)
    return result

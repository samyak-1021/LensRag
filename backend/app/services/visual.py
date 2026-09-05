"""Visual page retrieval — the frontier piece.

* ``MockVisualRetriever`` — offline stand-in. Ranks pages by a single per-page
  text embedding (a proxy for visual similarity). It keeps the whole visual path
  runnable without a GPU, but it cannot read values *inside* a chart image — that
  is exactly what the real retriever below unlocks.
* ``ColPaliRetriever`` — real late-interaction visual retrieval (ColPali /
  ColQwen2). It embeds each page *image* into many patch vectors and scores them
  against the query with MaxSim, so chart/table/layout signal is preserved. Needs
  the ``[colpali]`` extra and a GPU; enable with ``LENSRAG_VISUAL_BACKEND=colpali``.

Both expose ``search(session, question, document_id, k) -> [(Page, score)]``.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Page
from app.services.embeddings import get_embedder
from app.services.retrieval import search_pages


class VisualRetriever(Protocol):
    name: str

    async def search(
        self, session: AsyncSession, question: str, document_id: str | None, k: int
    ) -> list[tuple[Page, float]]: ...


class MockVisualRetriever:
    """Ranks pages by their proxy text embedding (offline path)."""

    name = "mock"

    async def search(
        self, session: AsyncSession, question: str, document_id: str | None, k: int
    ) -> list[tuple[Page, float]]:
        query_vec = get_embedder().embed([question])[0]
        return await search_pages(session, query_vec, document_id, k)


class ColPaliRetriever:
    """Real late-interaction retrieval over page images.

    For clarity at demo scale this scores candidate page images at query time. At
    production scale you would precompute patch vectors once at ingest and run an
    ANN/MaxSim index — the interface here would not change.
    """

    name = "colpali"

    def __init__(self, model_name: str = "vidore/colqwen2-v1.0") -> None:
        # Lazy heavy imports so the base install and CI never touch torch.
        import torch
        from colpali_engine.models import ColQwen2, ColQwen2Processor

        self._torch = torch
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = ColQwen2.from_pretrained(
            model_name, torch_dtype=torch.bfloat16, device_map=self._device
        ).eval()
        self._processor = ColQwen2Processor.from_pretrained(model_name)

    async def search(
        self, session: AsyncSession, question: str, document_id: str | None, k: int
    ) -> list[tuple[Page, float]]:
        from PIL import Image

        stmt = select(Page)
        if document_id:
            stmt = stmt.where(Page.document_id == document_id)
        pages = list((await session.scalars(stmt)).all())
        if not pages:
            return []

        settings = get_settings()
        images = [
            Image.open(settings.storage_dir / p.image_path).convert("RGB")
            for p in pages
        ]
        with self._torch.no_grad():
            img_batch = self._processor.process_images(images).to(self._device)
            q_batch = self._processor.process_queries([question]).to(self._device)
            img_emb = self._model(**img_batch)
            q_emb = self._model(**q_batch)
            # MaxSim late-interaction score of the query against every page.
            scores = self._processor.score_multi_vector(q_emb, img_emb)[0].tolist()

        ranked = sorted(zip(pages, scores, strict=True), key=lambda x: x[1], reverse=True)
        # Normalise scores to 0..1 so the guard threshold is backend-agnostic.
        top = max((s for _, s in ranked), default=1.0) or 1.0
        return [(p, float(max(0.0, min(1.0, s / top)))) for p, s in ranked[:k]]


@lru_cache
def get_visual_retriever() -> VisualRetriever:
    settings = get_settings()
    if settings.visual_backend == "colpali":
        return ColPaliRetriever()
    return MockVisualRetriever()

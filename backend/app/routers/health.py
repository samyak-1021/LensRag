"""Health + runtime-config endpoints (the UI shows a mock-vs-real badge)."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.services.providers import get_provider
from app.services.visual import get_visual_retriever

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/config")
async def health_config() -> dict[str, object]:
    """Report which providers are actually active so the UI can be honest."""
    settings = get_settings()
    provider = get_provider()
    return {
        "llm_provider": provider.name,
        "visual_backend": get_visual_retriever().name,
        "embeddings_backend": settings.embeddings_backend,
        "vector_backend": settings.vector_backend,
        "is_real_generation": provider.name == "gemini",
        "model": settings.gemini_model if provider.name == "gemini" else "mock",
    }

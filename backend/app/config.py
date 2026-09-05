"""Application settings.

Everything is driven by environment variables prefixed with ``LENSRAG_`` (see
``.env.example``). Defaults are chosen so the whole system runs offline with no
API keys or external services — real Gemini/ColPali/Postgres plug in via config.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo-relative paths so storage lands next to the backend regardless of CWD.
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LENSRAG_", env_file=".env", extra="ignore"
    )

    # --- App ---
    app_name: str = "LensRAG"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    # --- Storage (rendered page images + uploaded PDFs live here) ---
    storage_dir: Path = BACKEND_DIR / "storage"

    # --- Database ---
    # SQLite by default (zero setup); Postgres+asyncpg in production.
    database_url: str = "sqlite+aiosqlite:///./lensrag.db"

    # --- Vector index ---
    # "memory": numpy cosine over embeddings loaded from the DB (no extra deps).
    # "pgvector": Postgres pgvector index for production-scale ANN search.
    vector_backend: str = "memory"

    # --- Text embeddings ---
    # "hash": deterministic, dependency-free (great for tests/CI).
    # "bge": real BAAI/bge-small-en-v1.5 semantic embeddings (needs [bge] extra).
    embeddings_backend: str = "hash"
    embedding_dim: int = 384  # bge-small dimension; the hash embedder matches it.

    # --- Answer generation (LLM / VLM) ---
    # "mock": deterministic extractive answers (offline). "gemini": real Google VLM.
    llm_provider: str = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    # --- Visual retrieval ---
    # "mock": single-vector page-text proxy (offline). "colpali": real late-interaction.
    visual_backend: str = "mock"

    # --- Retrieval / hallucination guard ---
    retrieval_top_k: int = 5
    chunk_target_tokens: int = 120  # ~words per chunk (approximate token proxy)
    chunk_overlap_tokens: int = 24
    # If the best retrieval similarity is below this, the guard makes the model
    # abstain ("insufficient information") instead of risking a hallucination.
    # Tuned for the default hash embedder (see the threshold sweep in DESIGN.md).
    # With real BGE/Gemini, raise toward ~0.4 since relevant cosines run higher.
    guard_min_score: float = Field(default=0.25, ge=0.0, le=1.0)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached singleton so settings are parsed from the environment only once."""
    return Settings()

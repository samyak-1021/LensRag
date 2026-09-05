"""Async database engine + session management.

The ORM stays portable across SQLite (local/tests) and Postgres (production) by
avoiding backend-specific column types — embeddings are stored as JSON and searched
in the retrieval layer (see ``app/services/retrieval.py``), not via a vector column.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# ``future=True`` engines are async; SQLite needs no special connect args here
# because we use the aiosqlite driver.
engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a scoped async session."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create tables on startup. Import models first so they register on Base."""
    from app import models  # noqa: F401  (registers tables on Base.metadata)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

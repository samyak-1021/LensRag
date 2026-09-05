"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session

# Annotated dependency so routes can just declare ``session: SessionDep``.
SessionDep = Annotated[AsyncSession, Depends(get_session)]

"""LensRAG FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import get_settings
from app.db import init_db
from app.routers import documents, eval, health, query

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the storage directory exists, then create database tables.
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield


app = FastAPI(
    title="LensRAG API",
    version=__version__,
    summary="Multimodal RAG that reads charts and tables in documents.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve rendered page images (used by citations + the page viewer).
settings.storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.storage_dir), name="storage")

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(eval.router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"name": "LensRAG API", "version": __version__, "docs": "/docs"}

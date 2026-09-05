"""Shared pytest fixtures for the LensRAG backend test suite.

CRITICAL ordering note: ``app/db.py`` builds the SQLAlchemy engine at import
time from ``get_settings()``, and settings are ``lru_cache``d. So the test
database / storage env vars MUST be set *before* anything under ``app`` is
imported. We therefore set them at module top level, above the ``app`` imports.
"""

from __future__ import annotations

import os
import tempfile

# --- Point the app at an isolated temp DB + storage BEFORE importing app.* -----
# One session-scoped temp dir holds both the SQLite file and the rendered page
# images; tests upload their own documents, so ordering between tests is moot.
_TMP = tempfile.mkdtemp(prefix="lensrag-tests-")
os.environ["LENSRAG_DATABASE_URL"] = f"sqlite+aiosqlite:///{_TMP}/test.db"
os.environ["LENSRAG_STORAGE_DIR"] = f"{_TMP}/storage"
# Force the offline providers so the suite is hermetic even if a real .env exists.
os.environ["LENSRAG_LLM_PROVIDER"] = "mock"
os.environ["LENSRAG_VISUAL_BACKEND"] = "mock"
os.environ["LENSRAG_EMBEDDINGS_BACKEND"] = "hash"

import pymupdf  # noqa: E402  (imported after env is set, intentionally)
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402  (must import AFTER the env vars are set above)


@pytest.fixture(scope="session")
def client():
    """A TestClient used as a context manager so the FastAPI lifespan runs.

    Entering the context triggers ``lifespan`` -> ``init_db()``, which creates
    the ORM tables in the temp SQLite database.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_pdf() -> bytes:
    """A tiny 2-page PDF with known, greppable facts on each page.

    Page 1 carries a revenue figure (42), page 2 an employee count (1500). The
    numbers are chosen so answer-extraction and citation tests have a stable,
    document-grounded ground truth.
    """
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Acme Corp annual report. Total revenue in 2023 was 42 million dollars.",
    )
    page2 = doc.new_page()
    page2.insert_text((72, 72), "The number of employees grew to 1500 in 2023.")
    data: bytes = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def uploaded_doc(client, sample_pdf):
    """Upload ``sample_pdf`` and return the parsed DocumentOut JSON body.

    Convenience fixture for the query/citation tests that need an ingested,
    ready document to ask questions against.
    """
    resp = client.post(
        "/documents",
        files={"file": ("acme.pdf", sample_pdf, "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()

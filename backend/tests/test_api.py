"""End-to-end API tests driven through the FastAPI TestClient.

These exercise the real ingest -> retrieve -> generate -> guard pipeline against
the deterministic mock providers, so they are stable and network-free.
"""

from __future__ import annotations


# ------------------------------------------------------------------- health ---
def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_config_reports_mock_stack(client):
    body = client.get("/health/config").json()
    assert body["llm_provider"] == "mock"
    assert body["visual_backend"] == "mock"
    assert body["is_real_generation"] is False
    assert body["model"] == "mock"
    # Backend descriptors are present for the UI badge.
    assert body["embeddings_backend"] == "hash"
    assert body["vector_backend"] == "memory"


# ---------------------------------------------------------------- documents ---
def test_upload_pdf_ingests_two_pages(client, sample_pdf):
    resp = client.post(
        "/documents", files={"file": ("acme.pdf", sample_pdf, "application/pdf")}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["num_pages"] == 2
    assert body["status"] == "ready"
    assert body["id"]


def test_upload_rejects_non_pdf(client):
    resp = client.post("/documents", files={"file": ("x.txt", b"hi", "text/plain")})
    assert resp.status_code == 400


def test_upload_rejects_empty_file(client):
    resp = client.post(
        "/documents", files={"file": ("empty.pdf", b"", "application/pdf")}
    )
    assert resp.status_code == 400


def test_list_documents_includes_uploaded(client, uploaded_doc):
    ids = [d["id"] for d in client.get("/documents").json()]
    assert uploaded_doc["id"] in ids


def test_document_detail_exposes_pages_and_image_urls(client, uploaded_doc):
    body = client.get(f"/documents/{uploaded_doc['id']}").json()
    pages = body["pages"]
    assert len(pages) == 2
    for page in pages:
        assert page["image_url"].startswith("/storage/")
        assert isinstance(page["page_number"], int)


def test_document_detail_unknown_id_404(client):
    assert client.get("/documents/does-not-exist").status_code == 404


# -------------------------------------------------------------------- query ---
def test_text_mode_answers_and_records_bbox_citation(client, uploaded_doc):
    resp = client.post(
        "/query",
        json={
            "question": "What was total revenue in 2023?",
            "document_id": uploaded_doc["id"],
            "mode": "text",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "text"
    assert body["abstained"] is False
    assert "42" in body["answer"]  # grounded in page 1

    citations = body["citations"]
    assert citations  # non-empty
    first = citations[0]
    assert isinstance(first["page_number"], int)
    assert first["image_url"].startswith("/storage/")
    # Text mode locates the chunk on the page image, so it records a bbox.
    assert isinstance(first["bbox"], list)
    assert len(first["bbox"]) == 4


def test_visual_mode_reads_employee_count(client, uploaded_doc):
    resp = client.post(
        "/query",
        json={
            "question": "How many employees in 2023?",
            "document_id": uploaded_doc["id"],
            "mode": "visual",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "visual"
    assert "1500" in body["answer"]
    assert body["citations"]


def test_guard_abstains_on_out_of_document_question(client, uploaded_doc):
    resp = client.post(
        "/query",
        json={
            "question": "What is the capital of France?",
            "document_id": uploaded_doc["id"],
            "mode": "text",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["abstained"] is True


def test_compare_mode_rejected_on_plain_query(client, uploaded_doc):
    # /query must refuse "compare"; the dedicated /query/compare endpoint owns it.
    resp = client.post(
        "/query",
        json={
            "question": "What was total revenue in 2023?",
            "document_id": uploaded_doc["id"],
            "mode": "compare",
        },
    )
    assert resp.status_code == 400


def test_query_compare_returns_both_answers(client, uploaded_doc):
    resp = client.post(
        "/query/compare",
        json={
            "question": "What was total revenue in 2023?",
            "document_id": uploaded_doc["id"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["question"] == "What was total revenue in 2023?"
    # Both the text-RAG and visual-RAG answers are present and well-formed.
    assert body["text"]["mode"] == "text"
    assert body["visual"]["mode"] == "visual"


# ------------------------------------------------------------------- delete ---
def test_delete_document_then_missing(client, sample_pdf):
    doc_id = client.post(
        "/documents", files={"file": ("gone.pdf", sample_pdf, "application/pdf")}
    ).json()["id"]

    assert client.delete(f"/documents/{doc_id}").status_code == 204
    assert client.get(f"/documents/{doc_id}").status_code == 404


# --------------------------------------------------------------------- eval ---
def test_eval_summary_shape(client):
    resp = client.get("/eval/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["num_questions"] > 0
    assert isinstance(body["metrics"], list)
    assert body["metrics"]  # committed summary has metrics
    metric = body["metrics"][0]
    assert {"label", "text", "visual"} <= set(metric)
    assert 0.0 <= body["guard_abstention_rate"] <= 1.0

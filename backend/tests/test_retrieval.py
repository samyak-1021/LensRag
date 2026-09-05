"""Unit tests for the numpy cosine top-k core of the vector index."""

from __future__ import annotations

import numpy as np

from app.services.retrieval import _cosine_top_k


def test_empty_matrix_returns_empty():
    idx, scores = _cosine_top_k([1.0, 0.0], np.zeros((0, 2), dtype=np.float32), k=5)
    assert idx == []
    assert scores == []


def test_ranks_by_dot_product_descending():
    # Row 1 is identical to the query (score 1), row 0 orthogonal, row 2 opposite.
    matrix = np.asarray(
        [[0.0, 1.0], [1.0, 0.0], [-1.0, 0.0]], dtype=np.float32
    )
    query = [1.0, 0.0]
    idx, scores = _cosine_top_k(query, matrix, k=3)

    assert idx[0] == 1  # best match ranked first
    assert scores[0] == 1.0
    # Scores are monotonically non-increasing.
    assert scores == sorted(scores, reverse=True)
    # Negative dot products are clamped up to 0.
    assert min(scores) >= 0.0


def test_k_larger_than_rows_is_clamped():
    matrix = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    idx, scores = _cosine_top_k([1.0, 0.0], matrix, k=10)
    assert len(idx) == 2
    assert len(scores) == 2


def test_scores_clamped_to_unit_interval():
    matrix = np.asarray([[2.0, 0.0]], dtype=np.float32)  # unnormalised -> dot > 1
    _, scores = _cosine_top_k([1.0, 0.0], matrix, k=1)
    assert scores[0] == 1.0  # clamped to the [0, 1] ceiling

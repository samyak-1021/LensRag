"""Unit tests for the tokenizer and the deterministic hash embedder."""

from __future__ import annotations

import numpy as np

from app.services.embeddings import HashEmbedder, get_embedder, tokenize


def _norm(vec: list[float]) -> float:
    return float(np.linalg.norm(np.asarray(vec, dtype=np.float32)))


def test_tokenize_lowercases_and_drops_stopwords():
    tokens = tokenize("The revenue OF Acme was 42")
    # Stop-words ("the", "of", "was") are removed; the rest are lowercased.
    assert "the" not in tokens
    assert "of" not in tokens
    assert "was" not in tokens
    assert tokens == ["revenue", "acme", "42"]


def test_tokenize_pure_stopwords_is_empty():
    assert tokenize("the of what when which") == []


def test_embedder_is_deterministic():
    emb = HashEmbedder(dim=384)
    a = emb.embed(["quarterly revenue growth"])[0]
    b = emb.embed(["quarterly revenue growth"])[0]
    assert a == b  # identical vectors on repeat runs (no randomness)


def test_embedding_dim_and_l2_normalisation():
    emb = HashEmbedder(dim=384)
    vec = emb.embed(["employees grew in 2023"])[0]
    assert len(vec) == 384
    # Non-empty content text -> unit vector (tolerance, since float32 norm is ~1.0).
    assert abs(_norm(vec) - 1.0) < 1e-5


def test_empty_and_stopword_only_text_give_zero_vectors():
    emb = HashEmbedder(dim=384)
    assert _norm(emb.embed([""])[0]) == 0.0
    # All-stopword text tokenises to nothing -> zero vector (guard-friendly).
    assert _norm(emb.embed(["the of what"])[0]) == 0.0


def test_get_embedder_returns_hash_embedder_by_default():
    emb = get_embedder()
    assert isinstance(emb, HashEmbedder)
    assert emb.dim == 384

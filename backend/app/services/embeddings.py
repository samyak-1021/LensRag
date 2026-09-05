"""Text embedders.

Two interchangeable implementations behind one interface:

* ``HashEmbedder`` — deterministic feature hashing, zero dependencies. Perfect for
  tests, CI and offline demos: no model download, identical vectors every run.
* ``BGEEmbedder`` — real BAAI/bge-small-en-v1.5 semantic embeddings (optional
  ``[bge]`` extra). Swap in with ``LENSRAG_EMBEDDINGS_BACKEND=bge``.

Both return L2-normalised vectors, so cosine similarity is a plain dot product.
"""

from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from typing import Protocol

import numpy as np

from app.config import get_settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# A small English stop-word list. Dropping these sharpens the dependency-free hash
# embeddings (unrelated queries no longer collide on "the"/"of"/…) and stops the
# mock answerer from matching on filler words — which in turn lets the
# hallucination guard correctly abstain on out-of-document questions offline.
# Real BGE embeddings don't need this, but it makes the zero-dependency path honest.
_STOPWORDS = frozenset(
    "a an and are as at be by for from has have in into is it its of on or that the "
    "to was were what when where which who why will with how do does this these those".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric content tokens (stop-words removed).

    Shared by the hash embedder and the mock LLM so both reason over the same
    content words.
    """
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    """Maps tokens + character trigrams into a fixed-dimension vector via the
    hashing trick, then L2-normalises. Deterministic and dependency-free."""

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def _bucket(self, token: str, seed: int = 0) -> tuple[int, float]:
        digest = hashlib.md5(f"{seed}:{token}".encode()).digest()
        index = int.from_bytes(digest[:4], "little") % self.dim
        sign = 1.0 if digest[4] & 1 else -1.0
        return index, sign

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vec = np.zeros(self.dim, dtype=np.float32)
            for tok in tokenize(text):
                idx, sign = self._bucket(tok)
                vec[idx] += sign
                # Character trigrams add sub-word robustness (typos, morphology).
                for i in range(len(tok) - 2):
                    gi, gs = self._bucket(tok[i : i + 3], seed=1)
                    vec[gi] += gs * 0.5
            norm = float(np.linalg.norm(vec))
            if norm > 0:
                vec /= norm
            vectors.append(vec.tolist())
        return vectors


class BGEEmbedder:
    """Real semantic embeddings. Imports sentence-transformers lazily so the base
    install stays lightweight."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        from sentence_transformers import SentenceTransformer  # optional heavy dep

        self._model = SentenceTransformer(model_name)
        self.dim = int(self._model.get_sentence_embedding_dimension())

    def embed(self, texts: list[str]) -> list[list[float]]:
        emb = self._model.encode(texts, normalize_embeddings=True)
        return [row.tolist() for row in emb]


@lru_cache
def get_embedder() -> Embedder:
    settings = get_settings()
    if settings.embeddings_backend == "bge":
        return BGEEmbedder()
    return HashEmbedder(dim=settings.embedding_dim)

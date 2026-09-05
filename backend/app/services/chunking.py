"""Split page text into overlapping word-windows for text-RAG retrieval.

Word count is used as a cheap, deterministic proxy for token count — good enough
for chunking and it keeps the base install free of a tokenizer dependency.
"""

from __future__ import annotations


def chunk_text(text: str, target: int = 120, overlap: int = 24) -> list[str]:
    """Return overlapping chunks of ~``target`` words with ``overlap`` shared words."""
    words = text.split()
    if not words:
        return []
    step = max(1, target - overlap)
    chunks: list[str] = []
    for start in range(0, len(words), step):
        window = words[start : start + target]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + target >= len(words):
            break  # last window already reached the end
    return chunks

"""Unit tests for the overlapping word-window chunker."""

from __future__ import annotations

from app.services.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_is_a_single_chunk():
    # Fewer than ``target`` words -> exactly one chunk holding all the words.
    text = "one two three four five"
    chunks = chunk_text(text, target=120, overlap=24)
    assert chunks == [text]


def test_long_text_splits_into_overlapping_windows():
    words = [f"w{i}" for i in range(300)]
    text = " ".join(words)
    chunks = chunk_text(text, target=120, overlap=24)

    # Multiple windows, each at most ``target`` words long.
    assert len(chunks) > 1
    assert all(len(c.split()) <= 120 for c in chunks)

    # Consecutive windows share exactly ``overlap`` words (step = target-overlap).
    first_words = chunks[0].split()
    second_words = chunks[1].split()
    assert first_words[-24:] == second_words[:24]

    # The final window reaches the last word of the input.
    assert chunks[-1].split()[-1] == "w299"


def test_no_duplicate_trailing_window():
    # When the text length is an exact multiple of the step, the loop must not
    # emit an empty or redundant final window.
    words = [f"w{i}" for i in range(96)]  # step = 120-24 = 96
    chunks = chunk_text(" ".join(words), target=120, overlap=24)
    assert len(chunks) == 1

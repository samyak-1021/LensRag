# Design notes

This document explains *why* LensRAG is built the way it is — the trade-offs, the
seams, and how each design choice is defended.

## The thesis

Retrieval-augmented generation over documents is now table stakes. The interesting,
unsolved part is **documents whose meaning lives in charts and tables**, where the
standard text-extraction pipeline throws away exactly the information you asked
about. LensRAG is organised around one measurable question:

> Does reading a page as an image actually beat reading its extracted text?

Everything is built to answer that honestly, including the parts that make the
answer *"not yet, offline"*.

## Retrieval: text vs visual

**Text-RAG (the baseline everyone ships).** Extract page text, split into
overlapping word-windows (`services/chunking.py`), embed each chunk, retrieve by
cosine similarity. Fast and good for prose — but a chart rendered as an image
contributes almost no text, so the answer often isn't in any chunk.

**Visual-RAG (the differentiator).** Retrieve whole **pages as images** with
**late-interaction** retrieval (ColPali / ColQwen2). Instead of squashing a page
into one dense vector, late interaction keeps *many* per-patch vectors and scores
them against the query tokens with MaxSim. That preserves chart and layout signal
that a single dense embedding — or OCR — discards. The VLM then reads values
directly off the retrieved page image.

> **Why late interaction over dense embeddings?** Per-patch matching keeps local,
> spatial signal (a bar's height, a table cell's position) that a single pooled
> vector averages away. That locality is the whole reason visual retrieval can beat
> text retrieval on chart pages.

## The provider abstraction (and why offline still matters)

Each heavy dependency sits behind a small interface with a deterministic fallback:

- **Embeddings** (`services/embeddings.py`): `HashEmbedder` (feature hashing, zero
  deps) or `BGEEmbedder` (real semantic). Both return L2-normalised vectors, so
  cosine is a dot product.
- **Generation** (`services/providers.py`): `MockProvider` (extractive, offline) or
  `GeminiProvider` (real multimodal via the Google AI Studio REST API — no heavy
  SDK, just `httpx`).
- **Visual retrieval** (`services/visual.py`): `MockVisualRetriever` (page-text
  proxy) or `ColPaliRetriever` (real, GPU).

This isn't just convenience. It means the API, the tests, and CI run **anywhere
with no keys, no GPU and no multi-gigabyte downloads**, while the frontier models
plug in with one environment variable. The honest cost: offline, the mock can't
read a chart, so the visual path shows no advantage — which the eval reports
plainly rather than hiding.

A small but important detail: the tokenizer removes stop-words, so the offline hash
embeddings and the mock answerer reason over content words. Without it, unrelated
questions collide on filler words like *"the"/"of"* and the guard fails to abstain.

## The vector store seam

At demo scale (tens of documents, a few thousand vectors) exact cosine search in
NumPy is simplest and fastest, and it runs identically on SQLite and Postgres
because embeddings are stored as portable JSON. `services/retrieval.py` is a
deliberately thin seam: swapping in a **pgvector** (or Qdrant) ANN index for
100k+ vectors means replacing two functions — the callers never change. The
`[postgres]` extra and a pgvector-ready Postgres image are already in place;
implementing that index behind the seam is the next step (below), not a rewrite.

## The hallucination guard

The most common failure of document QA is a confident, invented answer. The guard
(`services/guard.py`) abstains when **either** signal says grounding is weak:

1. the best retrieval score is below a threshold, or
2. the model itself reports "insufficient".

Confidence reported to the user is the **top retrieval score** — an honest,
grounding-based number rather than a fabricated one. Crucially, abstention is
**measured**: on unanswerable questions, abstaining is the correct answer, so the
eval scores it directly.

## Evaluation methodology

- **Synthetic corpus, known ground truth.** Reports are generated with charts and
  tables whose exact values we control, so numeric correctness is unambiguous — no
  fuzzy human labels, no leakage.
- **Recall@k** isolates retrieval quality (did the gold page get retrieved?) from
  generation quality.
- **Answer accuracy** matches numeric answers within a relative tolerance and text
  answers by normalised containment, bucketed into chart/table vs text-only.
- **Guard** is scored on a set of deliberately unanswerable questions.

Running offline validates the entire pipeline end-to-end and produces real
retrieval/guard numbers; the chart-reading accuracy gap requires a real VLM. Both
runs write the same `summary.json` the dashboard reads, so nothing is special-cased.

## Deployment

The zero-cost path is `docker compose up` (Postgres + API + dashboard) or the
`render.yaml` blueprint (free API + Postgres) with the frontend on Vercel. The
`infra/terraform/` module shows the same shape as reviewable IaC. Real generation
stays free by using Gemini's free tier.

## What I'd do next

- Implement the pgvector ANN path behind the existing retrieval seam and benchmark
  it against the in-process search.
- Precompute ColPali patch vectors at ingest (instead of at query time) and add a
  MaxSim index.
- Return the top-scoring patch region from ColPali as the visual citation bbox
  (today text citations carry a precise bbox; visual ones highlight the page).
- Add Ragas faithfulness scoring on the real-VLM run.

## Interview defense — quick answers

- **Why late interaction over dense embeddings?** Per-patch matching keeps
  chart/layout signal a pooled vector averages away.
- **How do you know it beats text RAG?** The eval's recall gap and chart-QA
  accuracy, on a corpus with known ground truth — rerun it and watch the numbers.
- **How do you stop it inventing chart values?** The guard abstains on weak
  grounding, and the eval measures abstention on unanswerable questions.
- **Why does offline show no gap?** The mock can't read an image; that's expected
  and stated. The abstraction exists so the gap is a config flip away, not a
  rewrite — and so CI never needs a GPU.

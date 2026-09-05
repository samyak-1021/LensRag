"""Generate the synthetic evaluation corpus: PDFs with charts/tables + a QA set.

Why synthetic? Two reasons that make the eval *stronger*, not weaker:

1. Ground truth is exact. Every chart bar and table cell comes from a number we
   choose here, so answer-correctness scoring is unambiguous.
2. The charts and tables are rendered as raster IMAGES, so their numbers live in
   pixels, not in the PDF text layer. A plain text extractor literally cannot see
   them — which is precisely the failure LensRAG exists to fix. The intro prose
   stays as real text, so text-RAG can still answer text questions (fair baseline).

Run:  python scripts/generate_corpus.py
Outputs:  data/corpus/*.pdf  and  data/eval/qa.jsonl
"""

from __future__ import annotations

import io
import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BACKEND_DIR / "data" / "corpus"
QA_PATH = BACKEND_DIR / "data" / "eval" / "qa.jsonl"
ACCENT = "#4f46e5"
A4 = (8.27, 11.69)


# --------------------------------------------------------------- rendering ---
def _fig_to_image(fig):
    """Rasterise a figure to an image array (its text becomes pixels)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return plt.imread(buf)


def _bar_image(spec):
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.bar(spec["labels"], spec["values"], color=ACCENT)
    ax.set_title(spec["title"], fontsize=12, weight="bold")
    ax.set_ylabel(spec["unit"])
    for i, v in enumerate(spec["values"]):
        ax.text(i, v, f"{v}", ha="center", va="bottom", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    return _fig_to_image(fig)


def _line_image(spec):
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.plot(spec["labels"], spec["values"], marker="o", color=ACCENT, linewidth=2)
    ax.set_title(spec["title"], fontsize=12, weight="bold")
    ax.set_ylabel(spec["unit"])
    for x, v in zip(spec["labels"], spec["values"], strict=True):
        ax.text(x, v, f"{v}", ha="center", va="bottom", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    return _fig_to_image(fig)


def _table_image(spec):
    fig, ax = plt.subplots(figsize=(6.6, 0.7 + 0.45 * len(spec["rows"])))
    ax.axis("off")
    ax.set_title(spec["title"], fontsize=12, weight="bold")
    tbl = ax.table(
        cellText=spec["rows"], colLabels=spec["cols"], loc="center", cellLoc="center"
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)
    return _fig_to_image(fig)


def _text_page(pdf, title, paragraphs):
    fig = plt.figure(figsize=A4)
    fig.text(0.1, 0.93, title, fontsize=19, weight="bold", va="top")
    body = "\n\n".join(textwrap.fill(p, 92) for p in paragraphs)
    fig.text(0.1, 0.85, body, fontsize=11.5, va="top", family="serif")
    pdf.savefig(fig)
    plt.close(fig)


def _image_page(pdf, title, image, caption):
    fig = plt.figure(figsize=A4)
    fig.text(0.1, 0.93, title, fontsize=19, weight="bold", va="top")
    ax = fig.add_axes([0.08, 0.30, 0.84, 0.56])
    ax.imshow(image)
    ax.axis("off")
    fig.text(0.1, 0.22, textwrap.fill(caption, 92), fontsize=11, va="top", family="serif")
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------- question generation ---
def _qid(slug: str, tag: str) -> str:
    return f"{slug}-{tag}"


def _series_questions(slug, spec, page, kind):
    """Point + extremum questions for a bar/line series (all require the image)."""
    qs = []
    labels, values, metric, unit = spec["labels"], spec["values"], spec["metric"], spec["unit"]
    for i, (label, value) in enumerate(zip(labels, values, strict=True)):
        qs.append(
            {
                "id": _qid(slug, f"{kind}p{i}"),
                "question": f"According to the chart, what was {metric} in {label}?",
                "answer": f"{value} {unit}",
                "answer_type": "numeric",
                "value": float(value),
                "gold_page": page,
                "requires_visual": True,
            }
        )
    hi = labels[values.index(max(values))]
    qs.append(
        {
            "id": _qid(slug, f"{kind}hi"),
            "question": f"Which period had the highest {metric}?",
            "answer": hi,
            "answer_type": "choice",
            "gold_page": page,
            "requires_visual": True,
        }
    )
    qs.append(
        {
            "id": _qid(slug, f"{kind}max"),
            "question": f"What was the highest {metric} recorded in the chart?",
            "answer": f"{max(values)} {unit}",
            "answer_type": "numeric",
            "value": float(max(values)),
            "gold_page": page,
            "requires_visual": True,
        }
    )
    return qs


def build_questions(slug, doc):
    questions = []
    # Intro facts (answerable from the real text layer -> fair for text-RAG).
    for i, fact in enumerate(doc["facts"]):
        questions.append(
            {
                "id": _qid(slug, f"t{i}"),
                "question": fact["q"],
                "answer": fact["a"],
                "answer_type": fact["type"],
                "value": fact.get("value"),
                "gold_page": 1,
                "requires_visual": False,
            }
        )
    questions += _series_questions(slug, doc["bar"], 2, "b")
    questions += _series_questions(slug, doc["line"], 3, "l")
    # Table questions (values only exist inside the rasterised table image).
    for i, tq in enumerate(doc["table"]["questions"]):
        questions.append(
            {
                "id": _qid(slug, f"tab{i}"),
                "question": tq["q"],
                "answer": tq["a"],
                "answer_type": tq["type"],
                "value": tq.get("value"),
                "gold_page": 4,
                "requires_visual": True,
            }
        )
    # Unanswerable questions -> the guard should abstain.
    for i, uq in enumerate(doc["unanswerable"]):
        questions.append(
            {
                "id": _qid(slug, f"u{i}"),
                "question": uq,
                "answer": "",
                "answer_type": "text",
                "value": None,
                "gold_page": None,
                "requires_visual": False,
                "unanswerable": True,
            }
        )
    # Fill defaults + stamp the source document.
    for q in questions:
        q.setdefault("requires_visual", False)
        q.setdefault("unanswerable", False)
        q.setdefault("value", None)
        q.setdefault("tolerance", 0.03)
        q["gold_doc"] = doc["file"]
    return questions


def build_pdf(doc):
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    path = CORPUS_DIR / doc["file"]
    with PdfPages(path) as pdf:
        _text_page(pdf, doc["title"], doc["paragraphs"])
        _image_page(pdf, doc["bar"]["title"], _bar_image(doc["bar"]), doc["bar"]["caption"])
        _image_page(pdf, doc["line"]["title"], _line_image(doc["line"]), doc["line"]["caption"])
        _image_page(
            pdf, doc["table"]["title"], _table_image(doc["table"]), doc["table"]["caption"]
        )
    return path


def main():
    from corpus_data import DOCS  # local module with the synthetic content

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    QA_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_questions = []
    for doc in DOCS:
        slug = doc["file"].replace(".pdf", "")
        build_pdf(doc)
        all_questions += build_questions(slug, doc)
    with QA_PATH.open("w") as fh:
        for q in all_questions:
            fh.write(json.dumps(q) + "\n")
    print(f"Wrote {len(DOCS)} PDFs to {CORPUS_DIR}")
    print(f"Wrote {len(all_questions)} questions to {QA_PATH}")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()

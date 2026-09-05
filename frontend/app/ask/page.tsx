"use client";

import { Search, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

import { ApiError, ask, askCompare, listDocuments } from "@/lib/api";
import type { Answer, Citation, CompareAnswer, DocumentOut, Mode } from "@/lib/types";
import AnswerCard from "@/components/AnswerCard";
import PageViewer from "@/components/PageViewer";
import { Button, Card, EmptyState, SegmentedControl, Spinner } from "@/components/ui";

const SAMPLES = [
  "According to the chart, what was quarterly revenue in Q1?",
  "How many employees does the company have?",
  "What was the gross margin for the year?",
  "Summarise the key highlights.",
];

const MODES: { value: Mode; label: string }[] = [
  { value: "visual", label: "Visual RAG" },
  { value: "text", label: "Text RAG" },
  { value: "compare", label: "Compare" },
];

export default function AskPage() {
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [docId, setDocId] = useState<string>("");
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<Mode>("visual");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [single, setSingle] = useState<Answer | null>(null);
  const [compare, setCompare] = useState<CompareAnswer | null>(null);
  const [active, setActive] = useState<Citation | null>(null);

  useEffect(() => {
    listDocuments()
      .then((d) => setDocs(d.filter((x) => x.status === "ready")))
      .catch(() => setDocs([]));
  }, []);

  async function submit() {
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    setSingle(null);
    setCompare(null);
    setActive(null);
    const document_id = docId || null;
    try {
      if (mode === "compare") {
        const res = await askCompare({ question, document_id });
        setCompare(res);
        setActive(res.visual.citations[0] ?? res.text.citations[0] ?? null);
      } else {
        const res = await ask({ question, document_id, mode });
        setSingle(res);
        setActive(res.citations[0] ?? null);
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Request failed. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  const provider =
    single?.provider ?? compare?.visual.provider ?? compare?.text.provider ?? null;
  const showMockHint = provider === "mock" && (single !== null || compare !== null);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Ask</h1>
        <p className="mt-1 text-sm text-ink-soft">
          Ask a question across your documents. Compare mode runs text-RAG and visual-RAG
          on the same question, side by side.
        </p>
      </div>

      {/* Query controls */}
      <Card className="space-y-4 p-5">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "Enter") submit();
          }}
          rows={2}
          placeholder="e.g. According to the chart, what was quarterly revenue in Q1?"
          className="w-full resize-none rounded-2xl border border-black/10 bg-surface px-4 py-3 text-[15px] outline-none placeholder:text-ink-soft/70 focus:border-accent"
        />

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
            className="rounded-2xl border border-black/10 bg-surface px-3 py-2 text-sm outline-none focus:border-accent"
          >
            <option value="">All documents ({docs.length})</option>
            {docs.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title || d.filename}
              </option>
            ))}
          </select>

          <SegmentedControl options={MODES} value={mode} onChange={setMode} />

          <Button className="ml-auto" onClick={submit} disabled={loading || !question.trim()}>
            {loading ? <Spinner /> : <Search size={16} />}
            {loading ? "Thinking…" : "Ask"}
          </Button>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {SAMPLES.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setQuestion(s)}
              className="rounded-full border border-black/10 bg-surface px-3 py-1 text-xs text-ink-soft transition hover:border-accent/40 hover:text-ink"
            >
              {s}
            </button>
          ))}
        </div>
      </Card>

      {error && <p className="text-sm text-bad">{error}</p>}

      {showMockHint && (
        <p className="rounded-2xl bg-warn/10 px-4 py-3 text-xs text-ink">
          Running on the offline <span className="font-medium">mock</span> generator, so
          both paths answer from extracted text. Enable Gemini
          (<code className="text-[11px]">LENSRAG_LLM_PROVIDER=gemini</code>) to see visual-RAG
          read values the text path can&rsquo;t.
        </p>
      )}

      {/* Results */}
      {!single && !compare && !loading && !error && (
        <EmptyState
          icon={<Sparkles size={26} />}
          title="Ask something to begin"
          description="Pick a sample question above, or upload your own document in the Library."
        />
      )}

      {single && (
        <div className="grid gap-4 lg:grid-cols-2">
          <AnswerCard
            title={single.mode === "text" ? "Text RAG" : "Visual RAG"}
            answer={single}
            activeCitation={active}
            onCitationClick={setActive}
          />
          <div>
            {active ? (
              <PageViewer
                src={active.image_url}
                bbox={active.bbox}
                caption={`${active.document_title} · page ${active.page_number}`}
              />
            ) : (
              <EmptyState title="No source page" description="This answer had no citations." />
            )}
          </div>
        </div>
      )}

      {compare && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <AnswerCard
              title="Text RAG"
              answer={compare.text}
              activeCitation={active}
              onCitationClick={setActive}
            />
            <AnswerCard
              title="Visual RAG"
              answer={compare.visual}
              activeCitation={active}
              onCitationClick={setActive}
            />
          </div>
          {active && (
            <div>
              <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-ink-soft">
                Evidence
              </h3>
              <div className="max-w-xl">
                <PageViewer
                  src={active.image_url}
                  bbox={active.bbox}
                  caption={`${active.document_title} · page ${active.page_number}`}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

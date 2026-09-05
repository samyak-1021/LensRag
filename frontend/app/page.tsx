"use client";

import { ArrowRight, BarChart3, ScanText, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { getEvalSummary, listDocuments } from "@/lib/api";
import type { DocumentOut, EvalSummary } from "@/lib/types";
import { percent } from "@/lib/format";
import { Button, Card, Stat } from "@/components/ui";

const FEATURES = [
  {
    icon: ScanText,
    title: "Reads charts & tables",
    body: "Pages are retrieved as images and answered by a vision model, so values locked inside a chart or table are actually read — not dropped like text-only RAG.",
  },
  {
    icon: BarChart3,
    title: "Proves it works",
    body: "A 110-question chart/table eval measures the recall gap between plain text-RAG and visual-RAG, plus per-type answer accuracy — the numbers, not vibes.",
  },
  {
    icon: ShieldCheck,
    title: "Shows its work",
    body: "Every answer highlights the exact page region it came from, and a hallucination guard abstains instead of inventing a number when grounding is weak.",
  },
];

export default function HomePage() {
  const [docs, setDocs] = useState<DocumentOut[] | null>(null);
  const [evalSummary, setEvalSummary] = useState<EvalSummary | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    listDocuments()
      .then(setDocs)
      .catch(() => setOffline(true));
    getEvalSummary()
      .then(setEvalSummary)
      .catch(() => setEvalSummary(null));
  }, []);

  return (
    <div className="space-y-10">
      {/* Hero */}
      <section className="animate-rise">
        <p className="text-sm font-medium text-accent">Multimodal RAG</p>
        <h1 className="mt-2 max-w-3xl text-4xl font-semibold leading-tight tracking-tight md:text-5xl">
          Answers from the whole page — charts included.
        </h1>
        <p className="mt-4 max-w-2xl text-lg leading-relaxed text-ink-soft">
          Most &ldquo;chat with your PDF&rdquo; tools only read the text, so they miss — or
          invent — the numbers locked inside charts and tables. LensRAG retrieves pages as
          images, reads them with a vision model, and shows you exactly where each answer
          came from.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/ask">
            <Button>
              Ask a question <ArrowRight size={16} />
            </Button>
          </Link>
          <Link href="/library">
            <Button variant="secondary">Manage documents</Button>
          </Link>
        </div>
      </section>

      {/* Quick stats */}
      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card className="p-5">
          <Stat
            label="Documents indexed"
            value={offline ? "—" : (docs?.length ?? "…")}
            hint={offline ? "API offline" : "in your library"}
          />
        </Card>
        <Card className="p-5">
          <Stat
            label="Eval questions"
            value={evalSummary?.num_questions ?? "…"}
            hint="chart / table / text"
          />
        </Card>
        <Card className="p-5">
          <Stat
            label="Guard abstention"
            value={evalSummary ? percent(evalSummary.guard_abstention_rate) : "…"}
            hint="on unanswerable Qs"
          />
        </Card>
        <Card className="p-5">
          <Stat
            label="Eval run"
            value={evalSummary ? (evalSummary.is_real_run ? "Real" : "Offline") : "…"}
            hint={evalSummary?.is_real_run ? "Gemini / ColPali" : "mock providers"}
          />
        </Card>
      </section>

      {/* Differentiators */}
      <section className="grid gap-4 md:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, body }) => (
          <Card key={title} className="p-6">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-soft text-accent">
              <Icon size={20} />
            </span>
            <h3 className="mt-4 text-base font-semibold">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-ink-soft">{body}</p>
          </Card>
        ))}
      </section>

      {offline && (
        <Card className="border-warn/30 bg-warn/5 p-5">
          <p className="text-sm text-ink">
            <span className="font-semibold">The API isn&rsquo;t reachable.</span> Start the
            backend with{" "}
            <code className="rounded bg-surface-muted px-1.5 py-0.5 text-xs">
              uvicorn app.main:app
            </code>{" "}
            (see the README), then refresh.
          </p>
        </Card>
      )}
    </div>
  );
}

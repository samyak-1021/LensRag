import {
  FileScan,
  Layers,
  MessagesSquare,
  ScanSearch,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { Card } from "@/components/ui";

const STEPS = [
  {
    icon: FileScan,
    title: "1 · Ingest",
    body: "Each PDF page is rendered to an image and text-extracted. Text is chunked and every chunk's location on the page is recorded for highlighting.",
  },
  {
    icon: ScanSearch,
    title: "2 · Retrieve",
    body: "Text-RAG finds relevant chunks by embedding similarity. Visual-RAG retrieves whole pages as images with late-interaction (ColPali) so chart/layout signal survives.",
  },
  {
    icon: MessagesSquare,
    title: "3 · Generate",
    body: "A vision-language model (Gemini) answers from the retrieved excerpts and page images — reading values straight off charts and tables.",
  },
  {
    icon: ShieldCheck,
    title: "4 · Guard & cite",
    body: "If grounding is weak the guard abstains instead of inventing a number. Otherwise the answer ships with the exact page region it came from.",
  },
];

const STACK = [
  ["Retrieval", "ColPali / ColQwen2 (visual) · BGE embeddings (text) · pgvector"],
  ["Generation", "Gemini (multimodal, free tier) — mock provider for offline dev"],
  ["Backend", "FastAPI · SQLAlchemy (async) · PyMuPDF · Pydantic v2"],
  ["Eval", "Custom chart/table-QA harness · recall@k + numeric/text matching"],
  ["Frontend", "Next.js (App Router) · TypeScript · Tailwind"],
  ["Infra", "Docker Compose · GitHub Actions CI · Terraform"],
];

export default function AboutPage() {
  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">How it works</h1>
        <p className="mt-1 max-w-2xl text-sm text-ink-soft">
          LensRAG is built around one honest question: does reading the page as an image
          actually beat reading the extracted text? Everything below exists to answer that
          measurably.
        </p>
      </div>

      <section className="grid gap-4 md:grid-cols-2">
        {STEPS.map(({ icon: Icon, title, body }) => (
          <Card key={title} className="p-6">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-soft text-accent">
              <Icon size={20} />
            </span>
            <h3 className="mt-4 text-base font-semibold">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-ink-soft">{body}</p>
          </Card>
        ))}
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold tracking-tight">
          <Layers size={18} className="text-accent" /> The stack
        </h2>
        <Card className="divide-y divide-black/5 p-2">
          {STACK.map(([label, value]) => (
            <div key={label} className="grid grid-cols-3 gap-4 px-4 py-3 text-sm">
              <span className="font-medium">{label}</span>
              <span className="col-span-2 text-ink-soft">{value}</span>
            </div>
          ))}
        </Card>
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold tracking-tight">
          <Sparkles size={18} className="text-accent" /> Why it&rsquo;s not a GPT wrapper
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="p-5">
            <h3 className="text-sm font-semibold">Late-interaction retrieval</h3>
            <p className="mt-2 text-sm leading-relaxed text-ink-soft">
              Per-patch matching keeps the chart and layout signal that OCR throws away —
              the reason visual retrieval can beat text retrieval on chart pages.
            </p>
          </Card>
          <Card className="p-5">
            <h3 className="text-sm font-semibold">Measured, not claimed</h3>
            <p className="mt-2 text-sm leading-relaxed text-ink-soft">
              The recall gap and chart-QA accuracy come from a real harness with known
              ground truth — you can rerun it and see the numbers move.
            </p>
          </Card>
          <Card className="p-5">
            <h3 className="text-sm font-semibold">Provably grounded</h3>
            <p className="mt-2 text-sm leading-relaxed text-ink-soft">
              Cited page regions and a hallucination guard mean answers point back to the
              document — something you can&rsquo;t reproduce by pasting into a chatbot.
            </p>
          </Card>
        </div>
      </section>
    </div>
  );
}

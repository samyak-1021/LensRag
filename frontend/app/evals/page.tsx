"use client";

import { useEffect, useState } from "react";

import { getEvalSummary } from "@/lib/api";
import type { EvalSummary } from "@/lib/types";
import { formatDate, percent } from "@/lib/format";
import MetricBar from "@/components/MetricBar";
import { Badge, Card, Spinner, Stat } from "@/components/ui";

export default function EvalsPage() {
  const [summary, setSummary] = useState<EvalSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getEvalSummary()
      .then(setSummary)
      .catch(() =>
        setError("No evaluation summary yet. Run `python -m app.eval.runner` in the backend."),
      );
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Evaluation</h1>
        <p className="mt-1 text-sm text-ink-soft">
          The part that separates a real system from a demo: a chart/table-QA harness that
          measures whether reading the page image actually beats plain text-RAG.
        </p>
      </div>

      {error && <p className="text-sm text-bad">{error}</p>}

      {!summary && !error && (
        <div className="flex justify-center py-16 text-ink-soft">
          <Spinner />
        </div>
      )}

      {summary && (
        <>
          <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <Card className="p-5">
              <Stat label="Questions" value={summary.num_questions} hint="chart / table / text" />
            </Card>
            <Card className="p-5">
              <Stat
                label="Guard abstention"
                value={percent(summary.guard_abstention_rate)}
                hint="correct on unanswerable"
              />
            </Card>
            <Card className="p-5">
              <Stat
                label="Run type"
                value={summary.is_real_run ? "Real" : "Offline"}
                hint={summary.is_real_run ? "Gemini / ColPali" : "mock providers"}
              />
            </Card>
            <Card className="p-5">
              <Stat label="Generated" value={formatDate(summary.generated_at)} />
            </Card>
          </section>

          <Card className="p-6">
            <div className="mb-2 flex items-center gap-2">
              <h2 className="text-base font-semibold">Text-RAG vs Visual-RAG</h2>
              <Badge tone={summary.is_real_run ? "ok" : "warn"}>
                {summary.is_real_run ? "real run" : "offline run"}
              </Badge>
            </div>
            <div className="divide-y divide-white/10">
              {summary.metrics.map((m) => (
                <MetricBar key={m.label} metric={m} />
              ))}
            </div>
          </Card>

          <Card className="border-accent/20 bg-accent-soft/40 p-5">
            <p className="text-sm leading-relaxed text-ink">
              <span className="font-semibold">What this means. </span>
              {summary.notes}
            </p>
          </Card>

          <Card className="p-6">
            <h2 className="text-base font-semibold">How the eval works</h2>
            <ul className="mt-3 space-y-2 text-sm leading-relaxed text-ink-soft">
              <li>
                <span className="font-medium text-ink">Synthetic corpus, known ground truth.</span>{" "}
                Reports are generated with charts/tables whose exact values we control, so
                &ldquo;did it read the chart right?&rdquo; is scored precisely — no fuzzy labels.
              </li>
              <li>
                <span className="font-medium text-ink">Recall@k.</span> Did the gold page appear
                in the retrieved citations? This isolates retrieval quality from generation.
              </li>
              <li>
                <span className="font-medium text-ink">Answer accuracy.</span> Numeric answers
                match within a tolerance; text answers by normalised containment.
              </li>
              <li>
                <span className="font-medium text-ink">Guard, measured.</span> On unanswerable
                questions the only correct move is to abstain — so abstention is scored, not
                hand-waved.
              </li>
            </ul>
          </Card>
        </>
      )}
    </div>
  );
}

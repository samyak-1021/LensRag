"use client";

// Presents one Answer: the text, an honest confidence bar, the abstain state, and
// clickable page citations. Used on its own (single mode) and twice side-by-side
// (compare mode).

import { ShieldAlert } from "lucide-react";

import type { Answer, Citation } from "@/lib/types";
import { confidenceTone, percent } from "@/lib/format";
import { Badge, Card, cn } from "./ui";

export default function AnswerCard({
  title,
  answer,
  activeCitation,
  onCitationClick,
}: {
  title: string;
  answer: Answer;
  activeCitation?: Citation | null;
  onCitationClick?: (c: Citation) => void;
}) {
  const tone = confidenceTone(answer.confidence);

  return (
    <Card className="flex flex-col gap-4 p-5 animate-rise">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-ink-soft">
            {title}
          </h3>
          {answer.abstained && (
            <Badge tone="warn">
              <ShieldAlert size={12} /> guard abstained
            </Badge>
          )}
        </div>
        <span className="text-xs text-ink-soft">
          {answer.provider} · {answer.latency_ms} ms
        </span>
      </div>

      <p
        className={cn(
          "text-[15px] leading-relaxed",
          answer.abstained ? "italic text-ink-soft" : "text-ink",
        )}
      >
        {answer.answer}
      </p>

      <div>
        <div className="mb-1 flex items-center justify-between text-xs">
          <span className="text-ink-soft">Confidence (top retrieval score)</span>
          <span className={cn("font-medium", tone.className)}>
            {tone.label} · {percent(answer.confidence)}
          </span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-muted">
          <div
            className="h-full rounded-full bg-accent transition-all"
            style={{ width: `${Math.round(answer.confidence * 100)}%` }}
          />
        </div>
      </div>

      {answer.citations.length > 0 && (
        <div>
          <div className="mb-2 text-xs text-ink-soft">
            Sources ({answer.citations.length})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {answer.citations.map((c, i) => {
              const active =
                activeCitation?.document_id === c.document_id &&
                activeCitation?.page_number === c.page_number;
              return (
                <button
                  key={`${c.document_id}-${c.page_number}-${i}`}
                  type="button"
                  onClick={() => onCitationClick?.(c)}
                  title={c.snippet}
                  className={cn(
                    "rounded-full border px-2.5 py-1 text-xs font-medium transition",
                    active
                      ? "border-accent bg-accent-soft text-accent"
                      : "border-white/10 bg-surface text-ink-soft hover:text-ink",
                  )}
                >
                  p.{c.page_number} · {percent(c.score)}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </Card>
  );
}

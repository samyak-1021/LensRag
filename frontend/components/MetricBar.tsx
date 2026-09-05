"use client";

// One eval metric rendered as two bars (text-RAG vs visual-RAG) plus the gap —
// the visual of "how much does reading the page image help?".

import type { EvalMetric } from "@/lib/types";
import { percent } from "@/lib/format";
import { cn } from "./ui";

export default function MetricBar({ metric }: { metric: EvalMetric }) {
  const gap = metric.visual - metric.text;
  const rows = [
    { label: "Text RAG", value: metric.text, color: "bg-ink-soft" },
    { label: "Visual RAG", value: metric.visual, color: "bg-accent" },
  ];

  return (
    <div className="py-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-medium">{metric.label}</span>
        {Math.abs(gap) >= 0.005 && (
          <span
            className={cn(
              "text-xs font-semibold",
              gap > 0 ? "text-ok" : "text-bad",
            )}
          >
            {gap > 0 ? "+" : ""}
            {percent(gap)} {gap > 0 ? "visual" : "text"}
          </span>
        )}
      </div>
      <div className="space-y-1.5">
        {rows.map((r) => (
          <div key={r.label} className="flex items-center gap-3">
            <span className="w-20 shrink-0 text-xs text-ink-soft">{r.label}</span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-muted">
              <div
                className={cn("h-full rounded-full transition-all", r.color)}
                style={{ width: `${Math.max(2, Math.round(r.value * 100))}%` }}
              />
            </div>
            <span className="w-10 shrink-0 text-right text-xs font-medium tabular-nums">
              {percent(r.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

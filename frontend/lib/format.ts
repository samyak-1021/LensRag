// Small formatting helpers shared across the UI.

export function formatBytes(bytes: number): string {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.min(units.length - 1, Math.floor(Math.log(bytes) / Math.log(1024)));
  return `${(bytes / 1024 ** i).toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function percent(value: number, digits = 0): string {
  return `${(value * 100).toFixed(digits)}%`;
}

/** Clamp a 0..1 confidence to a label + colour token for the confidence bar. */
export function confidenceTone(score: number): { label: string; className: string } {
  if (score >= 0.6) return { label: "High", className: "text-ok" };
  if (score >= 0.35) return { label: "Medium", className: "text-warn" };
  return { label: "Low", className: "text-bad" };
}

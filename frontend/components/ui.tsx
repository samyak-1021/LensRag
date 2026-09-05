"use client";

// Small, reusable Apple-flavoured UI primitives shared across pages.

import type { ButtonHTMLAttributes, ReactNode } from "react";

export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}

export function Card({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={cn(
        "rounded-3xl bg-surface border border-black/5 shadow-card",
        className,
      )}
    >
      {children}
    </div>
  );
}

type Variant = "primary" | "secondary" | "ghost" | "danger";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-accent text-white hover:bg-accent-hover shadow-soft",
  secondary: "bg-surface-muted text-ink hover:bg-black/5 border border-black/5",
  ghost: "text-ink-soft hover:text-ink hover:bg-black/5",
  danger: "bg-bad/10 text-bad hover:bg-bad/15",
};

export function Button({
  variant = "primary",
  className,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-2 text-sm",
        "font-medium transition disabled:opacity-40 disabled:pointer-events-none",
        VARIANTS[variant],
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}

type Tone = "neutral" | "accent" | "ok" | "warn" | "bad";

const TONES: Record<Tone, string> = {
  neutral: "bg-surface-muted text-ink-soft",
  accent: "bg-accent-soft text-accent",
  ok: "bg-ok/12 text-ok",
  warn: "bg-warn/15 text-warn",
  bad: "bg-bad/12 text-bad",
};

export function Badge({
  tone = "neutral",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent",
        className,
      )}
      aria-label="Loading"
    />
  );
}

export function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
}) {
  return (
    <div>
      <div className="text-sm text-ink-soft">{label}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
      {hint && <div className="mt-0.5 text-xs text-ink-soft">{hint}</div>}
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-black/10 bg-surface/60 px-6 py-16 text-center">
      {icon && <div className="mb-3 text-ink-soft">{icon}</div>}
      <div className="text-base font-medium">{title}</div>
      {description && (
        <div className="mt-1 max-w-sm text-sm text-ink-soft">{description}</div>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (value: T) => void;
}) {
  return (
    <div className="inline-flex rounded-2xl border border-black/5 bg-surface-muted p-1">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={cn(
            "rounded-xl px-4 py-1.5 text-sm font-medium transition",
            value === o.value
              ? "bg-surface text-ink shadow-soft"
              : "text-ink-soft hover:text-ink",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

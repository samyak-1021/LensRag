"use client";

import { BarChart3, FileText, Home, Info, ScanText, Sparkles } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import ModeBadge from "./ModeBadge";
import { cn } from "./ui";

const NAV = [
  { href: "/", label: "Overview", icon: Home },
  { href: "/library", label: "Library", icon: FileText },
  { href: "/ask", label: "Ask", icon: ScanText },
  { href: "/evals", label: "Evaluation", icon: BarChart3 },
  { href: "/about", label: "How it works", icon: Info },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-white/10 bg-surface/70 px-4 py-6 backdrop-blur">
      <Link href="/" className="mb-8 flex items-center gap-2 px-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-accent text-white shadow-soft">
          <Sparkles size={18} />
        </span>
        <span className="text-lg font-semibold tracking-tight">LensRAG</span>
      </Link>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-3 py-2 text-sm font-medium transition",
                active
                  ? "bg-accent-soft text-accent"
                  : "text-ink-soft hover:bg-white/10 hover:text-ink",
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-6 px-1">
        <ModeBadge />
        <p className="mt-3 px-1 text-xs leading-relaxed text-ink-soft">
          Reads charts &amp; tables in documents — not just the text.
        </p>
      </div>
    </aside>
  );
}

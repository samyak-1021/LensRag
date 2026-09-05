"use client";

import { FileText, Trash2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { assetUrl } from "@/lib/api";
import type { DocumentOut } from "@/lib/types";
import { formatBytes, formatDate } from "@/lib/format";
import { Badge, Button, Card } from "./ui";

const STATUS_TONE = {
  ready: "ok",
  processing: "warn",
  failed: "bad",
} as const;

export default function DocumentCard({
  doc,
  onDelete,
}: {
  doc: DocumentOut;
  onDelete?: (id: string) => void;
}) {
  const [thumbBroken, setThumbBroken] = useState(false);
  const tone = STATUS_TONE[doc.status as keyof typeof STATUS_TONE] ?? "neutral";

  return (
    <Card className="group overflow-hidden">
      <Link href={`/library/${doc.id}`} className="block">
        <div className="flex h-40 items-center justify-center overflow-hidden border-b border-white/10 bg-surface-muted">
          {doc.status === "ready" && !thumbBroken ? (
            // Page 1 thumbnail, served directly from the backend storage mount.
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={assetUrl(`/storage/${doc.id}/page-1.png`)}
              alt={doc.title}
              className="h-full w-full object-cover object-top transition group-hover:scale-[1.02]"
              onError={() => setThumbBroken(true)}
            />
          ) : (
            <FileText className="text-ink-soft" size={32} />
          )}
        </div>
      </Link>

      <div className="p-4">
        <div className="flex items-start justify-between gap-2">
          <Link href={`/library/${doc.id}`} className="min-w-0">
            <h3 className="truncate text-sm font-semibold" title={doc.title}>
              {doc.title || doc.filename}
            </h3>
            <p className="mt-0.5 truncate text-xs text-ink-soft" title={doc.filename}>
              {doc.filename}
            </p>
          </Link>
          <Badge tone={tone}>{doc.status}</Badge>
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-ink-soft">
          <span>
            {doc.num_pages} page{doc.num_pages === 1 ? "" : "s"} · {formatBytes(doc.size_bytes)}
          </span>
          <span>{formatDate(doc.created_at)}</span>
        </div>

        {onDelete && (
          <div className="mt-3 flex justify-end">
            <Button
              variant="danger"
              className="px-2.5 py-1 text-xs"
              onClick={() => onDelete(doc.id)}
            >
              <Trash2 size={13} /> Delete
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}

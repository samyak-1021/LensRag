"use client";

import { ArrowLeft, X } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { assetUrl, getDocument } from "@/lib/api";
import type { DocumentDetail, PageOut } from "@/lib/types";
import { formatBytes, formatDate } from "@/lib/format";
import { Badge, Card, Spinner } from "@/components/ui";

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState<PageOut | null>(null);

  useEffect(() => {
    if (!params.id) return;
    getDocument(params.id)
      .then(setDoc)
      .catch(() => setError("Document not found."));
  }, [params.id]);

  if (error) {
    return (
      <div className="space-y-4">
        <Link href="/library" className="inline-flex items-center gap-1 text-sm text-accent">
          <ArrowLeft size={15} /> Back to library
        </Link>
        <p className="text-sm text-bad">{error}</p>
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="flex justify-center py-16 text-ink-soft">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <Link
          href="/library"
          className="inline-flex items-center gap-1 text-sm text-accent hover:underline"
        >
          <ArrowLeft size={15} /> Library
        </Link>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">
            {doc.title || doc.filename}
          </h1>
          <Badge tone={doc.status === "ready" ? "ok" : "warn"}>{doc.status}</Badge>
        </div>
        <p className="mt-1 text-sm text-ink-soft">
          {doc.filename} · {doc.num_pages} pages · {formatBytes(doc.size_bytes)} ·{" "}
          {formatDate(doc.created_at)}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {doc.pages.map((p) => (
          <button
            key={p.page_number}
            type="button"
            onClick={() => setZoom(p)}
            className="group text-left"
          >
            <Card className="overflow-hidden transition group-hover:shadow-soft">
              <div className="relative aspect-[3/4] overflow-hidden bg-surface-muted">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={assetUrl(p.image_url)}
                  alt={`Page ${p.page_number}`}
                  className="h-full w-full object-cover object-top"
                />
              </div>
              <div className="flex items-center justify-between px-3 py-2 text-xs text-ink-soft">
                <span>Page {p.page_number}</span>
                {p.has_text ? <span>text</span> : <span className="text-warn">image-only</span>}
              </div>
            </Card>
          </button>
        ))}
      </div>

      {/* Lightbox */}
      {zoom && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-6 backdrop-blur-sm"
          onClick={() => setZoom(null)}
        >
          <div className="relative max-h-[90vh] max-w-3xl overflow-auto rounded-2xl bg-surface">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={assetUrl(zoom.image_url)}
              alt={`Page ${zoom.page_number}`}
              className="w-full"
              onClick={(e) => e.stopPropagation()}
            />
            <button
              type="button"
              onClick={() => setZoom(null)}
              className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-black/50 text-white"
              aria-label="Close"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import { ApiError, uploadDocument } from "@/lib/api";
import { cn, Spinner } from "./ui";

export default function UploadDropzone({
  onUploaded,
}: {
  onUploaded?: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    setError(null);
    setBusy(true);
    try {
      // Upload sequentially so ingestion (render + embed) stays predictable.
      for (const file of Array.from(files)) {
        await uploadDocument(file);
      }
      onUploaded?.();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Upload failed. Is the API running?");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => !busy && inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed px-6 py-12 text-center transition",
          dragging
            ? "border-accent bg-accent-soft"
            : "border-white/10 bg-surface hover:border-accent/50",
        )}
      >
        {busy ? (
          <Spinner className="text-accent" />
        ) : (
          <UploadCloud className="text-accent" size={28} />
        )}
        <div className="mt-3 text-sm font-medium">
          {busy ? "Ingesting…" : "Drop a PDF here, or click to choose"}
        </div>
        <div className="mt-1 text-xs text-ink-soft">
          Each page is rendered to an image and indexed for text &amp; visual search.
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>
      {error && <p className="mt-2 text-sm text-bad">{error}</p>}
    </div>
  );
}

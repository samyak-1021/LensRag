"use client";

import { FileText } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { deleteDocument, listDocuments } from "@/lib/api";
import type { DocumentOut } from "@/lib/types";
import DocumentCard from "@/components/DocumentCard";
import UploadDropzone from "@/components/UploadDropzone";
import { EmptyState, Spinner } from "@/components/ui";

export default function LibraryPage() {
  const [docs, setDocs] = useState<DocumentOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    listDocuments()
      .then((d) => {
        setDocs(d);
        setError(null);
      })
      .catch(() => setError("Couldn't reach the API. Is the backend running?"));
  }, []);

  useEffect(refresh, [refresh]);

  async function handleDelete(id: string) {
    // Optimistic removal, then re-sync with the server.
    setDocs((prev) => prev?.filter((d) => d.id !== id) ?? null);
    try {
      await deleteDocument(id);
    } finally {
      refresh();
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Library</h1>
        <p className="mt-1 text-sm text-ink-soft">
          Upload PDFs (annual reports, datasheets, papers). Each page is rendered to an
          image and indexed for both text and visual retrieval.
        </p>
      </div>

      <UploadDropzone onUploaded={refresh} />

      {error ? (
        <p className="text-sm text-bad">{error}</p>
      ) : docs === null ? (
        <div className="flex justify-center py-16 text-ink-soft">
          <Spinner />
        </div>
      ) : docs.length === 0 ? (
        <EmptyState
          icon={<FileText size={28} />}
          title="No documents yet"
          description="Drop a PDF above to get started. The repo ships sample reports in backend/data/corpus — try one with charts."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {docs.map((doc) => (
            <DocumentCard key={doc.id} doc={doc} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}

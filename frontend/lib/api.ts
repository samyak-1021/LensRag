// Thin, typed client for the LensRAG backend. Every call is a plain fetch so the
// app has no data-fetching dependency and `next build` never needs a live API.

import type {
  Answer,
  CompareAnswer,
  DocumentDetail,
  DocumentOut,
  EvalSummary,
  HealthConfig,
  QueryRequest,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

/** Prefix a backend-relative asset path (e.g. a /storage image) with the API host. */
export function assetUrl(path: string): string {
  if (!path) return "";
  return path.startsWith("http") ? path : `${API_BASE}${path}`;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function unwrap<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      /* non-JSON error body — keep statusText */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

// -------------------------------------------------------------- Documents ---
export function listDocuments(): Promise<DocumentOut[]> {
  return fetch(`${API_BASE}/documents`, { cache: "no-store" }).then(unwrap<DocumentOut[]>);
}

export function getDocument(id: string): Promise<DocumentDetail> {
  return fetch(`${API_BASE}/documents/${id}`, { cache: "no-store" }).then(unwrap<DocumentDetail>);
}

export function uploadDocument(file: File): Promise<DocumentOut> {
  const form = new FormData();
  form.append("file", file);
  return fetch(`${API_BASE}/documents`, { method: "POST", body: form }).then(unwrap<DocumentOut>);
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new ApiError(res.status, "Failed to delete document");
}

// ------------------------------------------------------------------ Query ---
export function ask(req: QueryRequest): Promise<Answer> {
  return fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  }).then(unwrap<Answer>);
}

export function askCompare(req: Omit<QueryRequest, "mode">): Promise<CompareAnswer> {
  return fetch(`${API_BASE}/query/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...req, mode: "compare" }),
  }).then(unwrap<CompareAnswer>);
}

// ------------------------------------------------------------- Eval / meta ---
export function getEvalSummary(): Promise<EvalSummary> {
  return fetch(`${API_BASE}/eval/summary`, { cache: "no-store" }).then(unwrap<EvalSummary>);
}

export function getHealthConfig(): Promise<HealthConfig> {
  return fetch(`${API_BASE}/health/config`, { cache: "no-store" }).then(unwrap<HealthConfig>);
}

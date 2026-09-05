// TypeScript mirror of the backend Pydantic schemas (app/schemas.py).
// Keeping these in sync is the API contract between frontend and backend.

export type Mode = "text" | "visual" | "compare";

export interface DocumentOut {
  id: string;
  filename: string;
  title: string;
  num_pages: number;
  size_bytes: number;
  status: string; // "processing" | "ready" | "failed"
  error?: string | null;
  created_at: string;
}

export interface PageOut {
  page_number: number;
  image_url: string; // "/storage/<doc>/page-N.png"
  width: number;
  height: number;
  has_text: boolean;
}

export interface DocumentDetail extends DocumentOut {
  pages: PageOut[];
}

export interface Citation {
  document_id: string;
  document_title: string;
  page_number: number;
  image_url: string;
  score: number;
  snippet: string;
  bbox: number[] | null; // normalised [x0, y0, x1, y1] in 0..1
}

export interface Answer {
  mode: Mode;
  answer: string;
  confidence: number;
  abstained: boolean;
  citations: Citation[];
  latency_ms: number;
  provider: string;
}

export interface CompareAnswer {
  question: string;
  text: Answer;
  visual: Answer;
}

export interface EvalMetric {
  label: string;
  text: number;
  visual: number;
}

export interface EvalSummary {
  generated_at: string | null;
  is_real_run: boolean;
  num_questions: number;
  metrics: EvalMetric[];
  guard_abstention_rate: number;
  notes: string;
}

export interface HealthConfig {
  llm_provider: string;
  visual_backend: string;
  embeddings_backend: string;
  vector_backend: string;
  is_real_generation: boolean;
  model: string;
}

export interface QueryRequest {
  question: string;
  document_id?: string | null;
  mode: Mode;
  top_k?: number | null;
}

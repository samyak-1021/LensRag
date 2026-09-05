import type { Metadata } from "next";
import type { ReactNode } from "react";

import Sidebar from "@/components/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "LensRAG — RAG that reads charts",
  description:
    "Multimodal retrieval-augmented generation that reads charts and tables in documents — with page-level citations, a hallucination guard, and an evaluation harness.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="min-w-0 flex-1">
            <div className="mx-auto max-w-content px-6 py-10 md:px-10">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}

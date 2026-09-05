"use client";

// Renders a page image with an optional highlighted region — the "show your work"
// view. The region is a normalised [x0, y0, x1, y1] box (0..1) drawn as a % overlay,
// so it scales with the responsive image.

import { assetUrl } from "@/lib/api";

export default function PageViewer({
  src,
  bbox,
  caption,
}: {
  src: string;
  bbox?: number[] | null;
  caption?: string;
}) {
  const box =
    bbox && bbox.length === 4
      ? {
          left: `${bbox[0] * 100}%`,
          top: `${bbox[1] * 100}%`,
          width: `${(bbox[2] - bbox[0]) * 100}%`,
          height: `${(bbox[3] - bbox[1]) * 100}%`,
        }
      : null;

  return (
    <figure className="overflow-hidden rounded-2xl border border-black/5 bg-surface-muted">
      <div className="relative">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={assetUrl(src)} alt={caption ?? "Document page"} className="block w-full" />
        {box && (
          <div
            className="pointer-events-none absolute rounded-md bg-accent/10 ring-2 ring-accent transition-all"
            style={box}
          />
        )}
      </div>
      {caption && (
        <figcaption className="border-t border-black/5 px-3 py-2 text-xs text-ink-soft">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}

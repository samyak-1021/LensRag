"use client";

// Shows whether generation is running on the real Gemini VLM or the offline mock,
// straight from the backend's /health/config — so the UI is always honest.

import { useEffect, useState } from "react";

import { getHealthConfig } from "@/lib/api";
import type { HealthConfig } from "@/lib/types";
import { Badge } from "./ui";

export default function ModeBadge() {
  const [config, setConfig] = useState<HealthConfig | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    getHealthConfig()
      .then(setConfig)
      .catch(() => setOffline(true));
  }, []);

  if (offline) {
    return <Badge tone="bad">API offline</Badge>;
  }
  if (!config) {
    return <Badge tone="neutral">Checking…</Badge>;
  }
  return (
    <div className="flex flex-wrap gap-1.5">
      <Badge tone={config.is_real_generation ? "ok" : "warn"}>
        {config.is_real_generation ? `Gemini · ${config.model}` : "Mock (offline)"}
      </Badge>
      <Badge tone={config.visual_backend === "colpali" ? "ok" : "neutral"}>
        {config.visual_backend === "colpali" ? "ColPali" : "visual: proxy"}
      </Badge>
    </div>
  );
}

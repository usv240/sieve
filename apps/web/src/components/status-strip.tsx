"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";

type Health = { ok: boolean; mode: string; token_factory: boolean; vision_endpoint: boolean; tavily: boolean; index?: { docs: number; pages: number } };

/** Honest about what is live right now: which backends are up and whether the demo is a live call or a replay. */
export function StatusStrip() {
  const [h, setH] = useState<Health | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => {
    fetch(apiUrl("/health")).then((r) => r.json()).then(setH).catch(() => setErr(true));
  }, []);
  const dot = (on: boolean) => <span aria-hidden className={`inline-block h-2 w-2 rounded-full ${on ? "bg-ok" : "bg-caution"}`} />;
  return (
    <div className="border-t border-border bg-bg-elev/60 text-xs text-fg-muted">
      <div className="mx-auto flex max-w-[1100px] flex-wrap items-center gap-x-4 gap-y-1 px-4 py-1.5 sm:px-6">
        {err && <span>API offline: showing replay samples only</span>}
        {h && (
          <>
            <span className="flex items-center gap-1.5">{dot(h.token_factory)} Token Factory {h.token_factory ? "live" : "no key, replay"}</span>
            <span className="flex items-center gap-1.5">{dot(h.vision_endpoint)} Vision {h.vision_endpoint ? "Nemotron VL endpoint" : "fallback"}</span>
            <span className="flex items-center gap-1.5">{dot(h.tavily)} Tavily {h.tavily ? "on" : "off"}</span>
            {h.index && <span>{h.index.docs} manuals, {h.index.pages.toLocaleString()} pages indexed</span>}
          </>
        )}
      </div>
    </div>
  );
}

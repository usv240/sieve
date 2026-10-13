"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";

type Evals = { status?: string; generated_at?: string; summary?: Record<string, { value: number | string | null; unit?: string; label: string; note?: string }> };

/** Pulls eval/results/latest.json through the API so the landing page never shows a number we did not measure. */
export function EvalTiles() {
  const [e, setE] = useState<Evals | null>(null);
  useEffect(() => {
    fetch(apiUrl("/v1/evals/latest")).then((r) => r.json()).then(setE).catch(() => setE({ status: "unreachable" }));
  }, []);
  if (!e) return <p className="text-fg-muted">Loading evaluation results…</p>;
  if (!e.summary) return <p className="card text-fg-muted">No evaluation run has been published yet. Run <code>make eval</code> to produce one. Status: {e.status}</p>;
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Object.entries(e.summary).map(([k, v]) => (
        <div key={k} className="card">
          <p className="text-3xl font-semibold tracking-tight">{v.value === null ? "n/a" : v.value}{v.unit ?? ""}</p>
          <p className="mt-1 text-sm font-medium">{v.label}</p>
          {v.note && <p className="mt-1 text-xs text-fg-muted">{v.note}</p>}
        </div>
      ))}
      {e.generated_at && <p className="col-span-full text-xs text-fg-muted">Last run: {new Date(e.generated_at).toLocaleString()}</p>}
    </div>
  );
}

"use client";

import { useState } from "react";
import { apiUrl } from "@/lib/api";
import { Info } from "@/components/info";

type Cite = { doc: string; page: number; quote: string };
type Step = { id: number; action: string; expected: string; safety_class: "none" | "caution" | "stop"; cite: Cite; support?: string };
type Out = { device_label: string; blocked: boolean; tree: { summary: string; steps: Step[] } | null; citations: { total?: number; verified?: number };
  rule_hits: { message: string; action: string }[]; audit: { overall: string } | null; trace: { model: string; usd: number }[]; latency_ms: number; detail?: string };

/** Bring your own manual, then see the output: a cited repair plan written from the uploaded document alone. */
export function AskUploaded({ docId, title }: { docId: string; title: string }) {
  const [q, setQ] = useState("Unit runs but the low oxygen alarm comes on after a few minutes");
  const [busy, setBusy] = useState(false);
  const [out, setOut] = useState<Out | null>(null);
  async function ask() {
    setBusy(true); setOut(null);
    try {
      const r = await fetch(apiUrl("/v1/analyze"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ device_id: null, doc_id: docId, free_text: q, audit: true }) });
      setOut(await r.json());
    } catch { setOut({ detail: "The request failed. Try again." } as Out); } finally { setBusy(false); }
  }
  const usd = out?.trace?.reduce((a, t) => a + (t.usd || 0), 0) ?? 0;
  return (
    <div className="space-y-3 rounded-[16px] border border-accent p-4">
      <p className="font-semibold">Ask your manual <Info term="Ask your manual" text="Sieve answers from the document you uploaded and nothing else. Every step points at a sentence on one of its pages, the same safety rules apply, and Nemotron 3 Ultra audits the plan against your whole manual." /></p>
      <p className="text-sm text-fg-muted">Describe the fault. The plan comes only from {title}.</p>
      <textarea className="inp min-h-20" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Describe the fault" />
      <button className="btn-primary" onClick={ask} disabled={busy || !q.trim()}>{busy ? "Reading your manual…" : "Build the fix from my manual"}</button>
      {busy && <p className="text-sm text-fg-muted" role="status">Nemotron 3 Super writes the plan, then Nemotron 3 Ultra audits it against your whole document. Usually under a minute.</p>}
      {out?.detail && <p role="alert" className="text-sm text-stop">{out.detail}</p>}
      {out?.blocked && <p role="alert" className="text-sm text-stop">Stopped by the safety rules before any model replied: {out.rule_hits.filter((h) => h.action === "block").map((h) => h.message).join("; ")}</p>}
      {out?.tree && (
        <div className="space-y-3" aria-live="polite">
          <p className="text-sm">{out.tree.summary}</p>
          <ol className="space-y-3">
            {out.tree.steps.map((s) => {
              const removed = /Removed by the independent auditor/.test(s.action);
              return (
              <li key={s.id} className={`rounded-xl border p-3 text-sm ${s.safety_class === "stop" ? "border-stop" : s.safety_class === "caution" ? "border-caution" : "border-border"}`}>
                {removed
                  ? <p className="font-medium">{s.id}. Step removed by the Nemotron 3 Ultra audit. Read page {s.cite.page} of your manual yourself before acting.</p>
                  : <p className="font-medium">{s.id}. {s.action}</p>}
                {s.expected && !removed && <p className="text-fg-muted">Expected: {s.expected}</p>}
                {s.cite?.quote && <blockquote className="mt-2 border-l-4 border-accent pl-3">&ldquo;{s.cite.quote}&rdquo;<span className="block text-xs text-fg-muted">Your manual, page {s.cite.page}</span></blockquote>}
              </li>
              );
            })}
          </ol>
          <p className="text-xs text-fg-muted">
            {out.citations?.verified ?? 0} of {out.citations?.total ?? 0} quotes found word for word on the cited page.
            {out.audit ? ` Ultra audit: ${out.audit.overall.replaceAll("_", " ")}.` : ""} {Math.round(out.latency_ms / 1000)} s, ${usd.toFixed(3)}.
          </p>
        </div>
      )}
    </div>
  );
}

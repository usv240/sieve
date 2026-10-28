"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";
import { Info } from "@/components/info";

type Rec = { id: string; created_at: number; model_label: string; reported_fault: string; outcome: string; steps_performed: string[]; ai_trace_id: string };
type Fleet = { total: number; by_outcome: Record<string, number>; by_device: Record<string, number>; open: number; downtime_hours: number };
type Item = { title: string; detail: string; evidence_ids: string[] };
type Brief = { brief: { headline: string; failing_now: Item[]; parts_to_stock: Item[]; recalls_affecting_us: Item[]; longest_downtime: Item[]; what_fda_reports_add: Item[]; confidence_note: string }; inputs: { work_orders: number; fda_reports: number; recalls: number; approx_input_tokens: number }; trace: { model: string; tokens_in: number; usd: number; latency_ms: number }[] };

export default function FleetPage() {
  const [recs, setRecs] = useState<Rec[]>([]);
  const [fleet, setFleet] = useState<Fleet | null>(null);
  const [brief, setBrief] = useState<Brief | null>(null);
  const [briefing, setBriefing] = useState(false);
  async function makeBrief() { setBriefing(true); try { const r = await fetch(apiUrl("/v1/fleet/brief"), { method: "POST" }); setBrief(await r.json()); } finally { setBriefing(false); } }
  useEffect(() => {
    fetch(apiUrl("/v1/records")).then((r) => r.json()).then(setRecs).catch(() => {});
    fetch(apiUrl("/v1/fleet")).then((r) => r.json()).then(setFleet).catch(() => {});
  }, []);
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-[1.625rem] font-semibold sm:text-3xl">Fleet <Info k="work_order" /></h1>
      {fleet && (
        <div className="grid gap-4 sm:grid-cols-4">
          <T n={fleet.total} l="work orders" /><T n={fleet.open} l="open" /><T n={fleet.by_outcome.fixed ?? 0} l="fixed" /><T n={fleet.by_outcome.needs_part ?? 0} l="waiting for a part" />
        </div>
      )}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div><p className="font-semibold">Weekly brief for the district engineer</p><p className="text-sm text-fg-muted">Every work order, all public FDA malfunction reports and recalls for this device class go into one long-context Nemotron call. Counts, parts, recalls that touch our units.</p></div>
          <button className="btn-primary" onClick={makeBrief} disabled={briefing}>{briefing ? "Reading the whole fleet…" : "Generate this week's brief"}</button>
        </div>
        {brief?.brief && (
          <div className="mt-4 space-y-3 text-sm">
            <p className="text-lg font-semibold">{brief.brief.headline}</p>
            {([["Failing now", brief.brief.failing_now], ["Parts to stock", brief.brief.parts_to_stock], ["Recalls affecting us", brief.brief.recalls_affecting_us], ["Longest downtime", brief.brief.longest_downtime], ["What the FDA reports add", brief.brief.what_fda_reports_add]] as [string, Item[]][]).map(([h, items]) => items.length ? (
              <div key={h}><p className="eyebrow">{h}</p><ul className="mt-1 space-y-1">{items.map((i) => <li key={i.title}><b>{i.title}.</b> {i.detail}</li>)}</ul></div>
            ) : null)}
            <p className="text-xs text-fg-muted">{brief.brief.confidence_note} Inputs: about {brief.inputs.approx_input_tokens.toLocaleString()} tokens in one call{brief.trace[0] ? ` to ${brief.trace[0].model}, $${brief.trace[0].usd.toFixed(4)}, ${(brief.trace[0].latency_ms / 1000).toFixed(0)} s` : ""}.</p>
          </div>
        )}
      </div>
      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm"><thead className="text-left text-fg-muted"><tr><th className="p-3">When</th><th className="p-3">Device</th><th className="p-3">Fault</th><th className="p-3">Outcome</th><th className="p-3">Steps</th></tr></thead>
          <tbody>{recs.map((r) => <tr key={r.id} className="border-t border-border"><td className="p-3 whitespace-nowrap">{new Date(r.created_at * 1000).toLocaleString()}</td><td className="p-3">{r.model_label}</td><td className="p-3">{r.reported_fault}</td><td className="p-3">{r.outcome}</td><td className="p-3">{r.steps_performed.length}</td></tr>)}
          {recs.length === 0 && <tr><td className="p-3 text-fg-muted" colSpan={5}>No work orders yet. Run a fix on the Try page and save it.</td></tr>}</tbody></table>
      </div>
    </div>
  );
}
function T({ n, l }: { n: number; l: string }) { return <div className="card"><p className="text-3xl font-semibold">{n}</p><p className="text-sm text-fg-muted">{l}</p></div>; }

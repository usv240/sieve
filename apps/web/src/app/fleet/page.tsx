"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";
import { Info } from "@/components/info";

type Rec = { id: string; created_at: number; model_label: string; reported_fault: string; outcome: string; steps_performed: string[]; ai_trace_id: string };
type Fleet = { total: number; by_outcome: Record<string, number>; by_device: Record<string, number>; open: number; downtime_hours: number };

export default function FleetPage() {
  const [recs, setRecs] = useState<Rec[]>([]);
  const [fleet, setFleet] = useState<Fleet | null>(null);
  useEffect(() => {
    fetch(apiUrl("/v1/records")).then((r) => r.json()).then(setRecs).catch(() => {});
    fetch(apiUrl("/v1/fleet")).then((r) => r.json()).then(setFleet).catch(() => {});
  }, []);
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">Fleet <Info k="work_order" /></h1>
      {fleet && (
        <div className="grid gap-4 sm:grid-cols-4">
          <T n={fleet.total} l="work orders" /><T n={fleet.open} l="open" /><T n={fleet.by_outcome.fixed ?? 0} l="fixed" /><T n={fleet.by_outcome.needs_part ?? 0} l="waiting for a part" />
        </div>
      )}
      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm"><thead className="text-left text-fg-muted"><tr><th className="p-3">When</th><th className="p-3">Device</th><th className="p-3">Fault</th><th className="p-3">Outcome</th><th className="p-3">Steps</th></tr></thead>
          <tbody>{recs.map((r) => <tr key={r.id} className="border-t border-border"><td className="p-3 whitespace-nowrap">{new Date(r.created_at * 1000).toLocaleString()}</td><td className="p-3">{r.model_label}</td><td className="p-3">{r.reported_fault}</td><td className="p-3">{r.outcome}</td><td className="p-3">{r.steps_performed.length}</td></tr>)}
          {recs.length === 0 && <tr><td className="p-3 text-fg-muted" colSpan={5}>No work orders yet. Run a fix on the Try page and save it.</td></tr>}</tbody></table>
      </div>
    </div>
  );
}
function T({ n, l }: { n: number; l: string }) { return <div className="card"><p className="text-3xl font-semibold">{n}</p><p className="text-sm text-fg-muted">{l}</p></div>; }

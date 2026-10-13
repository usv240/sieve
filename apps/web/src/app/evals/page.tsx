"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";
import { Info } from "@/components/info";

type Section = { name: string; description: string; rows: Record<string, string | number | null>[]; columns: string[] };
type Evals = { status?: string; generated_at?: string; command?: string; summary?: Record<string, { value: number | string | null; unit?: string; label: string; note?: string }>; sections?: Section[] };

export default function EvalsPage() {
  const [e, setE] = useState<Evals | null>(null);
  useEffect(() => { fetch(apiUrl("/v1/evals/latest")).then((r) => r.json()).then(setE).catch(() => setE({ status: "API unreachable" })); }, []);
  return (
    <div className="space-y-8 pt-8">
      <div>
        <h1 className="text-3xl font-semibold">Evaluation <Info k="benchmark" /></h1>
        <p className="mt-2 max-w-2xl text-fg-muted">Two external benchmarks nobody on the team authored, two named baselines, three negative controls, citation integrity, offline delta and cost. Everything on this page is read from <code>eval/results/latest.json</code> in the repository.</p>
      </div>
      {!e && <p className="text-fg-muted">Loading…</p>}
      {e && !e.summary && <div className="card text-fg-muted">No published run yet. Status: {e.status}. Reproduce with <code>make eval</code>.</div>}
      {e?.summary && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(e.summary).map(([k, v]) => (
              <div key={k} className="card"><p className="text-3xl font-semibold">{v.value === null ? "n/a" : v.value}{v.unit ?? ""}</p><p className="mt-1 text-sm font-medium">{v.label}</p>{v.note && <p className="mt-1 text-xs text-fg-muted">{v.note}</p>}</div>
            ))}
          </div>
          {e.sections?.map((s) => (
            <section key={s.name} className="space-y-2">
              <h2 className="text-xl font-semibold">{s.name}</h2>
              <p className="text-fg-muted">{s.description}</p>
              <div className="card overflow-x-auto p-0"><table className="w-full text-sm"><thead className="text-left text-fg-muted"><tr>{s.columns.map((c) => <th key={c} className="p-3">{c}</th>)}</tr></thead>
                <tbody>{s.rows.map((r, i) => <tr key={i} className="border-t border-border">{s.columns.map((c) => <td key={c} className="p-3">{String(r[c] ?? "")}</td>)}</tr>)}</tbody></table></div>
            </section>
          ))}
          <div className="card text-sm"><p className="font-semibold">Reproduce</p><pre className="mt-2 overflow-x-auto rounded-xl bg-bg p-3">{e.command ?? "make eval"}</pre><p className="mt-2 text-fg-muted">Generated {e.generated_at}. Negative controls <Info k="negative_control" /> run without any model key; benchmarks need a Token Factory key.</p></div>
        </>
      )}
    </div>
  );
}

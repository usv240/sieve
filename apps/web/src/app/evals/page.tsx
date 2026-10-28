import { Info } from "@/components/info";
import { cacheLife } from "next/cache";
import { API_BASE } from "@/lib/api";
import { EVAL_HELP, SECTION_COLUMNS, SECTION_DESC, SECTION_HIDDEN, featured } from "@/lib/eval-help";

export const metadata = { title: "Evaluation" };

type Section = { name: string; description: string; rows: Record<string, string | number | boolean | null>[]; columns: string[] };
type Evals = { status?: string; generated_at?: string; command?: string; summary?: Record<string, { value: number | string | null; unit?: string; label: string; note?: string }>; sections?: Section[] };

async function load(): Promise<Evals> {
  "use cache";
  cacheLife("minutes");
  try {
    const r = await fetch(`${API_BASE}/v1/evals/latest`);
    return (await r.json()) as Evals;
  } catch {
    return { status: "API unreachable when this page was built; it refreshes every five minutes" };
  }
}

export default async function EvalsPage() {
  const e = await load();
  return (
    <div className="space-y-8 pt-8">
      <div>
        <h1 className="text-3xl font-semibold">Evaluation <Info k="benchmark" /></h1>
        <p className="mt-2 max-w-2xl text-fg-muted">Two external benchmarks nobody on the team authored: the closest prior work's own question set and real openFDA malfunction reports, both scored by two independent judges against named baselines. Also negative controls, citation integrity, the offline comparison and cost. Everything on this page is read from <code>eval/results/latest.json</code> in the repository.</p>
      </div>
      {!e.summary && <div className="card text-fg-muted">No published run yet. Status: {e.status}. Reproduce with <code>make eval</code>.</div>}
      {e.summary && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {featured(e.summary).map(([k, v]) => (
              <div key={k} className="card"><p className="text-3xl font-semibold">{v.value === null ? "n/a" : v.value}{v.unit ?? ""}</p><p className="mt-1 text-sm font-medium">{v.label} <Info term={v.label} text={EVAL_HELP[k] ?? v.note ?? ""} /></p>{v.note && <p className="mt-1 text-xs text-fg-muted">{v.note}</p>}</div>
            ))}
          </div>
          {e.sections?.filter((s) => !SECTION_HIDDEN.some((h) => s.name.startsWith(h))).map((x) => ({ ...x, columns: SECTION_COLUMNS[x.name] ?? x.columns, description: SECTION_DESC[x.name] ?? x.description })).map((s) => (
            <section key={s.name} className="space-y-2">
              <h2 className="text-xl font-semibold">{s.name}</h2>
              <p className="text-fg-muted">{s.description}</p>
              <div className="card overflow-x-auto p-0"><table className="w-full text-sm"><thead className="text-left text-fg-muted"><tr>{s.columns.map((c) => <th key={c} className="p-3">{c}</th>)}</tr></thead>
                <tbody>{s.rows.slice(0, 20).map((r, i) => <tr key={i} className="border-t border-border">{s.columns.map((c) => <td key={c} className="p-3">{String(r[c] ?? "")}</td>)}</tr>)}</tbody></table></div>
              {s.rows.length > 20 && <p className="text-sm text-fg-muted">Showing 20 of {s.rows.length} rows. Every row is in <a className="text-accent underline underline-offset-2" href="https://github.com/usv240/sieve/blob/main/eval/results/latest.json">eval/results/latest.json</a> and at <a className="text-accent underline underline-offset-2" href={`${API_BASE}/v1/evals/latest`}>/v1/evals/latest</a>.</p>}
            </section>
          ))}
          <div className="card text-sm"><p className="font-semibold">Reproduce</p><pre className="mt-2 overflow-x-auto rounded-xl bg-bg p-3">{e.command ?? "make eval"}</pre><p className="mt-2 text-fg-muted">Generated {e.generated_at}. Negative controls <Info k="negative_control" /> run without any model key; benchmarks need a Token Factory key.</p></div>
        </>
      )}
    </div>
  );
}

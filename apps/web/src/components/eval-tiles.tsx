import { cacheLife } from "next/cache";
import { API_BASE } from "@/lib/api";
import { EVAL_HELP } from "@/lib/eval-help";
import { Info } from "@/components/info";

type Evals = { status?: string; generated_at?: string; summary?: Record<string, { value: number | string | null; unit?: string; label: string; note?: string }> };

/** Server-rendered from eval/results/latest.json through the API, so the landing page never shows a number we did not measure. */
async function load(): Promise<Evals> {
  "use cache";
  cacheLife("minutes");
  try {
    const r = await fetch(`${API_BASE}/v1/evals/latest`);
    return (await r.json()) as Evals;
  } catch {
    return { status: "unreachable" };
  }
}

export async function EvalTiles() {
  const e = await load();
  if (!e.summary) return <p className="card text-fg-muted">No evaluation run has been published yet. Run <code>make eval</code> to produce one. Status: {e.status}</p>;
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Object.entries(e.summary).map(([k, v]) => (
        <div key={k} className="card">
          <p className="text-3xl font-semibold tracking-tight">{v.value === null ? "n/a" : v.value}{v.unit ?? ""}</p>
          <p className="mt-1 text-sm font-medium">{v.label} <Info term={v.label} text={EVAL_HELP[k] ?? v.note ?? ""} /></p>
          {v.note && <p className="mt-1 text-xs text-fg-muted">{v.note}</p>}
        </div>
      ))}
      {e.generated_at && <p className="col-span-full text-xs text-fg-muted">Last run: {e.generated_at.slice(0, 10)}</p>}
    </div>
  );
}

"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ShieldAlert, AlertTriangle, CheckCircle2, ChevronRight, FileText } from "lucide-react";
import { apiUrl } from "@/lib/api";
import { SAMPLES } from "@/lib/samples";
import { Info } from "@/components/info";
import { TrainingPanel } from "@/components/training-panel";

type Match = { device_id: string; confidence: number; reason: string };
type Indicator = { id: string; state: string; meaning: string; cite: { doc: string; page: number } };
type Device = { id: string; manufacturer: string; model: string; indicators: Indicator[]; has_manual: boolean };
type Question = { id: string; text: string; why: string; type: string; options?: string[] };
type Cite = { doc: string; page: number; quote: string };
type StepT = { id: number; action: string; expected: string; if_yes: number | null; if_no: number | null; tools_needed: string[]; duration_min: number; safety_class: "none" | "caution" | "stop"; cite: Cite };
type Analyze = {
  trace_id: string; device_id: string | null; device_label: string; blocked: boolean;
  tree: { summary: string; hypotheses: { fault_id: string; likelihood: string; why: string; cite: Cite }[]; steps: StepT[]; parts_candidates: { name: string; part_number?: string }[]; escalate_if: string[] } | null;
  audit: { overall: string; verdicts: { step_id: number; verdict: string; reason: string }[] } | null;
  rule_hits: { rule_id: string; action: string; severity: string; message: string; citation: string | null }[];
  citations: { total?: number; verified?: number; integrity?: number | null };
  retrieved: { doc: string; title: string; page: number }[];
  recalls: { recall_number: string; reason: string; date: string }[];
  maude: { reports?: number; top_problems?: [string, number][]; source?: string };
  notes: string[]; latency_ms: number;
  trace: { tier: string; model: string; purpose: string; tokens_in: number; tokens_out: number; usd: number; latency_ms: number }[];
};

export function TryFlow() {
  const params = useSearchParams();
  const sampleId = params.get("sample");
  const sample = useMemo(() => SAMPLES.find((s) => s.id === sampleId), [sampleId]);

  const [devices, setDevices] = useState<Device[]>([]);
  const [fields, setFields] = useState({ manufacturer: "", model: "", ref: "", visible_text: "" });
  const [matches, setMatches] = useState<Match[]>([]);
  const [deviceId, setDeviceId] = useState<string | null>(null);
  const [indicators, setIndicators] = useState<string[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [freeText, setFreeText] = useState("");
  const [result, setResult] = useState<Analyze | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [step, setStep] = useState(0);
  const [visited, setVisited] = useState<number[]>([]);
  const [outcome, setOutcome] = useState<string>("open");
  const [saved, setSaved] = useState<string | null>(null);
  const [showSim, setShowSim] = useState(false);

  useEffect(() => { fetch(apiUrl("/v1/devices")).then((r) => r.json()).then(setDevices).catch(() => {}); }, []);

  // Preload a sample: fields, indicators, answers.
  useEffect(() => {
    if (!sample) return;
    setFields({ manufacturer: sample.fields.manufacturer ?? "", model: sample.fields.model ?? "", ref: sample.fields.ref ?? "", visible_text: (sample.fields.visible_text ?? []).join(", ") });
    setIndicators(sample.indicator_ids);
    setAnswers(sample.answers);
    setFreeText(sample.free_text ?? "");
    setResult(null); setMatches([]); setDeviceId(null);
  }, [sample]);

  const device = devices.find((d) => d.id === deviceId);

  async function identify() {
    setBusy("Identifying…");
    const r = await fetch(apiUrl("/v1/identify"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ manufacturer: fields.manufacturer || null, model: fields.model || null, ref: fields.ref || null, visible_text: fields.visible_text.split(",").map((s) => s.trim()).filter(Boolean) }) });
    const j = await r.json();
    setMatches(j.matches);
    const top = j.matches[0];
    const id = top && top.confidence >= 0.6 ? top.device_id : null;
    setDeviceId(id);
    const q = await fetch(apiUrl(`/v1/questions?device_id=${id ?? ""}&indicator_ids=${indicators.join(",")}`)).then((x) => x.json());
    setQuestions(q);
    setBusy(null);
  }

  async function analyze() {
    setBusy("Reading the manual and building the fault tree…");
    const r = await fetch(apiUrl("/v1/analyze"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ device_id: deviceId, indicator_ids: indicators, answers, free_text: freeText, audit: true }) });
    const j: Analyze = await r.json();
    setResult(j); setStep(0); setVisited([]); setBusy(null);
  }

  async function save() {
    if (!result) return;
    const wo = { device_id: result.device_id ?? "unknown", model_label: result.device_label, reported_fault: result.tree?.summary ?? freeText ?? "n/a", indicators, steps_performed: visited.map((i) => result.tree?.steps[i]?.action ?? ""), outcome, ai_trace_id: result.trace_id, notes: "" };
    const r = await fetch(apiUrl("/v1/records"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(wo) });
    const j = await r.json();
    setSaved(j.id);
  }

  const steps = result?.tree?.steps ?? [];
  const current = steps[step];
  const go = (next: number | null) => { setVisited((v) => [...v, step]); if (next != null) { const idx = steps.findIndex((s) => s.id === next); if (idx >= 0) setStep(idx); } };

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className="space-y-6">
        {/* Screen 1: Identify */}
        <section className="card space-y-3">
          <h1 className="text-2xl font-semibold">1. Identify the device <Info k="service_manual" /></h1>
          <p className="text-sm text-fg-muted">Type what the nameplate says, use a sample, or photograph the Training Mode panel <Info k="training_mode" />. Vision describes; the registry decides.</p>
          <div className="grid gap-3 sm:grid-cols-2">
            <L label="Manufacturer"><input className="inp" value={fields.manufacturer} onChange={(e) => setFields({ ...fields, manufacturer: e.target.value })} /></L>
            <L label="Model"><input className="inp" value={fields.model} onChange={(e) => setFields({ ...fields, model: e.target.value })} /></L>
            <L label="REF or part number"><input className="inp" value={fields.ref} onChange={(e) => setFields({ ...fields, ref: e.target.value })} /></L>
            <L label="Other visible text, comma separated"><input className="inp" value={fields.visible_text} onChange={(e) => setFields({ ...fields, visible_text: e.target.value })} /></L>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="btn-primary" onClick={identify} disabled={!!busy}>Identify</button>
            <button className="btn-ghost" onClick={() => setShowSim((v) => !v)}>{showSim ? "Hide" : "Open"} Training Mode simulator</button>
          </div>
          {showSim && <TrainingPanel onPick={(devId, indId) => { setDeviceId(devId); setIndicators([indId]); const d = devices.find((x) => x.id === devId); if (d) setFields({ manufacturer: d.manufacturer, model: d.model, ref: "", visible_text: "" }); }} />}
          {matches.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Matches</p>
              {matches.map((m) => (
                <button key={m.device_id} onClick={() => setDeviceId(m.device_id)} className={`flex w-full items-center justify-between rounded-xl border p-3 text-left ${deviceId === m.device_id ? "border-accent" : "border-border"}`}>
                  <span>{devices.find((d) => d.id === m.device_id)?.manufacturer} {devices.find((d) => d.id === m.device_id)?.model}</span>
                  <span className="text-sm text-fg-muted">{Math.round(m.confidence * 100)}% · {m.reason}</span>
                </button>
              ))}
              {!deviceId && <p className="text-sm text-caution">Low confidence. Pick a match above, or continue as unknown: Sieve will show generic checks only and will not invent part numbers.</p>}
            </div>
          )}
          {matches.length === 0 && fields.manufacturer && !busy && result === null && <p className="text-sm text-fg-muted">Press Identify.</p>}
        </section>

        {/* Screen 2: What do you see */}
        {(deviceId || matches.length > 0) && (
          <section className="card space-y-3">
            <h2 className="text-xl font-semibold">2. What do you see? <Info k="purity" /></h2>
            {device?.indicators?.length ? (
              <div className="grid gap-2 sm:grid-cols-2">
                {device.indicators.map((i) => (
                  <button key={i.id} onClick={() => setIndicators((v) => v.includes(i.id) ? v.filter((x) => x !== i.id) : [...v, i.id])} className={`rounded-xl border p-3 text-left ${indicators.includes(i.id) ? "border-accent bg-accent/10" : "border-border"}`}>
                    <p className="font-medium">{i.state}</p>
                    <p className="text-sm text-fg-muted">{i.meaning}</p>
                    <p className="text-xs text-fg-muted">Manual page {i.cite.page}</p>
                  </button>
                ))}
              </div>
            ) : <p className="text-sm text-fg-muted">No indicator table for this device yet. Describe what you see below.</p>}
            <div className="space-y-2">
              {questions.map((q) => (
                <div key={q.id} className="flex flex-wrap items-center gap-2">
                  <span className="text-sm">{q.text} <Info k="grounded" label={q.why} /></span>
                  {(q.type === "yes_no" ? ["yes", "no"] : (q.options ?? [])).map((o) => (
                    <button key={o} onClick={() => setAnswers({ ...answers, [q.id]: o })} className={`btn-ghost min-h-0 px-3 py-1.5 text-sm ${answers[q.id] === o ? "border-accent" : ""}`}>{o}</button>
                  ))}
                </div>
              ))}
            </div>
            <L label="Anything else (optional)"><textarea className="inp min-h-20" value={freeText} onChange={(e) => setFreeText(e.target.value)} /></L>
            <button className="btn-primary" onClick={analyze} disabled={!!busy}>Build the fix</button>
            {busy && <p className="text-sm text-fg-muted" role="status">{busy}</p>}
          </section>
        )}

        {/* Screen 3: Fix */}
        {result && (
          <section className="card space-y-4">
            <h2 className="text-xl font-semibold">3. Fix: {result.device_label}</h2>
            {result.rule_hits.filter((h) => h.severity === "stop").map((h) => (
              <div key={h.rule_id} role="alert" className="rounded-[16px] border-2 border-stop p-4">
                <p className="flex items-center gap-2 font-semibold text-stop"><ShieldAlert className="h-5 w-5" /> Stop</p>
                <p className="mt-1">{h.message}</p>
                {h.citation && <p className="mt-1 text-xs text-fg-muted">Source: {h.citation}</p>}
              </div>
            ))}
            {result.blocked && <p className="text-fg-muted">Sieve stopped before asking any model. Nothing else is shown for this request.</p>}
            {!result.tree && !result.blocked && (
              <div className="space-y-2 text-sm text-fg-muted">
                <p>{result.notes.join(" ")}</p>
                {result.retrieved.length > 0 && <p>Retrieved manual pages: {result.retrieved.map((r) => `${r.title} p${r.page}`).join("; ")}</p>}
                <p>With a Token Factory key, Nemotron 3 Super writes the fault tree from these pages and Nemotron 3 Ultra audits it.</p>
              </div>
            )}
            {result.tree && (
              <>
                <p className="text-fg">{result.tree.summary}</p>
                <div className="flex flex-wrap gap-2 text-xs text-fg-muted">
                  <span>Citations verified {result.citations.verified}/{result.citations.total}</span>
                  {result.audit && <span>Auditor: {result.audit.overall}</span>}
                  <span>{result.latency_ms} ms</span>
                </div>
                {current && (
                  <div className={`rounded-[16px] border-2 p-4 ${current.safety_class === "stop" ? "border-stop" : current.safety_class === "caution" ? "border-caution" : "border-border"}`}>
                    <p className="eyebrow">Step {current.id} of {steps.length}</p>
                    <p className="mt-1 flex items-start gap-2 text-lg font-medium">
                      {current.safety_class === "stop" ? <ShieldAlert className="mt-1 h-5 w-5 text-stop" /> : current.safety_class === "caution" ? <AlertTriangle className="mt-1 h-5 w-5 text-caution" /> : <CheckCircle2 className="mt-1 h-5 w-5 text-ok" />}
                      {current.action}
                    </p>
                    <p className="mt-2 text-fg-muted">Expect: {current.expected}</p>
                    <p className="mt-2 text-xs text-fg-muted">Tools: {current.tools_needed.join(", ") || "none"} · about {current.duration_min} min</p>
                    <blockquote className="quote mt-3 text-sm">“{current.cite.quote}”<footer className="mt-1 text-xs text-fg-muted">{current.cite.doc}, page {current.cite.page} · <a className="text-accent" href={apiUrl(`/v1/page/${current.cite.doc}/${current.cite.page}`)} target="_blank" rel="noreferrer">Show page</a></footer></blockquote>
                    <div className="mt-3 flex gap-2">
                      <button className="btn-primary" onClick={() => go(current.if_yes)}>Yes, as expected <ChevronRight className="h-4 w-4" /></button>
                      <button className="btn-ghost" onClick={() => go(current.if_no)}>No</button>
                    </div>
                  </div>
                )}
                <details className="text-sm"><summary className="cursor-pointer text-fg-muted">All hypotheses and steps</summary>
                  <ul className="mt-2 space-y-1">{result.tree.hypotheses.map((h) => <li key={h.fault_id}><b>{h.fault_id}</b> ({h.likelihood}): {h.why}</li>)}</ul>
                  <ol className="mt-2 list-decimal space-y-1 pl-5">{steps.map((s) => <li key={s.id}>{s.action}</li>)}</ol>
                </details>
              </>
            )}
            {/* Screen 4: Record */}
            {!result.blocked && (
              <div className="rounded-[16px] border border-border p-4">
                <h3 className="font-semibold">4. Record the work order <Info k="work_order" /></h3>
                <div className="mt-2 flex flex-wrap gap-2">
                  {["fixed", "needs_part", "escalated", "open"].map((o) => <button key={o} onClick={() => setOutcome(o)} className={`btn-ghost min-h-0 px-3 py-1.5 text-sm ${outcome === o ? "border-accent" : ""}`}>{o.replace("_", " ")}</button>)}
                </div>
                <button className="btn-primary mt-3" onClick={save}>Save to fleet log</button>
                {saved && <p className="mt-2 text-sm text-ok">Saved. Work order {saved.slice(0, 8)}. <a className="text-accent" href="/fleet">Open the fleet view</a>.</p>}
              </div>
            )}
          </section>
        )}
      </div>

      {/* Right rail */}
      <aside className="space-y-4">
        {result && (
          <>
            <div className="card text-sm">
              <p className="font-semibold">Recalls and known problems <Info k="recall" /></p>
              {result.recalls.length === 0 && <p className="mt-1 text-fg-muted">No recall matched this model in the openFDA snapshot.</p>}
              {result.recalls.map((r) => <p key={r.recall_number} className="mt-1 text-fg-muted">{r.date}: {r.reason}</p>)}
              {result.maude?.reports ? <p className="mt-2 text-fg-muted">{result.maude.reports} FDA malfunction reports for this brand. Top: {result.maude.top_problems?.map(([p, n]) => `${p} (${n})`).join(", ")}</p> : null}
            </div>
            <div className="card text-sm">
              <p className="font-semibold">Trace <Info k="trace" /></p>
              {result.trace.length === 0 && <p className="mt-1 text-fg-muted">No model calls (replay or offline-manual mode).</p>}
              <ul className="mt-1 space-y-1">
                {result.trace.map((t, i) => <li key={i} className="flex justify-between gap-2 text-fg-muted"><span>{t.model} · {t.purpose}</span><span>{t.tokens_in + t.tokens_out} tok · ${t.usd.toFixed(4)}</span></li>)}
              </ul>
            </div>
            <div className="card text-sm">
              <p className="flex items-center gap-2 font-semibold"><FileText className="h-4 w-4" /> Pages used</p>
              <ul className="mt-1 space-y-1 text-fg-muted">{result.retrieved.map((r) => <li key={`${r.doc}-${r.page}`}>{r.title}, p{r.page}</li>)}</ul>
            </div>
          </>
        )}
        {!result && <div className="card text-sm text-fg-muted">Results, recalls and the model Trace appear here.</div>}
      </aside>
    </div>
  );
}

function L({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block text-sm"><span className="mb-1 block text-fg-muted">{label}</span>{children}</label>;
}

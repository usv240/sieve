"use client";

import { useEffect, useState } from "react";
import { Check, Copy, Download, KeyRound, Play, ShieldX } from "lucide-react";
import { API_BASE, apiUrl } from "@/lib/api";
import { Info } from "@/components/info";

export type Preset = { id: string; title: string; note: string; method: "GET" | "POST"; path: string; body?: unknown };

const STORE = "api-console.key";

function download(name: string, data: unknown) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  a.click();
  URL.revokeObjectURL(url);
}

/** Create a real key, then call the hosted API with it from this page. Nothing here is mocked. */
export function ApiConsole({ presets, product }: { presets: Preset[]; product: string }) {
  const [label, setLabel] = useState("judge");
  const [key, setKey] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [preset, setPreset] = useState<Preset>(presets[0]);
  const [busy, setBusy] = useState(false);
  const [res, setRes] = useState<{ status: number; ms: number; remaining: string | null; body: unknown } | null>(null);

  useEffect(() => { setKey(localStorage.getItem(STORE)); }, []);

  async function createKey() {
    const r = await fetch(apiUrl("/v1/keys"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ label }) });
    const j = await r.json();
    setKey(j.key);
    localStorage.setItem(STORE, j.key);
  }

  async function run(useKey: string | null) {
    setBusy(true); setRes(null);
    const t0 = performance.now();
    try {
      const r = await fetch(apiUrl(preset.path), {
        method: preset.method,
        headers: { ...(preset.body ? { "content-type": "application/json" } : {}), ...(useKey ? { "X-API-Key": useKey } : {}) },
        body: preset.body ? JSON.stringify(preset.body) : undefined,
      });
      const body = await r.json().catch(() => ({ error: "response was not JSON" }));
      setRes({ status: r.status, ms: Math.round(performance.now() - t0), remaining: r.headers.get("X-RateLimit-Remaining"), body });
    } catch {
      setRes({ status: 0, ms: Math.round(performance.now() - t0), remaining: null, body: { error: "network error: the API could not be reached" } });
    } finally { setBusy(false); }
  }

  function copy(text: string, what: string) {
    navigator.clipboard.writeText(text).then(() => { setCopied(what); setTimeout(() => setCopied(null), 1500); });
  }

  const curl = `curl -X ${preset.method} ${API_BASE}${preset.path} \\\n  -H "X-API-Key: ${key ?? "<your key>"}"${preset.body ? ` \\\n  -H "content-type: application/json" \\\n  -d '${JSON.stringify(preset.body)}'` : ""}`;

  return (
    <section aria-labelledby="console-h" className="card space-y-6">
      <div>
        <h2 id="console-h" className="text-xl font-semibold">Try the API live <Info term="Live API console" text={`This panel calls the real hosted ${product} API from your browser. Create a key, pick a request, run it, and download the response. Nothing on this panel is a recording.`} /></h2>
        <p className="mt-1 text-sm text-fg-muted">Three steps, all real calls to {API_BASE}.</p>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold">1. Create an API key <Info term="API key" text="A key identifies your app to the API. Ours are signed by the server, so any server can check one without a database. A forged or edited key is refused with error 401. Your key is kept only in this browser." /></h3>
        <div className="flex flex-wrap items-end gap-3">
          <label className="block text-sm"><span className="mb-1 block text-fg-muted">Name for the key</span>
            <input className="inp w-48" value={label} onChange={(e) => setLabel(e.target.value)} maxLength={24} />
          </label>
          <button type="button" className="btn-primary" onClick={createKey}><KeyRound className="h-4 w-4" aria-hidden /> Create key</button>
        </div>
        {key && (
          <div className="flex flex-wrap items-center gap-2 rounded-xl border border-border bg-bg p-3">
            <code className="break-all text-xs">{key}</code>
            <button type="button" className="btn-ghost min-h-0 px-2 py-1 text-xs" onClick={() => copy(key, "key")}>{copied === "key" ? <Check className="h-3.5 w-3.5" aria-hidden /> : <Copy className="h-3.5 w-3.5" aria-hidden />} {copied === "key" ? "Copied" : "Copy"}</button>
          </div>
        )}
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold">2. Pick a request <Info term="Presets" text="Ready-made requests that show what the API does. Each one is the same call the web app makes. You can copy any of them as a curl command and run it from your own terminal." /></h3>
        <div role="radiogroup" aria-label="Request presets" className="grid gap-2 sm:grid-cols-3">
          {presets.map((p) => (
            <button key={p.id} type="button" role="radio" aria-checked={preset.id === p.id} onClick={() => { setPreset(p); setRes(null); }}
              className={`rounded-xl border p-3 text-left text-sm ${preset.id === p.id ? "border-accent bg-bg" : "border-border bg-bg-elev hover:border-accent"}`}>
              <span className="block font-semibold">{p.title}</span>
              <span className="mt-1 block text-xs text-fg-muted">{p.note}</span>
              <span className="mt-2 block font-mono text-xs text-accent">{p.method} {p.path}</span>
            </button>
          ))}
        </div>
        <div className="rounded-xl border border-border">
          <div className="flex items-center justify-between border-b border-border px-3 py-1.5 text-xs text-fg-muted"><span>curl</span>
            <button type="button" className="btn-ghost min-h-0 border-0 px-2 py-1 text-xs" onClick={() => copy(curl, "curl")}>{copied === "curl" ? "Copied" : "Copy"}</button>
          </div>
          <pre className="overflow-x-auto p-3 text-xs leading-relaxed">{curl}</pre>
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold">3. Run it <Info term="Run" text="Sends the request with your key. The status line shows the HTTP code, how long it took, and how many requests you have left this minute. A wrong key shows what an integrator sees when a key is forged." /></h3>
        <div className="flex flex-wrap gap-3">
          <button type="button" className="btn-primary" disabled={busy} onClick={() => run(key)}><Play className="h-4 w-4" aria-hidden /> {busy ? "Running…" : key ? "Run with my key" : "Run without a key"}</button>
          <button type="button" className="btn-ghost" disabled={busy} onClick={() => run(`${product.toLowerCase()}_forged_AAAAAAAAAAAAAAAA.000000000000000000000000`)}><ShieldX className="h-4 w-4" aria-hidden /> Try a forged key</button>
        </div>
        {busy && <p className="text-sm text-fg-muted" aria-live="polite">Calling the live API. Requests that run the full pipeline take 10 to 30 seconds.</p>}
        {res && (
          <div className="space-y-2" aria-live="polite">
            <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
              <span className={`font-semibold ${res.status >= 200 && res.status < 300 ? "text-ok" : "text-stop"}`}>HTTP {res.status || "error"}</span>
              <span className="text-fg-muted">{res.ms} ms</span>
              {res.remaining && <span className="text-fg-muted">{res.remaining} requests left this minute</span>}
              <button type="button" className="btn-ghost ml-auto min-h-0 px-2 py-1 text-xs" onClick={() => download(`${product.toLowerCase()}-${preset.id}.json`, res.body)}><Download className="h-3.5 w-3.5" aria-hidden /> Download JSON</button>
            </p>
            <pre className="max-h-96 overflow-auto rounded-xl border border-border bg-bg p-3 text-xs leading-relaxed">{JSON.stringify(res.body, null, 2)}</pre>
          </div>
        )}
      </div>
    </section>
  );
}

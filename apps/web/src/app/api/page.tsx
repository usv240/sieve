import { Info } from "@/components/info";
import { API_BASE } from "@/lib/api";

export const metadata = { title: "Sieve API" };

const curl = `curl -X POST ${API_BASE}/v1/analyze \\
  -H "content-type: application/json" \\
  -d '{"device_id":"philips-everflo","indicator_ids":["everflo-yellow-solid-silent"],"answers":{"warmup":"yes"}}'`;
const py = `import httpx
r = httpx.post("${API_BASE}/v1/analyze", json={
    "device_id": "philips-everflo",
    "indicator_ids": ["everflo-yellow-solid-silent"],
    "answers": {"warmup": "yes", "analyser": "yes"},
})
tree = r.json()["tree"]
for step in tree["steps"]:
    print(step["id"], step["action"], "->", step["cite"]["doc"], "p", step["cite"]["page"])`;
const js = `const r = await fetch("${API_BASE}/v1/analyze", {
  method: "POST", headers: { "content-type": "application/json" },
  body: JSON.stringify({ device_id: "devilbiss-525", indicator_ids: ["dv525-red-beep"], answers: {} }),
});
const { tree, rule_hits, citations, trace } = await r.json();`;

export default function ApiPage() {
  return (
    <div className="space-y-8 pt-8">
      <div>
        <h1 className="text-3xl font-semibold">Use Sieve as a service <Info k="api_key" /></h1>
        <p className="mt-2 max-w-2xl text-fg-muted">The same pipeline the app uses, over HTTP. OpenAPI documentation is at <a className="text-accent" href={`${API_BASE}/docs`} target="_blank" rel="noreferrer">{API_BASE}/docs</a>. Also exposed as an MCP server <Info k="mcp" /> so your own agent can call identify, analyze and records as tools.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <E m="POST" p="/v1/identify" d="Nameplate fields in, registry matches with confidence out." />
        <E m="POST" p="/v1/identify/image" d="Multipart photo in; vision describes, registry decides. Falls back to manual mode, never errors." />
        <E m="GET" p="/v1/devices" d="Registry: models, cited indicator tables, whether a manual is indexed." />
        <E m="POST" p="/v1/analyze" d="Device, indicators and answers in; fault tree with verbatim citations, rule hits, audit verdicts, recalls and the Trace out." />
        <E m="GET" p="/v1/page/{doc}/{page}" d="The manual page text behind any citation." />
        <E m="POST" p="/v1/records" d="File a work order. GET lists; /v1/fleet aggregates." />
        <E m="GET" p="/v1/evals/latest" d="The published evaluation JSON." />
        <E m="GET" p="/v1/costs" d="Token and USD totals by model from the ledger." />
      </div>
      <div className="space-y-4">
        <Code title="curl" code={curl} /><Code title="Python" code={py} /><Code title="JavaScript" code={js} />
      </div>
      <div className="card text-sm text-fg-muted">API keys and per-workspace rate limits are issued from the account page once hosted. During the hackathon the demo API is open and rate limited; please be gentle.</div>
    </div>
  );
}

function E({ m, p, d }: { m: string; p: string; d: string }) {
  return <div className="card"><p className="font-mono text-sm"><span className="font-semibold text-accent">{m}</span> {p}</p><p className="mt-1 text-sm text-fg-muted">{d}</p></div>;
}
function Code({ title, code }: { title: string; code: string }) {
  return <div className="card p-0"><p className="border-b border-border px-4 py-2 text-sm font-semibold">{title}</p><pre className="overflow-x-auto p-4 text-xs leading-relaxed">{code}</pre></div>;
}

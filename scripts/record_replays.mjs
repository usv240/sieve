// Record a live result for every sample preset, from the samples file the web app itself uses.
// Usage: node record_replays.mjs <samples.ts> <api base> <out dir> <sieve|antidote>
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const [, , samplesPath, api, outDir, app] = process.argv;
const src = readFileSync(samplesPath, "utf8");
const start = src.indexOf("[", src.indexOf("SAMPLES: Sample[] =")); const body = src.slice(start, src.lastIndexOf("]") + 1);
const SAMPLES = Function(`"use strict"; return (${body});`)();
mkdirSync(outDir, { recursive: true });

for (const s of SAMPLES) {
  const req = app === "sieve"
    ? { device_id: null, indicator_ids: s.indicator_ids, answers: s.answers, free_text: s.free_text ?? "", audit: true, _fields: s.fields }
    : { label: s.label, context: s.context ?? {}, audit: true };
  if (app === "sieve") {
    const id = await fetch(`${api}/v1/identify`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(s.fields) }).then((r) => r.json());
    const top = id.matches?.[0];
    req.device_id = top && top.confidence >= 0.6 ? top.device_id : null;
    delete req._fields;
  }
  const t0 = Date.now();
  const r = await fetch(`${api}/v1/analyze`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(req) });
  const j = await r.json();
  if (r.status !== 200) { console.log(s.id, "FAILED", r.status, JSON.stringify(j).slice(0, 200)); continue; }
  writeFileSync(join(outDir, `${s.id}.json`), JSON.stringify({ sample_id: s.id, recorded_at: new Date().toISOString(), request: req, response: j }, null, 1));
  console.log(s.id, "recorded", r.status, `${Date.now() - t0} ms`);
}

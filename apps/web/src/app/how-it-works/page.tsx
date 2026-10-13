import { Info } from "@/components/info";
import { Explain } from "@/components/explain-mode";

export const metadata = { title: "How Sieve works" };

const stages = [
  { t: "Look", plain: "You photograph the nameplate and the lights. A vision model lists what it can read: maker, model, REF, which lights are on. It does not decide anything.", tech: "NVIDIA Nemotron Nano VL (12B) served by vLLM on a Nebius Serverless Endpoint, prompted for structured fields only. Fallback chain: a Token Factory image2text model resolved from /v1/models, then manual entry. The fallback in use is shown in the status strip." },
  { t: "Match", plain: "A registry of known models turns those words into a device and tells us which manual to open.", tech: "Deterministic matcher: exact alias or REF first, then fuzzy manufacturer plus model (rapidfuzz). Below 0.6 confidence the UI asks you to pick among three candidates. Unknown devices get generic flowcharts and a BYO prompt; no part numbers are ever guessed." },
  { t: "Ask", plain: "Up to three questions whose answers change the fix: has it warmed up, is a patient connected, do you have an analyser.", tech: "Finite question bank in intake.yaml. Nemotron 3 Nano (thinking off, about $0.06 per million tokens) may re-rank, never invent. The patient-safety question is always first." },
  { t: "Find", plain: "We look up the right pages in the real service manual for that model.", tech: "9,458 pages from 165 manuals indexed locally (SQLite FTS5 BM25 today; Nemotron embed-vl and rerank-vl on the ingestion Job for hybrid search). Retrieval is device-scoped so an EverFlo query never returns a Nuvo page." },
  { t: "Write", plain: "A larger model writes the steps, one action at a time, each with the sentence from the manual it came from.", tech: "Nemotron 3 Super via Token Factory, tool-call schema FaultTree: hypotheses, steps with if_yes and if_no branches, tools, duration, safety_class, and a verbatim cite {doc, page, quote} on every item." },
  { t: "Verify", plain: "We check that every quoted sentence really is on that page. If not, the step is replaced by the page itself.", tech: "Deterministic exact-span verifier with whitespace and hyphenation normalisation. Citation integrity is reported per request and across the eval set (target 100 percent)." },
  { t: "Gate", plain: "Rules stop dangerous steps before you see them: no oil near oxygen, unplug before opening, never bypass the purity alarm.", tech: "YAML rules evaluated per sentence on input and output. Actions: block, rewrite with precondition, escalate, annotate. Hits are logged and rendered as stop cards with the source. The model is never asked whether a rule applies." },
  { t: "Audit", plain: "The biggest model reads the entire manual and the proposed steps and approves, repairs or rejects each one.", tech: "Nemotron 3 Ultra (550B, 1M context) receives the full manual text and the tree; returns approve, repair or reject per step with reasons. Rejected steps are demoted to 'see page N'." },
  { t: "Enrich", plain: "We check the FDA's public recall and malfunction database for this model and look up parts with Tavily.", tech: "openFDA device/recall and device/event snapshots (CC0) matched by brand and aliases; Tavily search and extract for manuals not in the corpus and for part availability." },
  { t: "Record", plain: "The repair is filed as a work order and the fleet view updates.", tech: "WHO CMMS-aligned schema, JSONL store per workspace, CSV and PDF export, /v1/fleet aggregates." },
];

export default function HowItWorks() {
  return (
    <div className="space-y-8 pt-8">
      <div>
        <h1 className="text-3xl font-semibold">How Sieve works <Info k="tier_routing" /></h1>
        <p className="mt-2 max-w-2xl text-fg-muted">Switch Explain mode in the header to see the same ten stages in plain or technical wording. Every number here is measured on the Evals page.</p>
      </div>
      <ol className="space-y-3">
        {stages.map((s, i) => (
          <li key={s.t} className="card flex gap-4">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-semibold text-accent-fg">{i + 1}</span>
            <div><h2 className="font-semibold">{s.t}</h2><p className="mt-1 text-fg-muted"><Explain plain={s.plain} technical={s.tech} /></p></div>
          </li>
        ))}
      </ol>
      <div className="card">
        <h2 className="font-semibold">Design rule</h2>
        <p className="mt-1 text-fg-muted">Models read and draft. Tables, rules and the citation verifier decide what reaches the technician. That is what lets us put a number on refusals instead of describing an architecture.</p>
      </div>
    </div>
  );
}

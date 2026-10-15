/** Every info button reads from here, so all explanatory copy is reviewable in one file. */
export type GlossaryEntry = { term: string; plain: string; technical?: string; refs?: { label: string; url: string }[] };

export const GLOSSARY = {
  bmet: {
    term: "Biomedical equipment technician",
    plain: "The person in a hospital who keeps medical machines working. In many low-income countries there is one for a whole district, or none at all.",
    technical: "WHO (2017): 68 percent of sub-Saharan countries report at most one biomedical engineer per million people; the United States reports 49 per million.",
    refs: [{ label: "WHO Human Resources for Medical Devices, 2017", url: "https://link.springer.com/article/10.1007/s10439-017-1897-2" }],
  },
  concentrator: {
    term: "Oxygen concentrator",
    plain: "A bedside machine that pulls oxygen out of room air for a patient to breathe. The most common life-support device in district hospitals.",
    technical: "Pressure-swing adsorption through two zeolite sieve beds alternately pressurised by a compressor. Typical purity 87 to 96 percent at 0.5 to 5 litres per minute; low-purity alarm at 82 percent per WHO 2015 specification.",
    refs: [{ label: "WHO Technical specifications for oxygen concentrators (2015)", url: "https://apps.who.int/iris/bitstream/handle/10665/199326/9789241509886_eng.pdf" }],
  },
  service_manual: {
    term: "Service manual",
    plain: "The manufacturer's repair book for one model: what each light means, how to test it, which part to replace. Hospitals rarely have it when the machine arrives.",
    technical: "Sieve indexes service manuals page by page. Every step it shows quotes a span that the citation verifier confirmed exists verbatim on that page. Manuals are indexed locally and never redistributed.",
  },
  support_label: {
    term: "Manual states this, or general practice",
    plain: "After the steps are written, a second fast model reads each step next to the manual sentence it cites. If the sentence says the same thing, the step is marked as stated by the manual. If the step goes further than the sentence, it is marked as general practice so you know the manual itself does not say it.",
    technical: "Nemotron 3 Nano, thinking off, one parallel call per step: YES if the cited sentences state the action. On ten fixed cases an independent Nemotron 3 Super judge agreed with 62.5 percent of steps labelled manual and 5 percent of steps labelled general. Citations point at numbered sentences, so every quote shown is the exact manual text.",
  },
  grounded: {
    term: "Grounded",
    plain: "Every instruction comes from a real page of the manual, and we show you the page. Nothing is made up.",
    technical: "Retrieval-augmented generation with a hard constraint: each step carries a verbatim quote plus document and page; a deterministic verifier rejects any step whose quote is not found on the cited page; an independent Nemotron 3 Ultra audit then checks the whole tree against the whole manual.",
  },
  safety_stop: {
    term: "Safety stop",
    plain: "A rule that fires before the AI is allowed to answer. For example, no oil near oxygen, no opening the cabinet while it is plugged in.",
    technical: "Deterministic YAML rules evaluated on the input and on every generated step. Actions: block, rewrite with a precondition, escalate, annotate. The language model never decides whether a gate fires. Measured in the negative-control eval.",
  },
  sieve_beds: {
    term: "Sieve beds",
    plain: "Two canisters of special sand inside the machine that trap nitrogen so oxygen comes out. They wear out, especially in humid climates, and are the most common reason for a persistent yellow light.",
    technical: "Zeolite molecular sieve columns. Exhaustion shows as purity 82 to 87 percent after warm-up with normal flow and clean filters; confirm with a calibrated oxygen analyser before replacing.",
  },
  purity: {
    term: "Oxygen purity",
    plain: "How much of what comes out is actually oxygen. Below about 82 percent, the machine warns you; below that the patient may not be getting enough.",
    technical: "Measured with a calibrated oxygen analyser at the outlet after the manufacturer's warm-up period. Alarm thresholds are model-specific and cited from the manual.",
  },
  tier_routing: {
    term: "Model tiers",
    plain: "Small fast models do the quick jobs, a bigger model writes the steps, and the biggest model double-checks everything against the whole manual.",
    technical: "Nemotron 3 Nano or 3.5 Lightning (fast, thinking off) for extraction and intake; Nemotron 3 Super for synthesis; Nemotron 3 Ultra with up to one million tokens of context as auditor. All via Nebius Token Factory. Every call is logged with tokens and cost in the Trace.",
  },
  trace: {
    term: "Trace",
    plain: "A list of every AI call made for your session, which model answered, and what it cost. So you can see exactly what happened.",
    technical: "Per-request ledger rows: tier, model id, purpose, tokens in and out, USD at list price, latency, auditor verdicts. Backed by SQLite; exposed at /v1/trace/{id}.",
  },
  recall: {
    term: "Recall check",
    plain: "Manufacturers sometimes recall a model for a known fault. Donated machines never receive that letter. Sieve checks the FDA's public database.",
    technical: "openFDA device/recall and device/event (MAUDE) snapshots, CC0 licence, matched by brand and model aliases. 647 oxygen-concentrator malfunction reports are also used as an external benchmark.",
    refs: [{ label: "openFDA device endpoints", url: "https://open.fda.gov/apis/device/event" }],
  },
  work_order: {
    term: "Work order",
    plain: "The repair record: what was wrong, what was done, which parts, whether it is fixed. It goes into the hospital's equipment log.",
    technical: "Schema aligned to WHO CMMS core fields (asset, model, serial, fault, actions, parts, outcome, downtime, technician). Exportable as CSV and PDF; feeds the fleet dashboard.",
  },
  byo: {
    term: "Bring your own manual",
    plain: "If we do not have the manual for your machine, upload it. It is indexed in your own workspace and nobody else sees it.",
    technical: "Workspace-scoped ingestion through the same pipeline; data never merged into the shared index; export and delete from settings.",
  },
  api_key: {
    term: "API key",
    plain: "A password-like code that lets your own software call Sieve.",
    technical: "Created in the dashboard, hashed at rest, scoped to a workspace with per-key rate limits. Also exposed as an MCP server so other agents can call Sieve as a tool.",
  },
  mcp: {
    term: "MCP",
    plain: "A standard way for AI assistants to use other tools. With it, your assistant can ask Sieve to identify a device.",
    technical: "Model Context Protocol server exposing identify, analyze and records as tools.",
  },
  training_mode: {
    term: "Training Mode",
    plain: "A simulated front panel of a real concentrator model. Pick a fault, watch the lights behave as the manual says, and practise the diagnosis. Always labelled as a simulator.",
    technical: "Client-side state machine driven by the registry's cited indicator table. Replaces a physical unit in the demo and gives trainee technicians unlimited practice faults.",
  },
  offline: {
    term: "Offline mode",
    plain: "No internet? Sieve still works on a laptop using an open Nemotron model, with the manuals already on the machine.",
    technical: "llama.cpp serving a 4-bit Nemotron 3 Nano; same prompts and schemas; deep-tier audit disabled; accuracy delta versus cloud published on the Evals page.",
  },
  benchmark: {
    term: "External benchmark",
    plain: "A test set we did not write ourselves, so the score means something.",
    technical: "Benchmark A: 300 held-out QA pairs from the INGENZI dataset (CC BY-NC 4.0). Benchmark B: 335 openFDA malfunction reports with a manufacturer evaluation (CC0). Baselines: Nano zero-shot and plain chunk-RAG without auditor.",
  },
  negative_control: {
    term: "Negative control",
    plain: "Things the system must refuse or flag. We count how often it gets them right, and publish the number.",
    technical: "Hazardous request set (target 100 percent blocked or escalated), out-of-corpus devices (target 100 percent 'no manual indexed'), benign set (target 0 percent false stops), citation integrity (target 100 percent).",
  },
} satisfies Record<string, GlossaryEntry>;

export type GlossaryKey = keyof typeof GLOSSARY;

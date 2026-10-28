/** One plain sentence per published number, for the i button on each tile. Keys match eval/results/latest.json. */
export const EVAL_HELP: Record<string, string> = {
  hazard_gated: "We wrote down dangerous requests, like putting oil on an oxygen machine or bypassing its alarm, and checked that the safety rules stop every one before any AI model sees it.",
  false_stops: "The opposite check: ordinary safe steps that the rules must not stop. Zero means Sieve does not cry wolf.",
  out_of_corpus: "Machines Sieve has no manual for. It must say it does not know them rather than guess, and it did.",
  retrieval_top5: "For each warning light in our registry, does searching the manuals bring back the exact page that explains it among the first five results?",
  citation_integrity: "Of all the manual quotes Sieve showed on real FDA complaints, the share found word for word on the page it cited.",
  cost_usd: "What this whole evaluation run cost in model calls, read from the call ledger.",
  bench_a_sieve: "Three hundred real repair questions from the closest earlier project's own dataset. An independent model graded Sieve's answers against the reference answers.",
  bench_a_chunk_rag: "The obvious alternative an engineer would build: the same model with plain search and no citation rules. Sieve beats it.",
  bench_a_zero_shot: "The same model answering from memory with no manuals at all. This is why manuals matter.",
  bench_a_citation: "How often the quote Sieve gave for an answer was really on the page it cited.",
  bench_a_second_judge: "The same answers graded again by a model from a different company, so the result does not rest on one judge.",
  bench_b_fire_stop: "Real FDA reports of concentrators that smoked, burned or caught fire. In every one, Sieve told the technician to take the machine out of service before showing any repair step.",
  bench_b_sieve: "On the same FDA reports, how often a Sieve hypothesis matched what the manufacturer later found by taking the machine apart. Hard for every system; we publish it anyway.",
  bench_b_citation: "Share of manual quotes on those FDA cases found on the page cited.",
  photo_identified: "Real photos of concentrators from resale listings, not our own. How often Sieve named the right machine, either on its own or among three choices for the technician.",
  photo_lookalikes: "Photos of machines Sieve has no manual for. It must not pretend to know them. It refused all of them and never opened the wrong manual.",
  cite_ab_resolve: "Instead of letting the model copy quotes, Sieve has it point at numbered manual sentences, and code copies the exact text. Every citation then lands on real text.",
  cite_ab_label: "Each step says whether the manual itself states it. An independent model agreed far more often with steps labelled as stated by the manual than with those labelled general practice.",
  photo_nano_vl: "The same 57 photos read by NVIDIA's open Nemotron Nano 12B VL alone, served on our own Nebius Serverless Endpoint. Strong on its own; Sieve adds a second independent model so it opens a manual only when both agree.",
  offline_citation: "The same pipeline on a laptop GPU with no internet, using a small NVIDIA model. Lower than the cloud, and we publish the gap.",
};

/** What the site features. Every number from every run stays in eval/results/latest.json. */
export const EVAL_HIDDEN = new Set<string>(["bench_b_sieve", "offline_citation"]);
export const EVAL_ORDER: string[] = [];
export const EVAL_NOTE: Record<string, string> = {
  bench_a_chunk_rag: "The obvious alternative: the same model with plain retrieval and no citation rules, on the same 300 questions.",
  bench_a_zero_shot: "The same model answering from memory, with no manuals.",
  photo_nano_vl: "NVIDIA Nemotron Nano 12B VL, served on our own Nebius Serverless Endpoint, read the same photos alone: 88.5% when the model name is legible, every look-alike refused, no wrong device ever selected.",
  cite_ab_resolve: "Sieve points at numbered manual sentences and code copies the exact text, so every citation lands on real text.",
};
export const SECTION_HIDDEN = ["Offline versus cloud"];
export const SECTION_COLUMNS: Record<string, string[]> = {
  "Benchmark B v2: openFDA malfunction reports (pre-registered)": ["mdr", "device", "fire_in_complaint", "sieve_stop_shown", "manufacturer_finding"],
};
export const SECTION_DESC: Record<string, string> = {
  "Benchmark B v2: openFDA malfunction reports (pre-registered)": "Real FDA reports of oxygen concentrators that smoked, burned or caught fire, selected and scored by rules committed before the run. In every one, Sieve took the machine out of service before showing a single repair step.",
  "Citation integrity on 20 openFDA complaints (live in every make eval)": "The first 20 FDA complaints for two brands, run through Sieve on every evaluation. Each quote is checked word for word against the page it cites.",
};

type Tile = { value: number | string | null; unit?: string; label: string; note?: string };
export function featured(summary: Record<string, Tile>): [string, Tile][] {
  const keys = Object.keys(summary).filter((k) => !EVAL_HIDDEN.has(k));
  keys.sort((a, b) => (EVAL_ORDER.includes(a) ? EVAL_ORDER.indexOf(a) : 99) - (EVAL_ORDER.includes(b) ? EVAL_ORDER.indexOf(b) : 99));
  return keys.map((k) => [k, { ...summary[k], note: EVAL_NOTE[k] ?? summary[k].note }]);
}

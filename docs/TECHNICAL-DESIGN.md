# Sieve: Technical Design

Shared platform decisions (client, router, vision, retrieval, rules engine, eval harness, API, UI kit) are in `../PLATFORM.md`. This document covers what is specific to Sieve.

---

## 1. What Sieve does, as a system

Input: a phone photo of a hospital device (nameplate, alarm panel, open chassis) plus a few taps of context. Output: a model identification, a manual-grounded troubleshooting tree with page citations and hard safety stops, a recall check, a Tavily parts lookup, and a filed work order that updates a fleet dashboard. Works online through Nebius Token Factory and offline through a quantised Nemotron 3 Nano on the technician's laptop or phone.

Scope for the hackathon: oxygen concentrators as the headline device class (Philips EverFlo, DeVilbiss 525 family, AirSep NewLife and VisionAire, Invacare Platinum, Nidek Nuvo, Longfian, Oxymed), then suction pumps and pulse oximeters as proof the pattern generalises. Everything else returns "no manual indexed for this device" and offers BYO upload.

---

## 2. Architecture

```
 Phone / laptop (PWA)
   |  photo + taps                                  Trace panel <-- cost ledger
   v
 apps/api (FastAPI)
   |-- 1 Identify ------> vision endpoint (Nemotron Nano VL on Nebius Serverless Endpoint)
   |                       fallback: Token Factory image2text -> fallback: manual fields
   |-- 2 Intake --------> Nemotron 3 Nano (Token Factory): asks at most 3 questions
   |-- 3 Retrieve ------> LanceDB hybrid search + nemotron rerank (device-scoped)
   |-- 4 Synthesise ----> Nemotron 3 Super: fault tree as a tool-call schema
   |-- 5 Gate ----------> rules engine (deterministic YAML)
   |-- 6 Audit ---------> Nemotron 3 Ultra (1M ctx): full manual + tree -> approve/repair/reject
   |                      citation verifier: exact-span match on cited pages
   |-- 7 Enrich --------> openFDA recall + MAUDE; Tavily parts and field-safety notices
   |-- 8 Record --------> work order (WHO CMMS-aligned JSON) -> fleet dashboard
   v
 Ingestion (Nebius Serverless Job): PDFs -> pages -> text + VL figure descriptions -> embeddings -> LanceDB
 Offline: llama.cpp + Nemotron 3 Nano GGUF + curated LanceDB subset + rules; same prompts, same schemas
```

---

## 3. Data layer

### 3.1 Corpus manifest (`data/manifest.yaml`)
Each entry: `id, title, device_class, manufacturer, model_aliases[], url, licence, redistributable (bool), sha256, pages`.

Sources and how they are handled:

| Source | Content | Licence handling |
|---|---|---|
| Frank's Hospital Workshop concentrator service and user manuals (about 100 docs, 60 service manuals) | Fault codes, LED tables, sieve bed and compressor procedures, wiring diagrams | Manufacturer copyright. Downloaded by the ingest script to the operator's own storage, indexed locally, never committed or redistributed. Citations show document title and page, and the UI links to Frank's original page. |
| EWH Troubleshooting Flowchart Handbook v6; Pulse Oximeter Repair; Malkin textbook | Generic flowcharts for power supplies, alarms, batteries, tubing | Fair-use library. Same handling as above. |
| WHO Technical specifications for oxygen concentrators (2015); WHO-UNICEF O2 devices (2019); WHO maintenance programme overview (2011) | Purity thresholds (82 percent alarm), maintenance schedules, inventory fields | WHO copyright or CC BY-NC-SA 3.0 IGO depending on year. Quoted with attribution. |
| openFDA device/event (MAUDE) and device/recall | 647 concentrator malfunction reports with manufacturer evaluations; recall records | CC0. Committed as a snapshot for the eval set. |
| Open Critical Care concentrator guide; OSMS O2 maintenance guide | Setup, filter cleaning, purity checks | CC BY-NC-SA. Quoted with attribution. |
| DeVilbiss LT-2023 service manual (Oxygen Alliance mirror) | Full 525 service procedures | Manufacturer copyright, publicly mirrored. Indexed locally. |

### 3.2 Device registry (`packages/core/devices.yaml`)
Hand-curated, cited, and the backbone of identification:

```yaml
- id: philips-everflo
  manufacturer: Philips Respironics
  model_aliases: ["EverFlo", "EverFlo Q", "1020000", "1020001"]
  nameplate_patterns: ["EverFlo", "REF 1020", "Respironics"]
  indicators:
    - {state: "yellow solid, silent", meaning: "low O2 purity below 90 percent (OPI units)", source: {doc: everflo-service, page: 12}}
    - {state: "yellow blinking", meaning: "high flow or flow restriction", source: {...}}
    - {state: "red solid, continuous alarm", meaning: "system fault, production stopped", source: {...}}
  common_faults: [sieve-bed-exhaustion, compressor-wear, inlet-filter-blocked, check-valve, control-board]
  consumables: [{part: "inlet filter", pn: "1038831"}, {part: "sieve beds", pn: "..."}]
  manuals: [everflo-service, everflo-user]
```

Fault concepts (`faults.yaml`) are shared across brands: `sieve-bed-exhaustion` has symptoms (yellow light after 15 minutes warm-up, purity 82 to 87 percent on analyser, high cycling pressures), checks (inlet filter, tubing kinks, ventilation clearance, cannula length), confirmations (O2 analyser reading), and resolution (replace sieve beds; part numbers by brand). Each field carries a citation to a page in the manifest.

### 3.3 Index
LanceDB table `pages`: `doc_id, page, text, figure_desc, embedding_text, embedding_page_image, device_ids[], licence, redistributable`. Device scoping means a query about an EverFlo never retrieves a Nuvo page unless the device is unknown, in which case `faults.yaml` generic checks lead.

### 3.4 Ingestion job (`infra/job-ingest`)
Container: Python 3.12, PyMuPDF, vLLM for `nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL` (figure and table description per page), `nvidia/llama-nemotron-embed-vl-1b-v2` for page-image embeddings, BM25 build. Command:

```
nebius ai job create --name sieve-ingest \
  --image ghcr.io/<org>/sieve-ingest:latest \
  --platform gpu-l40s-a --preset 1gpu-8vcpu-32gb --timeout 3h \
  --env MANIFEST_URL=... --env OUTPUT_BUCKET=...
```

Output: LanceDB directory plus `ingest_report.json` (pages, figures described, tokens, GPU minutes, cost). The report is shown on the `/evals` page under "Ingestion", because judges asked for cost transparency in past Nebius events.

Fallback if Nebius AI Cloud credits are not available: `make ingest-local` runs the same container locally or on a rented GPU; Token Factory remains the runtime dependency.

---

## 4. The agent flow in detail

### Step 1: Identify
- Vision prompt asks for structured fields only: `manufacturer, model, ref, serial, visible_indicators[] (colour, state, label), visible_text[], device_type_guess`.
- Matcher in `packages/core`: exact REF or model alias match first, then fuzzy on manufacturer plus type, returns `device_id, confidence`. Below 0.6 confidence the UI shows the top three candidates with thumbnails and asks the technician to confirm. Unknown devices go to the generic flowchart path and a BYO prompt.

### Step 2: Intake (Nano, thinking off)
- Given device and indicators, Nano picks at most three questions from a fixed question bank (`intake.yaml`): "Does the yellow light persist after 15 minutes?", "Is a cannula or humidifier connected?", "Do you have an oxygen analyser?". The bank is finite so the UI can render each question with an info button explaining why it matters.

### Step 3: Retrieve
- Query = device id + indicator meanings + answers. Hybrid search over device-scoped pages, rerank to top 8, pass page text plus figure descriptions.

### Step 4: Synthesise (Super)
Tool-call schema `FaultTree`:
```json
{
 "device_id": "philips-everflo",
 "hypotheses": [{"fault_id": "sieve-bed-exhaustion", "likelihood": "high", "why": "...", "cite": {"doc":"everflo-service","page":34,"quote":"..."}}],
 "steps": [
   {"id": 1, "action": "...", "expected": "...", "if_yes": 2, "if_no": 5,
    "tools_needed": ["O2 analyser"], "duration_min": 5, "safety_class": "none|caution|stop",
    "cite": {"doc": "...", "page": 0, "quote": "verbatim span"}}
 ],
 "parts_candidates": [{"name": "sieve bed pair", "pn": "525D-619", "cite": {...}}],
 "escalate_if": ["purity remains below 82 percent after sieve replacement"]
}
```
Every step must carry a verbatim quote from a retrieved page. Steps with `safety_class: stop` are rendered as a full-width stop card.

### Step 5: Gate (rules engine)
Sieve-specific rules (excerpt of `rules/sieve.yaml`):
- `oxygen-oil-grease`: any step mentioning lubricant near oxygen path -> block and show the WHO and manufacturer warning.
- `open-while-running`: step implying chassis open with mains connected -> rewrite to "switch off and unplug first", annotate.
- `purity-alarm-bypass`: any suggestion to defeat or ignore the purity alarm -> block.
- `patient-first`: if the device is in use, prepend "move the patient to a backup supply before servicing" (cites WHO-UNICEF 2019).
- `mains-live-testing`, `capacitor-discharge`, `swollen-battery`: escalate to senior BMET or manufacturer.
- `no-manual-no-guess`: if retrieval confidence is low and device is unknown, only generic flowchart steps are allowed; no part numbers.

### Step 6: Audit (Ultra) and citation verification
- Ultra receives the entire service manual text (typically 60 to 200 pages, well inside 1M context), the fault tree, and the instruction: "For each step, confirm the cited quote supports the action, flag contradictions with any page of the manual, and return approve, repair or reject per step." Thinking on, budget 8K.
- Deterministic verifier: each `quote` must appear verbatim (whitespace-normalised) in the cited page text. Any miss is a hard failure and the step is replaced with "see page N" plus the page image.
- Metrics from this stage feed the eval: citation integrity percent, auditor repair rate.

### Step 7: Enrich
- openFDA: `device/recall` by brand and model; `device/event` count and top product problems for the model. Shown as "Recalls and known problems" with the FDA source link.
- Tavily: `search` for `"<model>" service manual pdf` when the corpus lacks one (offer BYO ingestion of the result), and `search` plus `extract` for `"<part number>" price` restricted to supplier domains to show availability and indicative price. Tavily calls are logged in the Trace and are the project's Best Use of Tavily claim.

### Step 8: Record
Work order schema aligned to WHO CMMS core fields: `asset_id, facility, device_id, serial, reported_fault, indicators, steps_performed[], parts_used[], outcome (fixed | needs_part | escalated | decommissioned), downtime_hours, technician, timestamps, cost_estimate, attachments (photos), ai_trace_id`. Stored per workspace; exportable as CSV and as a printable PDF; dashboard shows functional percent by facility, mean time between failures by brand, open work orders, parts demand.

---

## 4b. Training Mode (device simulator)

A client-side simulator in `apps/web/sim/`: SVG front panels for EverFlo and DeVilbiss 525 traced from the manuals' panel figures; a fault state machine whose indicator behaviour (light colour, blink pattern, alarm cadence, flow meter reading) is taken from the LED tables in `devices.yaml`, each state citing its manual page. Controls: pick a device, pick a visible or hidden fault, run, Send to Sieve (posts a rendered panel image plus the nameplate photo to `/v1/identify`). A persistent Simulator badge is rendered into every frame so no screenshot can be mistaken for hardware. Purpose: the demo without hardware, and a training surface for new technicians to practise twenty faults in an afternoon.

## 5. Offline mode

- `make offline` downloads Nemotron 3 Nano 30B-A3B GGUF Q4_K_M (about 17 GB, 3.5B active parameters) and starts llama.cpp's OpenAI-compatible server on localhost; the API's router points fast and mid tiers at it and disables the deep tier.
- The curated LanceDB subset (concentrators, suction, oximeters) and rules ship in the PWA offline bundle; the service worker caches the app shell.
- Vision offline: manual field entry plus the indicator picker (choose the light pattern from thumbnails). This is honest: a 12B VL model does not fit on a field laptop today, and the UI says so.
- Eval reports the offline-vs-cloud delta on the same question set as a measured limit.

---

## 6. Evaluation (project-specific)

| Metric | Set | Source | What is reported |
|---|---|---|---|
| Benchmark A | INGENZI_DatasetV1 held-out 300 QA (error codes and procedures, MRI and ultrasound manuals) | HF dataset, CC BY-NC 4.0 | Exact and judge-scored accuracy; Sieve vs chunk-RAG vs nano-zero-shot vs INGENZI's reported 100 percent and 80 percent |
| Benchmark B | 150 openFDA MAUDE concentrator malfunction narratives with a manufacturer evaluation | CC0 | Top-1 and top-3 agreement between Sieve's hypotheses and the manufacturer's finding, scored by a blinded Ultra judge with a published rubric and a 30-item human-checked subset |
| Negative control 1 | 50 hazardous requests (open running unit, oil the compressor, bypass alarm, test live mains) | Authored, published | Percent blocked or escalated: target 100 |
| Negative control 2 | 30 out-of-corpus devices | Authored, published | Percent answered with "no manual indexed" instead of invented steps: target 100 |
| Negative control 3 | 30 benign requests | Authored, published | False stop rate: target 0 |
| Citation integrity | All generated steps across A and B | Verifier | Percent of quotes found verbatim on cited pages: target 100 |
| Offline delta | 100 questions from A and B | Same | Accuracy offline Nano vs cloud routed |
| Cost | All runs | Ledger | USD per session, per tier |

Baselines are run with the same prompts and the same retrieved pages so the comparison is fair.

---

## 7. Security, privacy, operations

- API keys hashed (argon2); per-workspace isolation for BYO data and records; export and delete in settings.
- Photos stored only in the workspace; EXIF stripped; no third-party analytics.
- Secrets only in environment; CI runs a secret scanner and `make eval` smoke on every push.
- Health endpoint reports vision endpoint status, Token Factory reachability, index version, rules version; the UI status strip reads it.
- Logging: structured JSON; the Trace panel is a filtered view of the same records.

---

## 8. Cost estimate for the hackathon

| Item | Estimate |
|---|---|
| Ingestion job, L40S, about 3 hours | about $5 |
| Vision endpoint, L40S, about 25 hours across dev, video and judging | about $35 |
| Token Factory: development plus full eval runs (Ultra audits dominate) | $15 to $30 |
| Tavily | free tier, 1,000 credits |
| Hardware | none |

Published in README as actuals after the eval run.

---

## 9. Risks and mitigations (technical)

| Risk | Mitigation |
|---|---|
| Vision endpoint cold or down during judging | Fallback chain to Token Factory image2text then manual fields; sample gallery has pre-extracted fields; status strip is honest about mode |
| Nebius AI Cloud credits unavailable | Local ingestion; Token Factory remains the required runtime; design unchanged |
| Hallucinated steps | Verbatim-quote requirement, deterministic verifier, Ultra auditor, rules engine; "see page N" fallback |
| Corpus takedown | Nothing redistributed; index rebuildable from manifest; UI links to original sources |
| OCR on worn nameplates | Confidence threshold with candidate picker; serial and REF patterns per brand |
| Scope creep | Device classes fixed at three; unknown devices go to generic flowcharts and BYO |

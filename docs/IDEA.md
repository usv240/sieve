# SIEVE: Project 1 (LOCKED 2026-10-13)

Offline repair copilot for biomedical technicians in low-resource hospitals. Oxygen-concentrator-first, then suction pumps and pulse oximeters.

Hackathon: Nebius x NVIDIA Global AI Hackathon (nebiusglobalaihackathon.devpost.com). Deadline **Oct 30 2026, 10:00 PDT = 22:30 IST**. Track: **Best Apps & Agents**. Bonus: **Best Use of Tavily**.

Full research, citations, competitor list and alternatives: see `IDEA-RESEARCH.md`.

---

## One line
A technician photographs a dead oxygen concentrator; Sieve identifies the model, walks them through the service manual's fault tree with hard-coded safety stops, checks FDA recalls, and files the repair record into the hospital's log. Runs on open NVIDIA Nemotron models via Nebius Token Factory, with an offline mode.

## Tagline (two verified numbers)
"72% of broken hospital equipment in low-income countries can be fixed without imported parts, but two-thirds of sub-Saharan countries have at most one biomedical engineer per million people. Sieve puts that engineer in the technician's phone, offline."

## Why it wins (judge's eye)
- Specific person + specific object + visceral stakes (child needs oxygen, machine is dead, no engineer within 500 km).
- Numbers tell the story: the gap is knowledge, not parts; AI transfers knowledge.
- Photo in, action out. A product, not a chatbot.
- Physical demo: a real concentrator on the table with a real alarm light.
- Neglected open corpus already exists (thousands of service manuals, EWH flowcharts, WHO specs).
- Zero collision: none of ~200 public entries in this hackathon touch hospital equipment; not on any LLM cliché list.
- Uses every sponsor primitive for a real reason (see stack table).

## Impact evidence (primary sources only)
| Fact | Source |
|---|---|
| 38.3% of 112,040 devices across 16 LMICs out of service | Perry & Malkin 2011, https://pubmed.ncbi.nlm.nih.gov/21597999/ |
| 72% of 2,849 repair requests (60 hospitals, 11 countries) fixed WITHOUT imported parts; 66% using only 107 basic skills | Malkin & Keane 2010, https://link.springer.com/article/10.1007/s11517-010-0630-1 |
| 68% of sub-Saharan countries have at most 1 biomedical engineer per million (US: 49) | WHO HRMD 2017, https://link.springer.com/article/10.1007/s10439-017-1897-2 |
| >5 billion people lack safe medical oxygen; only 30% of acute LMIC patients needing O2 get it | Lancet Global Health Commission, Feb 2025, https://www.thelancet.com/journals/langlo/article/PIIS2214-109X(24)00496-0/fulltext |
| Functional concentrator at only 66.7% of primary facilities (39 countries, 2,884 facilities) | https://pmc.ncbi.nlm.nih.gov/articles/PMC11954661/ |
| Nigeria: 2 of 57 concentrators (3.5%) fit for use | https://pmc.ncbi.nlm.nih.gov/articles/PMC12581006/ |
| Malawi OpenO2: 649 concentrators returned to service, doubling the functional fleet; most faults trivial | https://www.openo2.org/concentrator-graveyard |
| Gambia: most concentrator faults fixed in under a day for under $10 | BMC HSR 2025, https://pmc.ncbi.nlm.nih.gov/articles/PMC11776221/ |
| NEST360, 63 hospitals: median 1 engineer + 1 technician per hospital; downtime never measured | JOGH 2026, https://jogh.org/2026/jogh-16-04270 |
| Kenya: 32% of O2 patients interrupted by outages, 19% case fatality among them | PMC11776221 |

Do NOT claim: "WHO says 70% of donated equipment never works" (anecdotal); any India-wide broken-concentrator percentage (none exists); "26 topics" (it is 107 skills).

## Prior art (name in README, beat measurably)
- INGENZI Tech, arXiv 2601.16967 (MICCAI 2025 workshop): text-only RAG over one ultrasound manual, GPT-3.5, calls OpenAI despite "offline" claim, no baseline, no code. Public dataset INGENZI_DatasetV1 (10,294 QA, CC BY-NC 4.0): https://huggingface.co/datasets/BernesLy/INGENZI_DatasetV1
- Jua, Devpost CSYA Hacks 2023 (GPT-3.5 paper-qa): https://devpost.com/software/jua
- TRIMEDX-AIQ, GE HealthCare internal agent, PartsSource PRO, BiomedRx: US enterprise, closed.
- iFixit FixBot: consumer devices only.
None ship: photo-first input, real offline, non-imaging life-support devices, hard-coded safety gates, recall check, structured repair log / fleet view.

## Corpus (index locally, cite page numbers, never redistribute PDFs)
- Frank's Hospital Workshop: ~100 oxygen-concentrator docs (~60 service manuals: Philips EverFlo, DeVilbiss 525/515/505, AirSep NewLife/VisionAire, Invacare Platinum, Nidek Nuvo, Longfian, Oxymat, Inogen), 69 suction, 220 pulse oximeter, Zambia BMET lecture notes. HTTP only. http://www.frankshospitalworkshop.com/equipment/oxygen_concentrators_service_manuals.html
- EWH BMET Library: Troubleshooting Flowchart Handbook v6, Pulse Oximeter Repair, Malkin textbook. https://bmet.ewh.org/handle/20.500.12091/79
- WHO Technical specifications for oxygen concentrators (2015): https://apps.who.int/iris/bitstream/handle/10665/199326/9789241509886_eng.pdf
- openFDA MAUDE device/event (CC0): 647 oxygen-concentrator malfunction reports with manufacturer evaluations. https://open.fda.gov/apis/device/event ; recalls: https://open.fda.gov/apis/device/recall/
- DeVilbiss 525 service manual LT-2023: https://www.oxygenalliance.org/wp-content/uploads/2022/03/LT-2023-Rev-N.pdf
- Open Critical Care concentrator guide (CC BY-NC-SA): https://opencriticalcare.org/resources/oxygen-concentrator-setup-and-maintenance/

## Stack (verified Oct 13 2026)
Token Factory base URLs: `https://api.tokenfactory.nebius.com/v1/` (Nano, Lightning) and `https://api.tokenfactory.us-central1.nebius.com/v1/` (Super, Ultra). Reasoning off: `extra_body={"chat_template_kwargs":{"enable_thinking":False}}`. Nemotron has no JSON-mode tag: use tool calling for schemas.

| Component | Model / service | Reason |
|---|---|---|
| Intake, fault classification, log extraction | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` or `nvidia/Nemotron-3_5-Lightning` ($0.06/$0.24) | Many cheap calls per session |
| Fault-tree synthesis with page citations | `nvidia/nemotron-3-super-120b-a12b` ($0.30/$0.90) | Mid reasoning over retrieved pages |
| Senior engineer + independent auditor | `nvidia/Nemotron-3-Ultra-550b-a55b` ($1/$3, 1M ctx) | Whole manual in context; audits every step before display |
| Nameplate / LED / board photo | `nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL` on vLLM, Nebius Serverless Endpoint (L40S) | No NVIDIA vision on TF. Fallback: TF image2text (Qwen3.8-27B) |
| Manual ingestion | Nebius Serverless Job: `nvidia/llama-nemotron-embed-vl-1b-v2` + `nvidia/llama-nemotron-rerank-vl-1b-v2` | Page-image embeddings handle wiring diagrams; real GPU batch job |
| Offline mode | Nemotron 3 Nano Q4 via llama.cpp on laptop + local index | Hospitals lose internet; measured as a limit |
| Live lookups | Tavily search/extract (manual by model number, field-safety notices, spare-part prices) | Runtime call -> Tavily bonus |
| Recall check | openFDA device/recall + MAUDE | Donated devices never get recall notices |
| Safety gates | Hard-coded rules, NOT the LLM: O2 + oil/grease, opening a running unit, bypassing purity alarm, mains-live testing, capacitors, swollen Li-ion -> STOP + escalate | Negative-control headline |
| Output artifact | WHO CMMS-style work order (JSON/CSV) + fleet dashboard | Loop closes into hospital records |

## Evaluation (the two numbers + negative control)
1. External A: INGENZI_DatasetV1 held-out subset. Sieve vs plain-RAG vs INGENZI's reported 100%/80%.
2. External B: openFDA MAUDE concentrator narratives. Top-1/top-3 diagnosis match vs manufacturer finding.
3. Negative control (headline): 100% of hazardous requests blocked; "no manual, won't guess" rate on out-of-corpus devices; zero hallucinated page citations (every citation verified).
4. Named baselines: Nano without retrieval; chunk-RAG without auditor.
5. Measured limits: offline Nano vs cloud Ultra; photo-ID accuracy on worn nameplates.
6. Real run: the physical concentrator, live.

## Demo (3:00)
0:00 problem, two numbers -> 0:25 photo of yellow LED + nameplate on real unit, model identified -> 0:50 triage questions, fault tree with page citations, say "Nemotron 3 Super on Nebius Token Factory" aloud -> 1:30 safety stop (ask to open running unit, hard refusal) -> 1:50 openFDA recall + Tavily part lookup -> 2:10 repair logged, dashboard updates -> 2:30 Serverless Job pages ingested + eval table -> 2:50 offline laptop mode, close.

## 17-day plan (IST)
- Oct 13–14: credits (NEBIUS-DEVPOST-GLOBAL26 + Builders Program), repo + Apache-2.0, corpus download, openFDA pull, order used concentrator (Rs 15–30k, IndiaMART), email BMETs / local hospital biomedical dept for a quote.
- Oct 15–17: ingestion Job, retrieval + Super tree agent, hard-coded safety layer, eval harness v0.
- Oct 18–20: VL endpoint, device ID, Ultra auditor, openFDA + Tavily tools, work order + dashboard.
- Oct 21–23: mobile-first PWA, offline mode, fallbacks.
- Oct 24–25: final evals, baselines, negative control, limits table, README with prior-art section.
- Oct 26–27: video, Devpost text, required tool-feedback section, hosted demo.
- Oct 28–29: buffer, submit Oct 29.

## Risks
1. Prior-art optics: name INGENZI and Jua, beat them on their own dataset, ship what they lack.
2. Corpus legality: local index only, page citations, CC0/WHO for anything redistributed.
3. Safety liability: deterministic gates + auditor; "stops and escalates" is the product guarantee.
4. Nebius AI Cloud credits may need a card: fallback is local/Colab ingestion; TF runtime call remains the hard requirement.
5. Hardware: a dead unit is fine. Fallback: LED tables from manuals + iFixit DeVilbiss 525 photos.

## Open decisions (owner: Ujwal)
- Hardware: none. Training Mode simulator replaces the physical unit (decided 2026-10-13).
- Team entry; Ujwal is the only coder.
- Final name: Sieve / Workshop / O2Keeper.

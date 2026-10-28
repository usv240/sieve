# Sieve

[![ci](https://github.com/usv240/sieve/actions/workflows/ci.yml/badge.svg)](https://github.com/usv240/sieve/actions/workflows/ci.yml) [![licence](https://img.shields.io/badge/licence-Apache--2.0-blue)](LICENSE)

**Photographs a dead oxygen concentrator, finds the manual page, walks the fix with safety stops, checks recalls, and files the work order. Offline-capable.**

Built for the Nebius x NVIDIA Global AI Hackathon on **Nebius Token Factory** with **NVIDIA Nemotron 3 Nano, Super, Ultra, 3.5 Lightning and 3.5 Super VL**. Apache-2.0.

> Benchmark A: 69.7 percent on the closest prior work's own dataset, versus 62.0 percent for the obvious baseline and 17.0 percent zero-shot, two independent judges agreeing (kappa 0.94), with every Sieve answer cited and verified.
>
> At Chintheche Health Center in Malawi, four oxygen concentrators sat broken for four years; a repair team had all four running again in a few hours (OpenO2). Replacing them would have cost $2,000 to $6,400 before shipping, at UNICEF's $500 to $1,600 per concentrator ex-works. Sieve is built to make that repair the default.
>
> 72 percent of broken hospital equipment in low-income countries was fixed without any imported parts (Malkin and Keane, 2010). Two-thirds of sub-Saharan countries have at most one biomedical engineer per million people (WHO, 2017). The gap is knowledge. Sieve puts that knowledge, the manufacturer's own service manual, in the technician's phone.

## Live

Entered in the Physical AI track: an edge agent that reads a physical machine through the camera, runs on the device without internet, and directs the technician's hands one check at a time.

Web: https://sieve-kappa.vercel.app. API: https://sieve-api.vercel.app (OpenAPI docs at `/docs`). Both run on Vercel's free plan; the API is a Python function with a 300 second budget, enough for the Nemotron 3 Ultra audit.

## Status

Working scaffold with a real index and a real evaluation. Model-dependent stages run once a Token Factory key is present.

| Area | State |
|---|---|
| Corpus | 167 manuals, 9,462 pages indexed locally (oxygen concentrators 75, pulse oximeters 68, suction pumps 24). Manuals are not redistributed; `make fetch-corpus` rebuilds the index from `data/manifest.yaml`. |
| Registry | Philips EverFlo and DeVilbiss 525 indicator tables, every entry cited to a verified manual page. Six more concentrator models identified and retrievable. |
| Safety rules | 8 deterministic rules (oil near oxygen, open while plugged in, purity-alarm bypass, patient first, live mains, capacitors, swollen battery, no-manual-no-guess). |
| Pipeline | Identify, intake, device-scoped retrieval, Nemotron 3 Super synthesis with verbatim citations, deterministic citation verifier, rules gate, Nemotron 3 Ultra whole-manual audit, openFDA recalls, work order. |
| Web | Next.js app: landing that teaches the domain, Try flow with a Training Mode simulator, fleet, evals, how it works, API, scope and safeguards, references. Light and dark, phone and desktop, info buttons on every term. |
| Eval (no key) | Hazardous requests gated 20/20, false stops 0/10, unknown devices refused 10/10, cited page retrieved in top 5 for 10/10 indicators. See `eval/results/`. |
| Eval (with key, 2026-10-14) | **Benchmark A, the competitor's own dataset (INGENZI, 300 held-out questions, blind Nemotron 3 Super judge): Sieve 69.7 percent, plain retrieval baseline 62.0 percent, Nano zero-shot 17.0 percent.** A second, independent judge (DeepSeek-V4.1-Flash) grading the same stored answers gives 66.0, 52.4 and 2.5 percent, with Cohen's kappa 0.94 between judges on Sieve answers. Sieve is the only system whose answers carry a verified citation (80.7 percent of its quotes found on the cited page). **Benchmark B, 74 real openFDA malfunction reports, pre-registered in `eval/PREREG-benchmark-b.md`:** Sieve took the unit out of service on all 62 reports describing smoke, fire, burning or heat. Sieve citation integrity on Benchmark B: 94.7 percent. **Real-world photos:** 57 photos from resale listings and product pages, annotated by eye before any run. Two vision models read each photo, NVIDIA Nemotron 3.5 Super VL and a second model, and Sieve picks a device on its own only when both agree. It identified 82.9 percent of covered concentrators and 100 percent of those whose model name is legible, refused all 16 look-alike devices it has no manual for, and never auto-selected a wrong device. **Citations:** Sieve now cites by pointing at numbered manual sentences instead of copying them; on the same ten cases 100 percent of citations resolve against 88.8 percent for copied quotes. Each step carries a label saying whether the manual states it; an independent judge agreed with 62.5 percent of steps labelled as stated, against 5 percent of steps labelled general practice. |

## Validated against real-world evidence

- **Missing service manuals predict broken equipment.** Across public hospitals in Amhara, Ethiopia, equipment without a service manual was 55 percent less likely to be functional (adjusted odds ratio 0.45); the service manual and technician training were the key determinants of functionality (Sewagegn et al., Discover Health Systems 2025, https://link.springer.com/article/10.1007/s44250-025-00312-9). Sieve puts the right manual page in front of the technician.
- **Concentrators fail, and skills are the reason given.** Of 57 oxygen concentrators tested in secondary hospitals in southwest Nigeria, 2 were fit for use; no concentrator had a clean external filter, and staff listed lack of maintenance knowledge and of technician training among the causes (Bakare, Graham et al., International Health 2020, https://pmc.ncbi.nlm.nih.gov/articles/PMC6964224/).
- **The person with the know-how doubles uptime.** Rural Nepali hospitals without a biomedical technician had twice the share of non-functional devices of those with one, 14 versus 7 percent (Thapa et al., Human Resources for Health 2022, https://pmc.ncbi.nlm.nih.gov/articles/PMC8895523/).
- **A working concentrator saves lives.** When hospitals in Papua New Guinea gained working oxygen systems, the risk of death for children with pneumonia fell by 35 percent (Duke et al., Lancet 2008, https://pubmed.ncbi.nlm.nih.gov/18708248/). Worldwide, only 30 percent of the 299 million people in low- and middle-income countries who need oxygen receive it, and technical surveys found most hospital concentrators in sub-Saharan Africa and south Asia not functioning (Lancet Global Health Commission on medical oxygen security, 2025, https://pmc.ncbi.nlm.nih.gov/articles/PMC11865010/).
- **Step-by-step structure changes outcomes.** A 19-item checklist cut surgical deaths from 1.5 to 0.8 percent across eight hospitals in eight cities, from Seattle to Ifakara in Tanzania (Haynes et al., NEJM 2009, https://pubmed.ncbi.nlm.nih.gov/19144931/). Sieve brings the same discipline to repair: one check at a time, each from the manual.
- **The oil stop is industry standard.** "Oil and grease are particularly hazardous in the presence of oxygen as they can ignite extremely easily and burn with explosive violence" (European Industrial Gases Association, Doc 04/26, https://www.eiga.eu/uploads/documents/DOC004.pdf). Sieve blocks any lubricant near the oxygen path before a model replies.

## Where the models run

| Stage | Model | Platform |
|---|---|---|
| Extraction, intake, drafting | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`, `nvidia/Nemotron-3_5-Lightning` | Nebius Token Factory (EU) |
| Fault-tree synthesis | `nvidia/nemotron-3-super-120b-a12b` | Nebius Token Factory (US) |
| Whole-manual audit | `nvidia/Nemotron-3-Ultra-550b-a55b` (1M context) | Nebius Token Factory (US) |
| Nameplate and panel reading | `nvidia/Nemotron-3.5-Super-VL`, cross-checked by an independent second read (`openbmb/MiniCPM-V-4_5`); a device is auto-selected only when both agree. Offline: `NVIDIA-Nemotron-Nano-12B-v2-VL` via llama.cpp | Nebius Token Factory; laptop GPU offline |
| Offline diagnosis (no internet) | `NVIDIA-Nemotron-Nano-9B-v2` 4-bit via llama.cpp (`scripts/offline.ps1`, port 8090) | Laptop RTX 4070, 8 GB. Re-verified 2026-10-28 with every cloud key removed: a full EverFlo low-oxygen diagnosis in 61 s, steps cited to pages 24 and 90 of the service manual |
| Hybrid retrieval | `Qwen/Qwen3-Embedding-8B` embeddings over 2,994 concentrator pages, fused with BM25 | Nebius Token Factory; embedded in 352 s |
| Corpus ingestion | PyMuPDF plus Tavily extract for web-sourced manuals | Laptop (33 s). Serverless Job manifest in `infra/job-ingest`; the verification Job in `infra/job-verify` ran on AI Cloud |
| Live lookups and manual discovery | Tavily search, extract, map | Tavily API. When a known device has no manual, Sieve finds one, extracts it, indexes it and retrieves from it in the same request |
| Agent surfaces | MCP server with 8 tools (`apps/mcp`); Hermes Agent on Nemotron 3 Super via Token Factory (`infra/hermes`); OpenShell sandbox with brokered credentials (`infra/openshell`) | All verified: MCP over stdio; Hermes calling Sieve tools; a full diagnosis (Super, Ultra audit, Tavily) executed inside an OpenShell sandbox that holds only credential placeholders and can reach nothing but four hosts |
| Recalls and known problems | openFDA device/recall and MAUDE (CC0) | snapshot in `data/external` |

Every call is written to a ledger (tier, model, tokens, USD, latency) and shown in the app's Trace panel.

## Nebius Serverless, run and stopped

- **Job: verify both entries from a clean machine.** A Serverless Job cloned both public repositories, ran every test and the published safety checks, and called both live APIs. Result PASS in about 3 minutes (`sieve/infra/job-verify/RUN.md`).
- **Endpoint: an open NVIDIA vision model on our own GPU.** A Serverless Endpoint served NVIDIA Nemotron Nano 12B v2 VL with vLLM on one L40S, and both photo benchmarks were rerun with it as the only reader. It read 92.9 percent of legible Indian pesticide labels correctly on its own, and showed why Antidote pairs two independent reads with a brand check: together they give 0 unsafe cards in 68 (`sieve/infra/endpoint-vl/RUN.md`). Stopped after the run; about $1 in total.

## Where Token Factory accelerated our workflow

- **Five NVIDIA models behind one key and one API shape.** Nemotron 3 Nano, 3.5 Lightning, 3 Super, 3 Ultra and 3.5 Super VL all answer the same OpenAI-compatible call. Moving a pipeline stage to a different tier is a one-line change in the router, which is how we tuned cost and speed per stage instead of picking one model for everything.
- **A one-million-token auditor without a GPU.** Nemotron 3 Ultra reads an entire service manual in a single call. Running a 550B model ourselves was out of reach for a laptop team.
- **Long context as a feature, not a workaround.** The weekly fleet brief sends 140,000 tokens (the whole fleet log, 647 FDA reports and 34 recalls) to Nemotron 3.5 Lightning in one call, at about one cent.
- **Evaluation at a scale we could afford.** Benchmark A graded 300 questions across three systems with two judges for $0.65. Every benchmark in this repo was rerun several times during development because each run cost cents.
- **A vision model appeared mid-hackathon and we switched in a day.** Nemotron 3.5 Super VL arrived in the catalog; adopting it was a model id and one request flag, and it became our first photo reader.
- **Embeddings from the same account.** Qwen3-Embedding-8B on Token Factory embedded the 2,994 oxygen concentrator pages in 352 seconds; full-text search covers all 9,462, so retrieval, generation and audit share one bill and one ledger.

## Screenshots

Light and dark, same page: `docs/screenshots/landing-light.jpg`, `docs/screenshots/landing-dark.jpg`. Live fix with citations and Trace: `docs/screenshots/try-fix-dark.jpg`. Evals page: `docs/screenshots/evals-light.jpg`.

## Ecosystem, verified

- **MCP**: `apps/mcp/sieve_mcp.py` exposes list_devices, identify_device, identify_from_photo, analyze_fault, read_manual_page, file_work_order. Any MCP client can drive a full diagnosis.
- **Hermes Agent**: with the config in `infra/hermes`, `hermes -z "DeVilbiss 525, red light beeping. Use the sieve tools."` makes Nemotron 3 Super on Nebius call identify_device and analyze_fault and answer with the cited page. Hermes also bridges WhatsApp and Telegram, which is how field staff actually communicate.
- **OpenShell**: demonstrated on WSL2 plus Docker Desktop. Deny-by-default proven (EACCES at the kernel), four hosts allowed by policy, Nebius and Tavily credentials brokered so the sandbox only ever sees placeholders, and a full diagnosis run inside. Transcript and lessons in `infra/openshell/DEMONSTRATED.md`; reproduce with `infra/openshell/run.sh`.
- **NemoClaw**: installed with the Hermes agent and onboarded onto Nemotron 3 Super through Token Factory. The sandboxed agent sees only a placeholder key and cannot reach the open web. Record in `infra/nemoclaw/DEMONSTRATED.md`.
- **Tavily**: search, extract and map are runtime calls, logged in the Trace next to the model calls.

## Quick start

```
git clone https://github.com/usv240/sieve && cd sieve
cp .env.example .env            # add NEBIUS_API_KEY and TAVILY_API_KEY
make setup                      # uv sync + import paths
make fetch-corpus               # downloads manuals to data/corpus (gitignored)
make ingest                     # builds data/index/sieve.db in about 30 seconds
make test                       # 37 tests
make eval                       # writes eval/results/latest.json and REPORT.md
make dev                        # API on :8000, OpenAPI at /docs
cd apps/web && npm install && npm run dev   # web on :3000
```

Without a key the app runs in replay mode: identification, retrieval, rules and recalls work; synthesis and audit wait for Token Factory.

## Design rule

Models read and draft. The registry, the rules engine and the citation verifier decide what reaches the technician. Every step carries a verbatim quote from a cited manual page; a step whose quote is not found on that page is replaced by the page itself. That is what lets us publish a refusal rate instead of describing an architecture.

## Prior art, named

INGENZI Tech (arXiv 2601.16967) built a text chatbot over one ultrasound manual with a closed model; Jua (Devpost 2023) did document Q&A. Sieve adds photo-first identification, a cited indicator registry, deterministic safety gates, an independent whole-manual audit, recall checks, a work order and fleet view, offline mode, Training Mode, and an external evaluation with baselines, including on INGENZI's own published dataset.

## Documents

- [EVIDENCE.md](EVIDENCE.md): every published number, its raw output file, and the command that reruns it.

`docs/IDEA.md`, `docs/PLAN.md`, `docs/TECHNICAL-DESIGN.md`, `docs/UX-DESIGN.md`, `FEEDBACK.md`.

## Licence and data

Apache-2.0. Service manuals are manufacturer copyright, indexed locally for retrieval and quoted in short spans with page numbers; never redistributed. openFDA data is CC0. INGENZI sample is CC BY-NC 4.0 (attribution INGENZI Tech).

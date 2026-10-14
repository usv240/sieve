# Sieve

**Photographs a dead oxygen concentrator, finds the manual page, walks the fix with safety stops, checks recalls, and files the work order. Offline-capable.**

Built for the Nebius x NVIDIA Global AI Hackathon on **Nebius Token Factory** with **NVIDIA Nemotron 3 Nano, Super and Ultra**. Apache-2.0.

> Benchmark A: 69.7 percent on the closest prior work's own dataset, versus 62.0 percent for the obvious baseline and 17.0 percent zero-shot, two independent judges agreeing (kappa 0.94), with every Sieve answer cited and verified.
>
> 72 percent of broken hospital equipment in low-income countries was fixed without any imported parts (Malkin and Keane, 2010). Two-thirds of sub-Saharan countries have at most one biomedical engineer per million people (WHO, 2017). The gap is knowledge. Sieve puts that knowledge, the manufacturer's own service manual, in the technician's phone.

## Live

Web: https://sieve-kappa.vercel.app. API: https://sieve-api.vercel.app (OpenAPI docs at `/docs`). Both run on Vercel's free plan; the API is a Python function with a 300 second budget, enough for the Nemotron 3 Ultra audit.

## Status

Working scaffold with a real index and a real evaluation. Model-dependent stages run once a Token Factory key is present.

| Area | State |
|---|---|
| Corpus | 165 manuals, 9,458 pages indexed locally (oxygen concentrators 73, pulse oximeters 68, suction pumps 24). Manuals are not redistributed; `make fetch-corpus` rebuilds the index from `data/manifest.yaml`. |
| Registry | Philips EverFlo and DeVilbiss 525 indicator tables, every entry cited to a verified manual page. Six more concentrator models identified and retrievable. |
| Safety rules | 8 deterministic rules (oil near oxygen, open while plugged in, purity-alarm bypass, patient first, live mains, capacitors, swollen battery, no-manual-no-guess). |
| Pipeline | Identify, intake, device-scoped retrieval, Nemotron 3 Super synthesis with verbatim citations, deterministic citation verifier, rules gate, Nemotron 3 Ultra whole-manual audit, openFDA recalls, work order. |
| Web | Next.js app: landing that teaches the domain, Try flow with a Training Mode simulator, fleet, evals, how it works, API, limits, references. Light and dark, phone and desktop, info buttons on every term. |
| Eval (no key) | Hazardous requests gated 20/20, false stops 0/10, unknown devices refused 10/10, cited page retrieved in top 5 for 10/10 indicators. See `eval/results/`. |
| Eval (with key, 2026-10-14) | **Benchmark A, the competitor's own dataset (INGENZI, 300 held-out questions, blind Nemotron 3 Super judge): Sieve 69.7 percent, plain retrieval baseline 62.0 percent, Nano zero-shot 17.0 percent.** A second, independent judge (DeepSeek-V4.1-Flash) grading the same stored answers gives 66.0, 52.4 and 2.5 percent, with Cohen's kappa 0.94 between judges on Sieve answers. Sieve is the only system whose answers carry a verified citation (80.7 percent of its quotes found on the cited page). Benchmark B subset, 20 real openFDA complaints: raw citation integrity 87.7 percent before demotion, 100 percent after. Whole run $1.06. |

## Where the models run

| Stage | Model | Platform |
|---|---|---|
| Extraction, intake, drafting | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`, `nvidia/Nemotron-3_5-Lightning` | Nebius Token Factory (EU) |
| Fault-tree synthesis | `nvidia/nemotron-3-super-120b-a12b` | Nebius Token Factory (US) |
| Whole-manual audit | `nvidia/Nemotron-3-Ultra-550b-a55b` (1M context) | Nebius Token Factory (US) |
| Nameplate and panel reading | Token Factory image models, `openbmb/MiniCPM-V-4_5` first (2.6 s measured on a nameplate) | Nebius Token Factory. The NVIDIA Nemotron Nano VL endpoint (`infra/endpoint-vl`) is ready but needs AI Cloud billing, so it is not used in the demo. |
| Hybrid retrieval | `Qwen/Qwen3-Embedding-8B` embeddings over 2,994 concentrator pages, fused with BM25 | Nebius Token Factory; embedded in 352 s |
| Corpus ingestion | PyMuPDF plus Tavily extract for web-sourced manuals | Laptop (33 s). Serverless Job manifest in `infra/job-ingest` ready for AI Cloud |
| Live lookups and manual discovery | Tavily search, extract, map | Tavily API. When a known device has no manual, Sieve finds one, extracts it, indexes it and retrieves from it in the same request |
| Agent surfaces | MCP server with 6 tools (`apps/mcp`); Hermes Agent on Nemotron 3 Super via Token Factory (`infra/hermes`); OpenShell sandbox with brokered credentials (`infra/openshell`) | All verified: MCP over stdio; Hermes calling Sieve tools; a full diagnosis (Super, Ultra audit, Tavily) executed inside an OpenShell sandbox that holds only credential placeholders and can reach nothing but four hosts |
| Recalls and known problems | openFDA device/recall and MAUDE (CC0) | snapshot in `data/external` |

Every call is written to a ledger (tier, model, tokens, USD, latency) and shown in the app's Trace panel.

## Screenshots

Light and dark, same page: `docs/screenshots/landing-light.jpg`, `docs/screenshots/landing-dark.jpg`. Live fix with citations and Trace: `docs/screenshots/try-fix-dark.jpg`. Evals page: `docs/screenshots/evals-light.jpg`.

## Ecosystem, verified

- **MCP**: `apps/mcp/sieve_mcp.py` exposes list_devices, identify_device, identify_from_photo, analyze_fault, read_manual_page, file_work_order. Any MCP client can drive a full diagnosis.
- **Hermes Agent**: with the config in `infra/hermes`, `hermes -z "DeVilbiss 525, red light beeping. Use the sieve tools."` makes Nemotron 3 Super on Nebius call identify_device and analyze_fault and answer with the cited page. Hermes also bridges WhatsApp and Telegram, which is how field staff actually communicate.
- **OpenShell**: demonstrated on WSL2 plus Docker Desktop. Deny-by-default proven (EACCES at the kernel), four hosts allowed by policy, Nebius and Tavily credentials brokered so the sandbox only ever sees placeholders, and a full diagnosis run inside. Transcript and lessons in `infra/openshell/DEMONSTRATED.md`; reproduce with `infra/openshell/run.sh`.
- **Tavily**: search, extract and map are runtime calls, logged in the Trace next to the model calls.

## Quick start

```
git clone https://github.com/usv240/sieve && cd sieve
cp .env.example .env            # add NEBIUS_API_KEY and TAVILY_API_KEY
make setup                      # uv sync + import paths
make fetch-corpus               # downloads manuals to data/corpus (gitignored)
make ingest                     # builds data/index/sieve.db in about 30 seconds
make test                       # 24 tests
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

`docs/IDEA.md`, `docs/PLAN.md`, `docs/TECHNICAL-DESIGN.md`, `docs/UX-DESIGN.md`, `FEEDBACK.md`.

## Licence and data

Apache-2.0. Service manuals are manufacturer copyright, indexed locally for retrieval and quoted in short spans with page numbers; never redistributed. openFDA data is CC0. INGENZI sample is CC BY-NC 4.0 (attribution INGENZI Tech).

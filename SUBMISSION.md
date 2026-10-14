# Devpost submission draft: Sieve

Track: Best Apps and Agents. Bonus: Best Use of Tavily. Team: Ujwal Vanjare (code), teammates on testing and video.

## Tagline (one line, chain of verbs)
Photographs a dead oxygen concentrator, finds the manual page, walks the fix with safety stops, checks recalls, files the work order. Offline-capable, open NVIDIA Nemotron models on Nebius Token Factory.

## First sentence (two numbers)
On the closest prior work's own dataset Sieve scores 72.7 percent against 61.3 percent for the obvious retrieval baseline and 16.0 percent zero-shot, with every answer cited and verified; on 20 real FDA malfunction complaints it blocks 20 of 20 hazardous requests with zero false stops.

## Inspiration
38.3 percent of hospital devices across 16 low- and middle-income countries are out of service (Perry and Malkin 2011). 72 percent of 2,849 repair requests in 60 hospitals were resolved without any imported parts (Malkin and Keane 2010). Two-thirds of sub-Saharan countries have at most one biomedical engineer per million people (WHO 2017). The gap is knowledge, and knowledge is what an open model can carry into a district hospital with no internet.

## What it does
A technician photographs the nameplate and alarm light. Sieve identifies the model, asks up to three questions, retrieves the real service manual pages, and writes a step-by-step fault tree where every step quotes the page it came from. Dangerous steps are stopped by rules before any model answers. Nemotron 3 Ultra audits the tree against the entire manual. FDA recalls and known malfunction patterns are checked. Tavily finds parts, and finds and ingests a manual when we have none. The repair is filed as a work order; the fleet view and a weekly brief update. Training Mode lets a trainee practise on a simulated panel and ask the machine what it would do. Offline mode runs on a laptop GPU.

## How we built it
Nebius Token Factory serves every language-model call: Nemotron 3 Nano and 3.5 Lightning for extraction, intake and the 140,000-token fleet brief; Nemotron 3 Super for synthesis; Nemotron 3 Ultra with the whole manual in a one-million-token context as auditor. Qwen3-Embedding-8B on Token Factory for hybrid retrieval over 9,458 indexed pages. Token Factory image models read nameplates; NVIDIA Nemotron Nano 12B VL was verified locally on an RTX 4070. Tavily search, extract and map. A deterministic YAML rules engine and an exact-span citation verifier decide what reaches the technician. Sieve is also an MCP server, runs inside Hermes Agent, and was executed inside an NVIDIA OpenShell sandbox with brokered credentials. FastAPI, Next.js, SQLite FTS5.

## Evaluation (all reproducible with `make eval`)
Benchmark A, INGENZI 300 held-out, blind judge: Sieve 72.7, chunk-RAG 61.3, zero-shot 16.0. Benchmark B, 20 openFDA complaints: raw citation integrity 88.4 percent, 100 percent after demotion. Negative controls: 20 of 20 hazards gated, 0 of 10 false stops, 10 of 10 unknown devices refused, 10 of 10 cited pages retrieved. Lighthouse accessibility 100 on every page. Cost of every run published from the ledger.

## Prior art and what is new
INGENZI Tech (arXiv 2601.16967) and Jua (Devpost 2023) built text chatbots over manuals. Sieve adds photo-first identification, a cited indicator registry, deterministic safety gates, an independent whole-manual audit, recall checks, the work order and fleet brief, the digital twin, offline mode, MCP, Hermes, OpenShell, and an external evaluation on the prior work's own data.

## Challenges
The manual corpus is copyright-grey, so it is indexed locally and never redistributed. PDF text artefacts broke exact quote matching until a tiered verifier was built. Vision Nemotron is not on Token Factory's shared endpoints; the local GPU path proved it. Nebius AI Cloud needs a card, so the Serverless manifests are prepared but the run was done on a laptop. OpenShell on WSL2 plus Docker Desktop needed an undocumented endpoint override.

## What we learned
Models read and draft; tables, rules and verifiers decide. That rule is what let us put numbers on refusals instead of describing an architecture.

## What is next
A real pilot with a district hospital biomedical department; the NVIDIA page-image embedder on a Serverless Job; OCR enrichment for the 2,121 scanned pages; WhatsApp delivery through Hermes.

## Feedback on Nebius and NVIDIA tools (required)
See FEEDBACK.md in the repository: onboarding times, what worked, what needs work, whether we would build with them again.

## Links
Repository: https://github.com/usv240/sieve (Apache-2.0). Demo: (hosted URL). Video: (YouTube URL).

## Built With
nebius-token-factory, nvidia-nemotron-3-nano, nvidia-nemotron-3-super, nvidia-nemotron-3-ultra, nvidia-nemotron-3.5-lightning, nvidia-nemotron-nano-vl, tavily, hermes-agent, nvidia-openshell, mcp, fastapi, nextjs, sqlite, llama.cpp, openfda

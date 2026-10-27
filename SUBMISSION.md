# Devpost submission draft: Sieve

Track: Physical AI. Bonus: Best Use of Tavily. (Antidote, our other entry, is in Best Apps and Agents.) Team: Ujwal Vanjare (code), teammates on testing and video.

## Tagline (one line, chain of verbs)
Photographs a dead oxygen concentrator, finds the manual page, walks the fix with safety stops, checks recalls, files the work order. Offline-capable, open NVIDIA Nemotron models on Nebius Token Factory.

## Why Physical AI
Sieve is an edge agent for physical machines. It senses through the phone camera: NVIDIA Nemotron 3.5 Super VL reads the nameplate and the alarm lights, and a second model must agree before Sieve opens a manual. It reasons on the device when there is no internet: NVIDIA Nemotron Nano 9B v2 on a laptop GPU through llama.cpp, with Nemotron Nano 12B v2 VL verified for photos offline. It acts in the real world through the technician's hands: it chooses the next physical check, waits for what the technician sees, and branches on the answer. Smoke, oil near oxygen and live mains work stop it before any model replies. Hermes Agent is the runtime that exposes Sieve as tools and runs a scheduled FDA recall watch over the fleet.

Video module clip (one minute): a photo of a real concentrator, the device identified, the first physical check with its manual sentence, a branch on the technician's answer, and the smoke stop.

## First sentence (two numbers)
On the closest prior work's own dataset Sieve scores 69.7 percent against 62.0 percent for the obvious retrieval baseline and 17.0 percent zero-shot, confirmed by a second independent judge (kappa 0.94), with every answer cited and verified; on 62 real FDA reports of oxygen concentrators that smoked, burned or caught fire, it took the unit out of service before showing a single step, 62 of 62 times.

## Inspiration
38.3 percent of hospital devices across 16 low- and middle-income countries are out of service (Perry and Malkin 2011). 72 percent of 2,849 repair requests in 60 hospitals were resolved without any imported parts (Malkin and Keane 2010). Two-thirds of sub-Saharan countries have at most one biomedical engineer per million people (WHO 2017). The gap is knowledge, and knowledge is what an open model can carry into a district hospital with no internet.

## What it does
A technician photographs the nameplate and alarm light. Sieve identifies the model, asks up to three questions, retrieves the real service manual pages, and writes a step-by-step fault tree where every step quotes the page it came from. Dangerous steps are stopped by rules before any model answers. Nemotron 3 Ultra audits the tree against the entire manual. FDA recalls and known malfunction patterns are checked. Tavily finds parts, and finds and ingests a manual when we have none. The repair is filed as a work order; the fleet view and a weekly brief update. Training Mode lets a trainee practise on a simulated panel and ask the machine what it would do. Offline mode runs on a laptop GPU.

## How we built it
Nebius Token Factory serves every language-model call: Nemotron 3 Nano and 3.5 Lightning for extraction, intake and the 140,000-token fleet brief; Nemotron 3 Super for synthesis; Nemotron 3 Ultra with the whole manual in a one-million-token context as auditor. Qwen3-Embedding-8B on Token Factory for hybrid retrieval over 9,458 indexed pages. NVIDIA Nemotron 3.5 Super VL on Token Factory reads the nameplate, and a second, different model reads it again; Sieve opens a manual on its own only when both reads agree, because we caught Nemotron VL inventing a 525DS rating on a real 1025DS label. Offline, NVIDIA Nemotron Nano 12B v2 VL reads photos on a laptop RTX 4070. Tavily search, extract and map. A deterministic YAML rules engine and an exact-span citation verifier decide what reaches the technician. Sieve is also an MCP server, runs inside Hermes Agent, and was executed inside an NVIDIA OpenShell sandbox with brokered credentials. FastAPI, Next.js, SQLite FTS5.

## Evaluation (all reproducible with `make eval`)
Benchmark A, INGENZI 300 held-out, blind Nemotron 3 Super judge: Sieve 69.7, chunk-RAG 62.0, zero-shot 17.0; second judge DeepSeek-V4.1-Flash: 66.0, 52.4, 2.5; Cohen's kappa 0.94 to 1.0. Benchmark B, 74 openFDA malfunction reports, selection and scoring pre-registered before the run: remove-from-service stop on 62 of 62 fire and heat reports; root cause named in 20.3 percent against 24.3 percent for a Nano zero-shot baseline, two judges in agreement (kappa 0.95). We publish that Sieve does not beat the baseline at root cause: manufacturers find failed capacitors and connectors by teardown, and the complaint does not describe them. Citation integrity 94.7 percent. Real-world photos: 57 photos from resale listings and product pages, annotated by eye before any run. Sieve identified 82.9 percent of covered concentrators, 96.2 percent when the model name is legible, refused all 16 look-alike devices it has no manual for, and never auto-selected a wrong device. Citations: Sieve now cites by pointing at numbered manual sentences instead of copying them; on the same ten cases 100 percent of citations resolve against 88.8 percent for copied quotes. Each step carries a label saying whether the manual states it; an independent judge agreed with 62.5 percent of steps labelled as stated, against 5 percent of steps labelled general practice. Negative controls: 20 of 20 hazards gated, 0 of 10 false stops, 10 of 10 unknown devices refused, 10 of 10 cited pages retrieved. Lighthouse accessibility 100 on every page. Cost of every run published from the ledger.

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
Repository: https://github.com/usv240/sieve (Apache-2.0). Demo: https://sieve-kappa.vercel.app (API and OpenAPI docs: https://sieve-api.vercel.app/docs). Video: (YouTube URL).

## Built With
nebius-token-factory, nvidia-nemotron-3-nano, nvidia-nemotron-3-super, nvidia-nemotron-3-ultra, nvidia-nemotron-3.5-lightning, nvidia-nemotron-nano-vl, tavily, hermes-agent, nvidia-openshell, mcp, fastapi, nextjs, sqlite, llama.cpp, openfda

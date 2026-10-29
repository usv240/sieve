# Devpost submission draft: Sieve

Track: Physical AI. Bonus: Best Use of Tavily. (Antidote, our other entry, is in Best Apps and Agents.) Team: Ujwal Vanjare (code), teammates on testing and video.

## Tagline (one line, chain of verbs)
Photographs a dead oxygen concentrator, finds the manual page, walks the fix with safety stops, checks recalls, files the work order. Offline-capable, open NVIDIA Nemotron models on Nebius Token Factory.

## The result, in time and money
Four oxygen concentrators at Chintheche Health Center in Malawi sat broken for four years. A repair team with the right knowledge had all four running again in a few hours (OpenO2), instead of $2,000 to $6,400 for replacements. Sieve puts that knowledge in every technician's phone: a repair plan from the manufacturer's own service manual, every step cited to its page and audited by Nemotron 3 Ultra, in under a minute for about 5 to 7 US cents.

## Judge it in two minutes (no sign-up, no key)
- **Technological implementation:** run the EverFlo yellow-light case live (https://sieve-kappa.vercel.app/try?sample=everflo-yellow). In under a minute Nemotron 3 Super writes the plan, every step points at a numbered manual sentence that a verifier checks on its page, Nemotron 3 Ultra audits the plan against the whole manual, and the Trace panel lists every call with tokens, cost and seconds.
- **Design:** on the landing page (https://sieve-kappa.vercel.app), pick what the front panel shows and watch the manual's meaning, the first check and its quoted page change. Then follow it from photo to work order to a QR sticker for the machine.
- **Potential impact:** six published sources, under "Validated against real-world evidence" below. Equipment without a service manual is 55 percent less likely to work, and working oxygen cut child pneumonia deaths by 35 percent.
- **Quality of the idea:** ask to oil the compressor (https://sieve-kappa.vercel.app/try?sample=hazard-oil) and a fixed rule stops it before any model is asked. The evals page (https://sieve-kappa.vercel.app/evals) shows 69.7 percent on the closest prior work's own dataset against 62.0 for the baseline.
- **Your own data:** upload any service manual on https://sieve-kappa.vercel.app/data and ask it a question. Create your own API key on https://sieve-kappa.vercel.app/api.
- **Your own agent:** add https://sieve-api.vercel.app/mcp as a remote MCP server in Claude, Cursor or any MCP client. No install: list_devices, identify_device, diagnose and read_manual_page.

## Why Physical AI
Sieve is an edge agent for physical machines. It senses through the phone camera: NVIDIA Nemotron 3.5 Super VL reads the nameplate and the alarm lights, and a second model must agree before Sieve opens a manual. It reasons on the device when there is no internet: NVIDIA Nemotron Nano 9B v2 on a laptop GPU through llama.cpp, with Nemotron Nano 12B v2 VL verified for photos offline. It acts in the real world through the technician's hands: it chooses the next physical check, waits for what the technician sees, and branches on the answer. Smoke, oil near oxygen and live mains work stop it before any model replies. Hermes Agent is the runtime that exposes Sieve as tools and runs a scheduled FDA recall watch over the fleet. On Nebius AI Cloud, a Serverless Endpoint served NVIDIA Nemotron Nano 12B v2 VL for real-time photo reading and was benchmarked on the same 57 real photos (73.2 percent alone, against 82.9 percent for the two-model check), and a Serverless Job evaluated both entries from a clean machine.

Video module clip (one minute): a photo of a real concentrator, the device identified, the first physical check with its manual sentence, a branch on the technician's answer, the smoke stop, and the repair ending as a printed sticker on the machine that a phone scans to start the next repair.

## First sentence (two numbers)
On the closest prior work's own dataset Sieve scores 69.7 percent against 62.0 percent for the obvious retrieval baseline and 17.0 percent zero-shot, confirmed by a second independent judge (kappa 0.94), with every answer cited and verified; on 62 real FDA reports of oxygen concentrators that smoked, burned or caught fire, it took the unit out of service before showing a single step, 62 of 62 times.

## Inspiration
At Chintheche Health Center in Malawi, four oxygen concentrators sat broken for four years. A repair team had all four running again in a few hours (OpenO2). Replacing them would have cost $2,000 to $6,400 before shipping: UNICEF puts a concentrator at $500 to $1,600 ex-works, with at least 30 percent added to land it. The machines were never the problem; the knowledge was.

38.3 percent of hospital devices across 16 low- and middle-income countries are out of service (Perry and Malkin 2011). 72 percent of 2,849 repair requests in 60 hospitals were resolved without any imported parts (Malkin and Keane 2010). Two-thirds of sub-Saharan countries have at most one biomedical engineer per million people (WHO 2017). The gap is knowledge, and knowledge is what an open model can carry into a district hospital with no internet.

## What it does
A technician photographs the nameplate and alarm light. Sieve identifies the model, asks up to three questions, retrieves the real service manual pages, and writes a step-by-step fault tree where every step quotes the page it came from. Dangerous steps are stopped by rules before any model answers. Nemotron 3 Ultra audits the tree against the entire manual. FDA recalls and known malfunction patterns are checked. Tavily finds parts, and finds and ingests a manual when we have none. The repair is filed as a work order, and Sieve prints a QR sticker for the machine itself: the next technician scans it, sees the last repair, and starts the next one on the right manual without identifying the machine again. The sticker carries the record in its own link, so it opens even when the hospital's server is down. The fleet view and a weekly brief update. Training Mode lets a trainee practise on a simulated panel and ask the machine what it would do. Offline mode runs on a laptop GPU.

## How we built it
Nebius Token Factory serves every language-model call: Nemotron 3 Nano and 3.5 Lightning for extraction, intake and the 140,000-token fleet brief; Nemotron 3 Super for synthesis; Nemotron 3 Ultra with the whole manual in a one-million-token context as auditor. Hybrid retrieval over 9,462 indexed pages: full-text search everywhere, fused with Qwen3-Embedding-8B vectors from Token Factory for the 2,994 oxygen concentrator pages. NVIDIA Nemotron 3.5 Super VL on Token Factory reads the nameplate, and a second, different model reads it again; Sieve opens a manual on its own only when both reads agree, because we caught Nemotron VL inventing a 525DS rating on a real 1025DS label. Offline, NVIDIA Nemotron Nano 12B v2 VL reads photos on a laptop RTX 4070. Tavily search, extract and map. A deterministic YAML rules engine and an exact-span citation verifier decide what reaches the technician. Sieve is also an MCP server, runs inside Hermes Agent, and was executed inside an NVIDIA OpenShell sandbox with brokered credentials; a Hermes agent also runs in an NVIDIA NemoClaw sandbox on Nemotron 3 Super through Token Factory. FastAPI, Next.js, SQLite FTS5.

## How Sieve uses Tavily (Best Use of Tavily)
- **Closes the gap when there is no manual, in the same request.** When a known device has no manual in the index, Tavily search finds one on manual sites, Tavily extract pulls its text, Sieve indexes it and retrieves from it before writing the plan. The technician gets cited steps instead of "not covered".
- **Finds the part for the cited fault.** After the plan names a failed part, Tavily search over supplier sites returns where to buy it, scoped to that device.
- **Built the corpus and the benchmark.** Tavily extract read the manual library's category pages to discover 25 more manuals, and Tavily image search found the 57 real-world photos for the photo benchmark, annotated by eye before any run.
- Every Tavily call is logged in the same ledger as the model calls and shown in the Trace panel.

## Validated against real-world evidence
Sieve is tested on data nobody on the team wrote: 57 photos of real concentrators from resale listings and product pages, 74 pre-registered FDA malfunction reports filed by the people who opened the machines, and the closest prior work's own 300 repair questions. It is built on what biomedical technicians have already measured: the Malawi and Gabon health-worker surveys of the knowledge gap, and the NEST360 survey of equipment downtime across 63 hospitals.

### What the published evidence says

- **Missing service manuals predict broken equipment.** Across public hospitals in Amhara, Ethiopia, equipment without a service manual was 55 percent less likely to be functional (adjusted odds ratio 0.45); the service manual and technician training were the key determinants of functionality (Sewagegn et al., Discover Health Systems 2025, https://link.springer.com/article/10.1007/s44250-025-00312-9). Sieve puts the right manual page in front of the technician.
- **Concentrators fail, and skills are the reason given.** Of 57 oxygen concentrators tested in secondary hospitals in southwest Nigeria, 2 were fit for use; no concentrator had a clean external filter, and staff listed lack of maintenance knowledge and of technician training among the causes (Bakare, Graham et al., International Health 2020, https://pmc.ncbi.nlm.nih.gov/articles/PMC6964224/).
- **The person with the know-how doubles uptime.** Rural Nepali hospitals without a biomedical technician had twice the share of non-functional devices of those with one, 14 versus 7 percent (Thapa et al., Human Resources for Health 2022, https://pmc.ncbi.nlm.nih.gov/articles/PMC8895523/).
- **A working concentrator saves lives.** When hospitals in Papua New Guinea gained working oxygen systems, the risk of death for children with pneumonia fell by 35 percent (Duke et al., Lancet 2008, https://pubmed.ncbi.nlm.nih.gov/18708248/). Worldwide, only 30 percent of the 299 million people in low- and middle-income countries who need oxygen receive it, and technical surveys found most hospital concentrators in sub-Saharan Africa and south Asia not functioning (Lancet Global Health Commission on medical oxygen security, 2025, https://pmc.ncbi.nlm.nih.gov/articles/PMC11865010/).
- **Step-by-step structure changes outcomes.** A 19-item checklist cut surgical deaths from 1.5 to 0.8 percent across eight hospitals in eight cities, from Seattle to Ifakara in Tanzania (Haynes et al., NEJM 2009, https://pubmed.ncbi.nlm.nih.gov/19144931/). Sieve brings the same discipline to repair: one check at a time, each from the manual.
- **The oil stop is industry standard.** "Oil and grease are particularly hazardous in the presence of oxygen as they can ignite extremely easily and burn with explosive violence" (European Industrial Gases Association, Doc 04/26, https://www.eiga.eu/uploads/documents/DOC004.pdf). Sieve blocks any lubricant near the oxygen path before a model replies.

## Where Token Factory accelerated our workflow

- Five NVIDIA models behind one key and one API shape. Nemotron 3 Nano, 3.5 Lightning, 3 Super, 3 Ultra and 3.5 Super VL all answer the same OpenAI-compatible call. Moving a pipeline stage to a different tier is a one-line change in the router, which is how we tuned cost and speed per stage instead of picking one model for everything.
- A one-million-token auditor without a GPU. Nemotron 3 Ultra reads an entire service manual in a single call. Running a 550B model ourselves was out of reach for a laptop team.
- Long context as a feature, not a workaround. The weekly fleet brief sends 140,000 tokens (the whole fleet log, 647 FDA reports and 34 recalls) to Nemotron 3.5 Lightning in one call, at about one cent.
- Evaluation at a scale we could afford. Benchmark A graded 300 questions across three systems with two judges for $0.65. Every benchmark in this repo was rerun several times during development because each run cost cents.
- A vision model appeared mid-hackathon and we switched in a day. Nemotron 3.5 Super VL arrived in the catalog; adopting it was a model id and one request flag, and it became our first photo reader.
- Embeddings from the same account. Qwen3-Embedding-8B on Token Factory embedded the 2,994 oxygen concentrator pages in 352 seconds; full-text search covers all 9,462, so retrieval, generation and audit share one bill and one ledger.

## Evaluation (all reproducible with `make eval`)
Benchmark A, INGENZI 300 held-out, blind Nemotron 3 Super judge: Sieve 69.7, chunk-RAG 62.0, zero-shot 17.0; second judge DeepSeek-V4.1-Flash: 66.0, 52.4, 2.5; Cohen's kappa 0.94 to 1.0. Benchmark B, 74 openFDA malfunction reports, selection and scoring pre-registered before the run: remove-from-service stop on 62 of 62 fire and heat reports. Citation integrity 95.6 percent on real FDA complaints (94.7 on Benchmark B). Real-world photos: 57 photos from resale listings and product pages, annotated by eye before any run. Two vision models read each photo, NVIDIA Nemotron 3.5 Super VL and a second model, and Sieve picks a device on its own only when both agree. It identified 82.9 percent of covered concentrators and 100 percent of those whose model name is legible, refused all 16 look-alike devices it has no manual for, and never auto-selected a wrong device. Citations: Sieve now cites by pointing at numbered manual sentences instead of copying them; on the same ten cases 100 percent of citations resolve against 88.8 percent for copied quotes. Each step carries a label saying whether the manual states it; an independent judge agreed with 62.5 percent of steps labelled as stated, against 5 percent of steps labelled general practice. Negative controls: 20 of 20 hazards gated, 0 of 10 false stops, 10 of 10 unknown devices refused, 10 of 10 cited pages retrieved. Lighthouse accessibility 100 on every page. Cost of every run published from the ledger.

## Prior art and what is new
INGENZI Tech (arXiv 2601.16967) and Jua (Devpost 2023) built text chatbots over manuals. Sieve adds photo-first identification, a cited indicator registry, deterministic safety gates, an independent whole-manual audit, recall checks, the work order and fleet brief, the digital twin, offline mode, MCP, Hermes, OpenShell, and an external evaluation on the prior work's own data.

## Challenges
The manual corpus is copyright-grey, so it is indexed locally and never redistributed. PDF text artefacts made exact quote matching hard, so we built a tiered verifier and then switched to citing numbered sentences, which resolve 100 percent of the time. Worn nameplates are hard to read, so Sieve reads every photo twice with two different models and opens a manual on its own only when they agree. Nebius AI Cloud has no CPU-only quota on a new account, so the Serverless verification Job ran on an L40S GPU instead; it passed, and the Nemotron Nano 12B VL endpoint was benchmarked on the same photos and stopped after use (about $1). OpenShell on WSL2 plus Docker Desktop needed an undocumented endpoint override.

## What we learned
Models read and draft; tables, rules and verifiers decide. That rule is what let us put numbers on refusals instead of describing an architecture.

## What is next
Deployment with a district hospital biomedical department; the NVIDIA page-image embedder on a Serverless Job; OCR enrichment for the 2,121 scanned pages; WhatsApp delivery through Hermes.

## Feedback on Nebius and NVIDIA tools (required)
See FEEDBACK.md in the repository: onboarding times, what worked, what needs work, whether we would build with them again.

## Links
Repository: https://github.com/usv240/sieve (Apache-2.0). Demo: https://sieve-kappa.vercel.app (API and OpenAPI docs: https://sieve-api.vercel.app/docs). Video: (YouTube URL).

## Built With
nebius-token-factory, nebius-ai-cloud, nebius-serverless, nvidia-nemotron-3-nano, nvidia-nemotron-3-super, nvidia-nemotron-3-ultra, nvidia-nemotron-3.5-lightning, nvidia-nemotron-3.5-super-vl, nvidia-nemotron-nano-vl, nvidia-nemotron-nano-9b-v2, qwen3-embedding, tavily, hermes-agent, nvidia-openshell, nvidia-nemoclaw, mcp, fastapi, nextjs, sqlite, llama.cpp, openfda

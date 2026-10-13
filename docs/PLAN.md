# Sieve: Delivery Plan

Deadline: Oct 30 2026, 22:30 IST (10:00 PDT). Target submission: Oct 29. Time split across both projects: roughly 65 percent Sieve, 35 percent Antidote, because Sieve has hardware, a GPU job and a heavier eval.

Related: `IDEA.md` (the locked idea and evidence), `TECHNICAL-DESIGN.md`, `UX-DESIGN.md`, `../PLATFORM.md`.

---

## 1. Definition of done (what "exceeds expectations" means, concretely)

- A judge with no hardware runs the full flow on a sample in under 60 seconds and sees a live Token Factory call.
- Two external benchmark numbers and three negative-control numbers are on the /evals page with a one-line reproduce command, and baselines are beaten.
- Every generated step shows a verbatim quote and page from a real manual, and the citation verifier reports 100 percent integrity on the eval set.
- The video shows a real concentrator being diagnosed, a stop card firing, a work order filed, and the Trace with model names and cost.
- Offline mode runs on a laptop and its accuracy delta is published.
- BYO upload works end to end for a manual we do not have.
- API key, OpenAPI docs, three snippets and the MCP server work.
- README, FEEDBACK.md, LICENSE, .env.example, both-theme screenshots complete.
- One practitioner quote (a BMET, a hospital engineer, or EWH or Frank Weithoener) obtained by email and shown, or the attempt documented honestly.
- Training Mode works: pick a fault, the panel behaves per the manual, Send to Sieve runs the full flow.

---

## 2. Work breakdown

### Phase 0: Setup (Oct 13 to 14)
- Redeem credits: Token Factory promo code `NEBIUS-DEVPOST-GLOBAL26` via the promo form; join the Nebius Builders Program for the second $25 plus Tavily credits. Create the Tavily key. Check whether Nebius AI Cloud (Serverless) needs a card; if blocked, note the local ingestion fallback.
- Repo `sieve` on GitHub, Apache-2.0, description and topics set, CI with lint, tests, secret scan.
- No hardware purchase (decision 2026-10-13). Build Training Mode, a browser simulator of the EverFlo and DeVilbiss 525 front panels driven by the manuals' LED tables, as the demo and training surface. Collect licensed photos (iFixit DeVilbiss 525 page, CC BY-NC-SA; manual figures) for nameplates and interiors.
- Email outreach for a practitioner quote: a local hospital biomedical department, EWH, Frank Weithoener, two BMETs on LinkedIn. Template in `docs/outreach.md`.
- Download corpus per `data/manifest.yaml` to local storage (not committed). Pull openFDA MAUDE and recall snapshots (CC0, committed).
- Start `FEEDBACK.md` with onboarding notes: time to first Token Factory call, friction points.

### Phase 1: Core pipeline (Oct 15 to 17)
- `packages/llm`: dual-base-URL client, router, thinking toggle, tool-call structured output with validation retry, cost ledger, trace.
- `packages/retrieval`: PDF to pages, text extraction, LanceDB schema, BM25 plus vector hybrid, device scoping. Run ingestion locally first; package the Serverless Job container; launch one real Job and save its report.
- `packages/core`: device registry for seven concentrator models, fault concepts, intake question bank, matcher.
- `packages/rules`: Sieve rules YAML and evaluator with unit tests.
- Fault-tree synthesis with Super; citation verifier; first end-to-end CLI run on a text-only input.
- Eval harness skeleton: load INGENZI subset, load MAUDE set, run nano-zero-shot baseline, write results JSON.

### Phase 2: Vision, audit, enrich, record (Oct 18 to 20)
- Vision endpoint: Dockerfile for vLLM with Nemotron Nano VL, `nebius ai endpoint create` script, proxy, fallback to Token Factory image2text, then manual fields.
- Identify step with confidence and candidate picker.
- Ultra auditor with whole-manual context; approve, repair, reject loop.
- openFDA recall and MAUDE enrichment; Tavily manual search and parts lookup tools.
- Work order schema, storage per workspace, CSV and PDF export, fleet dashboard queries.
- Eval: run chunk-RAG baseline and full Sieve on A and B; author and publish the three negative-control sets; first REPORT.md.

### Phase 3: Product surface (Oct 21 to 23)
- Web app: landing page sections 3.1 to 3.13, /try four screens, /fleet, /evals rendering JSON, /how-it-works, /data with BYO upload, /api with keys and snippets, /limits, /references, /about.
- Info component wired to glossary.yaml; Explain mode; theme toggle; PWA manifest and service worker; status strip and health endpoint.
- BYO ingestion path (local worker plus Job when available).
- API keys, rate limits, OpenAPI, MCP server.
- Offline mode: llama.cpp server script, GGUF download, router switch, offline bundle; measure the delta.
- Sample gallery: six simulator states plus licensed nameplate photos; add the kettle negative sample. Training Mode: fault picker, panel behaviour per manual, Send to Sieve button, Simulator label always visible.

### Phase 4: Proof and polish (Oct 24 to 25)
- Final eval run with all baselines; commit results; write the numbers into the README and hero tiles.
- Accessibility pass: keyboard, contrast in both themes, labels, reduced motion, 320 px layout.
- Performance pass: first load under 300 KB JS, image lazy loading, Lighthouse above 90 on mobile.
- README complete with architecture diagram, "Where the models run" table, cost actuals, prior art section naming INGENZI and Jua with what Sieve adds.
- Practitioner quote inserted if obtained.

### Phase 5: Video and submission (Oct 26 to 27)
- Shoot the video per the storyboard below. Record screen at 1080p, phone footage of the real unit, voice-over scripted.
- Devpost draft: description, Built With, track Best Apps and Agents, demo URL, repo URL, video URL, feedback section.
- Fresh-clone test: a teammate or a clean machine follows the README from zero.

### Phase 6: Buffer and submit (Oct 28 to 29)
- Fix anything found in the fresh-clone test. Keep the vision endpoint up through judging windows or document the fallback. Submit Oct 29.

---

## 3. Video storyboard (2:50)

| Time | Visual | Voice-over |
|---|---|---|
| 0:00 | Black screen, one line of text: "38 percent of hospital equipment in poor countries is broken." | "Most of it is fixable without imported parts. What is missing is the knowledge, and the engineer, who is often one per million people." |
| 0:15 | Training Mode panel on a tablet, yellow light blinking, Simulator label visible | "This oxygen concentrator shows a yellow light. In a district hospital, that light can mean a child does not get oxygen tonight." |
| 0:25 | Phone photographs the tablet panel and a licensed nameplate photo is shown | "Sieve reads the nameplate with an NVIDIA Nemotron vision model running on a Nebius Serverless Endpoint." |
| 0:40 | Indicator picker, two questions | "It asks two questions, using Nemotron 3 Nano on Nebius Token Factory." |
| 0:55 | Fault tree, step 1 with page citation, page image opens | "Nemotron 3 Super builds the fault tree from the real service manual. Every step quotes the page it came from." |
| 1:15 | Stop card fires when the user picks "open the unit while running" | "Some steps are dangerous. A rules engine stops them before any model is allowed to answer. We measured it: 100 percent of our hazardous test cases were blocked." |
| 1:35 | Trace panel: Nano, Super, Ultra calls with cost | "Nemotron 3 Ultra, with the entire manual in its one-million-token context, audits every step. The whole session cost a few cents." |
| 1:55 | Recalls card and Tavily parts lookup | "Sieve checks FDA recalls and uses Tavily to find the part and its price." |
| 2:05 | Work order saved, fleet dashboard updates | "The repair is filed as a work order, and the hospital's fleet view updates." |
| 2:20 | /evals page: two benchmark numbers, baselines, negative controls | "We tested against an external dataset and against 150 real FDA malfunction reports, and we beat the obvious baseline. The numbers are on the site." |
| 2:35 | Laptop with offline mode banner | "No internet? Sieve runs offline on an open Nemotron model. Open models, open data, in the technician's hands." |
| 2:45 | Logo, URL, "Built on Nebius Token Factory with NVIDIA Nemotron 3" | "Sieve." |

---

## 4. Devpost submission outline

- Title: Sieve. Tagline: "Photographs a dead oxygen concentrator, finds the manual page, walks the fix with safety stops, checks recalls, files the work order. Offline."
- Inspiration: the two numbers and the Malawi fleet story.
- What it does: the four screens.
- How we built it: platform table, model routing, Serverless Job and Endpoint, Tavily, openFDA.
- Evaluation: benchmark A, benchmark B, negative controls, baselines, citation integrity, offline delta, cost.
- Prior art and what is new.
- Challenges, accomplishments, what we learned, what is next.
- Feedback on Nebius Token Factory, Serverless, Nemotron, Tavily (required field; copy from FEEDBACK.md).

---

## 5. Risk register (delivery)

| Risk | Likelihood | Plan |
|---|---|---|
| Simulator reads as less convincing than hardware | Medium | Label it honestly, make it manual-accurate, present it as a training feature with its own user; add a real unit only if one appears cheaply |
| Nebius AI Cloud credits blocked | Medium | Local ingestion; vision via Token Factory image2text fallback; document honestly |
| Ultra audits too slow or costly for the eval | Low | Audit only steps that pass the gate; cap at 8K thinking; cache by manual |
| Time overrun on UI | Medium | Landing page sections prioritised 3.1 to 3.8 first; the rest after evals are committed |
| No practitioner reply | Medium | Document outreach; quote the published practitioner surveys instead |

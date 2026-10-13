# Sieve: UX and Landing Page Design

Goal: a judge or a first-time technician who has never heard of a biomedical engineer opens the site and, within two minutes, understands what Sieve is, why it matters, how it works, trusts it, and has run it once on a sample photo. On a phone or a desktop, in light or dark, with an info button beside anything that might be unfamiliar.

Shared UI kit, tokens, Info component, Explain mode and theme behaviour are in `../PLATFORM.md` section 10.

---

## 1. Design principles we commit to (and will cite in the README)

1. **Progressive disclosure.** One plain sentence first; details behind an info button or a "Learn more" drawer. Never a wall of text.
2. **Recognition over recall.** Alarm lights are chosen from pictures, devices from thumbnails, steps shown one at a time with a photo of the part.
3. **Safety is visible, not buried.** Stop cards are full-width, high contrast, with the source quoted. The product guarantee "Sieve stops and escalates when the manual says to" appears on the landing page.
4. **Two audiences, one page.** Explain mode toggles every card between Plain and Technical wording. A nurse and an NVIDIA engineer read the same screen.
5. **Field conditions first.** 44 px targets for gloved hands, high contrast for sunlight, works at 320 px width, first load under 300 KB, offline-capable PWA.
6. **Accessibility baseline WCAG 2.2 AA.** Contrast, focus rings, keyboard paths, labels, reduced motion, no information carried by colour alone.
7. **Honesty in the interface.** Status strip shows live or replay, which backends are up, which model answered, and what it cost. Limits page shows measured numbers.

---

## 2. Information architecture

```
/                 Landing: teaches and invites a first run
/try              The app: Identify -> Intake -> Fix -> Record (also /try?sample=everflo-yellow)
/fleet            Dashboard of work orders (demo workspace pre-seeded)
/evals            Live evaluation results, baselines, negative controls, reproduce command
/how-it-works     Model routing diagram, trace example, safety architecture (Plain and Technical)
/data             Corpus, licences, BYO upload, what we do and do not redistribute
/api              API keys, OpenAPI, snippets, MCP server
/limits           Measured limits and what Sieve refuses to do
/references       Every statistic with its primary source
/about            Team, prior art named, Nebius and NVIDIA tools used, feedback
```

Header: logo, Try it, How it works, Evals, API, Explain mode toggle, theme toggle. Footer: licence, GitHub, video, Devpost, "Built on Nebius Token Factory with NVIDIA Nemotron 3".

---

## 3. Landing page, section by section

Each section lists the Plain text (default) and what the info buttons open. Technical text is shown when Explain mode is Technical.

### 3.1 Hero
- Headline: **"The manual is in the drawer. The engineer is 500 km away. The oxygen machine is dead."**
- Subhead: "Sieve reads the machine's nameplate and alarm light, finds the right page of the service manual, and walks a technician through the fix, with safety stops. Offline if needed."
- Two numbers as stat tiles, each with an info button linking to the primary source: "72% of broken hospital equipment in poor countries can be fixed without imported parts" and "Two-thirds of sub-Saharan countries have at most one biomedical engineer per million people."
- Buttons: "Try it on a sample photo" (opens /try with the EverFlo yellow-light sample) and "Watch 3-minute video".
- Status strip beneath: Live, vision endpoint up, Token Factory up, last eval date.

### 3.2 What is this, in one minute
Three cards: **What** (a repair copilot for hospital equipment technicians), **Why** (machines sit broken because the knowledge is in a manual nobody has), **How** (photo, questions, manual-grounded steps, safety stops, record). Each card has an info button: "What is a biomedical equipment technician?", "What is a service manual and why is it hard to get?", "Why do we say grounded?".

### 3.3 See it work (interactive, no hardware)
A sample gallery with six photos: EverFlo yellow light, DeVilbiss 525 red light, AirSep no power, suction pump weak suction, oximeter erratic reading, and a non-medical object (a kettle) to show the refusal. Clicking any sample runs the live flow inside the landing page in a framed panel. A small label says "Live call to Nebius Token Factory" or "Replay" if backends are down. Info button: "Why do you offer samples? So a judge or a new user can see the whole flow without owning a machine."

### 3.4 Who it is for
Three personas with one sentence of what changes for them: the district hospital technician (gets steps now, not next month), the nurse in charge when no technician exists (knows whether it is a five-minute fix or a call), the biomedical engineer covering 40 facilities (sees the fleet, plans parts). Info buttons explain each role.

### 3.5 The numbers
A table of six statistics, each row: the number, one plain sentence, the source as a link, year. Rows: 38.3 percent out of service; 72 percent fixable without parts; one engineer per million; 5 billion lack safe oxygen; 66.7 percent of primary facilities with a working concentrator; Malawi doubled its working fleet by repairing. Info button on the table: "Why these numbers and not others?" explaining why we excluded anecdotal figures.

### 3.6 How the AI works (Plain and Technical)
Plain: a labelled picture with five boxes: Look (reads the nameplate and light), Ask (up to three questions), Find (the right manual pages), Check (a second, larger model verifies every step against the manual; a rules engine stops dangerous steps), Record (writes the work order). Each box has an info button.
Technical: the same diagram with model names: Nemotron Nano VL on a Nebius Serverless Endpoint; Nemotron 3 Nano for intake; Nemotron 3 Super for synthesis; Nemotron 3 Ultra with the whole manual in a 1M context as auditor; deterministic rules engine; LanceDB hybrid retrieval with Nemotron embed and rerank models; openFDA; Tavily. A link opens a real Trace from the sample run.

### 3.7 Safety: what Sieve refuses
Four example stop cards rendered exactly as in the app: oil near oxygen, opening a running unit, bypassing the purity alarm, live mains testing. Text: "Sieve is built to stop. These are not suggestions the model declines; they are rules that fire before the model is allowed to answer." Link to /limits and /evals negative-control results.

### 3.8 Evaluation results
Three stat tiles pulled from `eval/results/latest.json`: Benchmark A accuracy vs baseline, Benchmark B top-3 agreement, negative controls (hazard blocked percent, false-stop percent, citation integrity percent). Button: "See full results and reproduce". Info button: "What is a baseline and why do we show one?"

### 3.9 Bring your own data
"Have a manual we do not? Upload it. Your hospital's documents are indexed in your own workspace, never mixed with others, and you can export or delete them any time." Button: Upload a manual (requires a free account). Info button: "What happens to my file?" with the pipeline in plain words.

### 3.10 Use Sieve as a service
Three tabs: curl, Python, JavaScript, each a complete request to `/v1/analyze` with a Copy button. Text: "Also available as an MCP server so your own agent can ask Sieve to identify a device." Button: Get an API key. Info buttons: "What is an API key?", "What is MCP?".

### 3.11 Built with
Logos and one sentence each: Nebius Token Factory (all language model calls), NVIDIA Nemotron 3 Nano, Super, Ultra (which does what), NVIDIA Nemotron Nano VL (vision), Nebius Serverless Endpoints and Jobs, Tavily, openFDA. Link to FEEDBACK.md.

### 3.12 Limits, honestly
Three measured limits with numbers from the eval: offline accuracy versus cloud; photo identification accuracy on worn nameplates; device classes covered. Text: "We publish limits as measurements, not promises."

### 3.13 References and FAQ
Full reference list with links. FAQ with eight questions a judge or a new user would ask, including "Is this medical advice?" (No: it is equipment maintenance guidance for trained staff, grounded in manufacturer and WHO documents, and it stops when those documents say to), "Does it replace a biomedical engineer?" (No: it transfers the first 107 skills and escalates the rest), "Why open models?" (hospitals need offline, sovereign, auditable tools).

---

## 4. The app (/try) screen by screen

**Screen 1: Identify.** Camera or upload, or pick a sample. After the photo: a card with manufacturer, model, confidence, and the matched manual title. Below 60 percent confidence: three candidate thumbnails to pick from. Info buttons: "Where does the model name come from?", "What if my device is not listed?" (leads to generic flowcharts and BYO).

**Screen 2: What do you see?** Indicator picker: thumbnails of light patterns for this model, each with its meaning and page citation. Then up to three questions, each with an info button on why it matters. Big toggles, no typing required.

**Screen 3: Fix.** Hypotheses ranked, then one step at a time: action, what you should expect, Yes and No buttons, tools needed, duration, and the citation (document, page, quote) with a "Show page" button that opens the page image. Stop cards interrupt the flow in full width with the rule reason and source. A right rail (desktop) or a bottom sheet (mobile) shows Parts, Recalls (openFDA), Tavily availability, and the Trace.

**Screen 4: Record.** Pre-filled work order; the technician edits outcome and parts; Save files it to the fleet, Export gives PDF and CSV, Print gives a one-page sheet. Confirmation shows the fleet counters updating.

**Trace panel (any screen).** Each model call: tier, model, purpose, tokens, cost, latency, and the auditor verdict per step. Info button: "Why show this?" (so you can see which model did what and what it cost; judges and hospital IT ask the same question).

---

## 5. Visual system

- Tokens: OKLCH palettes. Light: background near-white warm, text near-black, accent a deep teal (oxygen, medical, calm). Dark: background deep slate, text off-white, same accent lightened for contrast. Severity: caution amber with triangle icon and the word Caution; stop red with octagon icon and the word Stop; success green with check icon and the word Done. Colour is never the only signal.
- Type: a humanist sans for UI, tabular numerals for stats, 16 px base on mobile, 18 px on desktop, scale 1.25.
- Spacing: 8-point grid, cards with 16 px radius, generous padding, max content width 1100 px.
- Motion: 150 to 200 ms, reduced-motion respected, no decorative animation.
- Imagery: real photos of devices from the corpus where licensed, our own photos of the demo unit, line illustrations for the How it works diagram.

---

## 6. Light and dark, phone and desktop

- Theme: system default, user toggle persisted, no flash on load, all tokens defined for both; screenshots in README show both.
- Breakpoints: 320, 480, 768, 1024, 1280. Mobile uses a bottom tab bar (Identify, Fix, Record, Fleet). Desktop uses a left rail and a right details rail.
- PWA: installable, offline shell, offline banner that explains what still works.

---

## 7. Content rules for everything we write

- One idea per sentence. Plain words first. Define a term the first time it appears with an info button.
- Every statistic has a year and a link.
- Every generated step shows its source.
- No emojis, no em dashes, no exclamation marks in product copy.
- Say what Sieve is not: not medical advice, not a replacement for an engineer, not a parts shop.

---

## 8. Judge path, timed

0:00 land, read headline and two numbers. 0:20 click "Try it on a sample photo". 0:30 see model identified with confidence. 0:45 pick the yellow-light indicator, answer two questions. 1:10 read the first step with page citation, open the page image. 1:30 trigger a stop card by choosing the "open the unit while running" sample. 1:50 open the Trace and see Nano, Super, Ultra calls with cost. 2:10 save the work order, watch the fleet counter move. 2:30 open /evals, see benchmark, baseline and negative controls. Under three minutes, everything verified.

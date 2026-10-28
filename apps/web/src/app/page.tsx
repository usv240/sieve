import Link from "next/link";
import Image from "next/image";
import { Info } from "@/components/info";
import { Reveal } from "@/components/reveal";
import { SampleGallery } from "@/components/sample-gallery";
import { ShieldAlert } from "lucide-react";

const d = (ms: number) => ({ "--d": `${ms}ms` }) as React.CSSProperties;

const JUMP = [
  ["#what", "What it is"],
  ["#why", "Why it matters"],
  ["#how", "How it works"],
  ["#try", "Try it"],
  ["#results", "Results"],
  ["#who", "Who it is for"],
  ["#build", "Build on it"],
];

export default function Landing() {
  return (
    <div className="pb-8">
      <Reveal />

      {/* Hero: what it is, in one sentence, with the product doing its job beside it */}
      <section className="grid gap-12 pt-20 sm:pt-14 lg:grid-cols-[minmax(0,1.08fr)_minmax(0,0.92fr)] lg:items-center lg:gap-16 lg:pt-16">
        <div>
          <h1 className="rise text-balance text-[2.5rem] font-semibold leading-[1.03] tracking-[-0.03em] sm:text-6xl lg:text-[4.25rem]">
            The oxygen machine is dead.
          </h1>
          <p className="rise mt-6 max-w-xl text-xl leading-relaxed" style={d(90)}>
            Sieve is a repair copilot for hospital technicians<Info k="bmet" />. Photograph the machine and it walks the fix one check at a time, quoting the manufacturer&apos;s own service manual<Info k="service_manual" />.
          </p>
          <div className="rise mt-8 flex flex-wrap gap-3" style={d(180)}>
            <Link href="/try?sample=everflo-yellow" className="btn-primary">Try it on a sample machine</Link>
            <a href="#how" className="btn-ghost">See how it works</a>
            {process.env.NEXT_PUBLIC_VIDEO_URL ? <a href={process.env.NEXT_PUBLIC_VIDEO_URL} className="btn-ghost" target="_blank" rel="noreferrer">Watch the 3-minute video</a> : null}
          </div>
          <p className="rise mt-8 max-w-xl text-base leading-relaxed text-fg-muted" style={d(260)}>
            At Chintheche Health Center in Malawi, four concentrators sat broken for four years. A repair team had all four running again in a few hours{" "}
            (<a className="text-accent underline underline-offset-2" href="https://www.openo2.org/concentrator-graveyard" target="_blank" rel="noreferrer">OpenO2</a>). Replacing them would have cost $2,000 to $6,400 before shipping{" "}
            (<a className="text-accent underline underline-offset-2" href="https://www.unicef.org/supply/media/2916/file/_Oxygen-Concentrator-TPP-v1.pdf" target="_blank" rel="noreferrer">UNICEF</a>).
          </p>
        </div>

        <figure data-ui className="rise rounded-[24px] bg-surface p-6 sm:p-8" style={d(200)}>
          <p className="text-[0.9375rem] text-fg-muted">Philips EverFlo, yellow light on, alarm silent</p>
          <p className="mt-3 text-2xl font-semibold leading-snug tracking-[-0.01em]">Step 1 of 3: observe the lights on the front panel.</p>
          <p className="mt-2 text-base text-fg-muted">Expected: yellow light on, red light off, alarm silent.</p>
          <blockquote className="quote mt-5 text-base leading-relaxed">
            &ldquo;Yellow LED illuminates continuously. The Red LED is off and the Audible Alarm is silent. The device has detected a low oxygen condition. (For OPI units only.)&rdquo;
            <footer className="mt-2 text-[0.9375rem] text-fg-muted">Philips EverFlo service manual, page 31</footer>
          </blockquote>
          <div className="mt-5 flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-ok/15 px-3 py-1 text-[0.9375rem] font-medium text-ok">The manual states this step</span>
           <Info k="support_label" />
          </div>
          <div className="mt-6 flex flex-wrap gap-2">
            <span className="rounded-full bg-accent px-4 py-2 text-[0.9375rem] font-semibold text-accent-fg">Yes, as expected</span>
            <span className="rounded-full bg-bg-elev px-4 py-2 text-[0.9375rem] font-semibold">No</span>
          </div>
          <figcaption className="mt-6 text-[0.9375rem] leading-relaxed text-fg-muted">
            From a live run: every quote is checked against its page, and Nemotron 3 Ultra audits the whole plan against the full manual.{" "}
            <Link href="/try?sample=everflo-yellow" className="text-accent underline underline-offset-2">Run it yourself</Link>
          </figcaption>
        </figure>
      </section>

      <nav aria-label="On this page" className="rise mt-14 flex flex-wrap gap-2" style={d(340)}>
        {JUMP.map(([href, label]) => (
          <a key={href} href={href} className="lift rounded-full bg-surface px-4 py-2 text-[0.9375rem] text-fg-muted hover:text-fg">{label}</a>
        ))}
      </nav>

      {/* What, why, how in one minute */}
      <section id="what" aria-labelledby="what-h" className="scroll-mt-32 pt-28">
        <h2 id="what-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Sieve in one minute</h2>
        <div className="mt-10 grid gap-10 md:grid-cols-3 md:gap-12">
          <div data-reveal style={d(60)}>
            <h3 className="text-xl font-semibold">What it is</h3>
            <p className="mt-3 text-lg leading-relaxed">A step-by-step repair guide for the oxygen concentrators<Info k="concentrator" /> that keep patients breathing. The technician photographs the nameplate; Sieve opens the right page of the real service manual and waits for each answer before the next check.</p>
          </div>
          <div data-reveal style={d(140)}>
            <h3 className="text-xl font-semibold">Why it matters</h3>
            <p className="mt-3 text-lg leading-relaxed">Most broken hospital equipment needs knowledge, not parts: in one study of 2,849 repairs, 72 percent needed no imported parts. That knowledge sits in a service manual the technician does not have, and the nearest engineer can be a day away.</p>
          </div>
          <div data-reveal style={d(220)}>
            <h3 className="text-xl font-semibold">How it works</h3>
            <p className="mt-3 text-lg leading-relaxed">Open NVIDIA Nemotron models on Nebius Token Factory read the photo, find the pages and write the plan, and every step quotes its page<Info k="grounded" />. Fixed rules stop hazards before any model answers<Info k="safety_stop" />, and a larger model audits the whole plan.</p>
          </div>
        </div>
      </section>

      {/* Why: the evidence, with the machine itself */}
      <section id="why" aria-labelledby="why-h" className="scroll-mt-32 pt-36">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] lg:gap-16">
          <figure data-reveal className="lg:order-none">
            <Image src="/images/concentrator.jpg" alt="A beige DeVilbiss LT4000 oxygen concentrator with green tubing and a printed sticker that says it is for machine breakdown calls only" width={1000} height={1176} sizes="(min-width: 1024px) 440px, 100vw" className="h-auto w-full rounded-[20px] object-cover" />
            <figcaption className="mt-3 text-[0.9375rem] text-fg-muted">An oxygen concentrator in a patient&apos;s home. The sticker gives a number to call for machine breakdowns, office hours only.</figcaption>
          </figure>
          <div>
            <h2 id="why-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Why it matters</h2>
            <div data-reveal style={d(80)} className="mt-8">
              <p className="text-7xl font-semibold tracking-[-0.04em] text-accent sm:text-8xl">55%</p>
              <p className="mt-3 max-w-xl text-xl leading-relaxed">lower odds that a hospital device is working when its service manual is missing, across public hospitals in Amhara, Ethiopia. <a className="text-accent underline underline-offset-2" href="https://link.springer.com/article/10.1007/s44250-025-00312-9" target="_blank" rel="noreferrer">Sewagegn et al., 2025</a></p>
            </div>
            <ul className="mt-12 grid gap-x-8 gap-y-14 sm:grid-cols-3">
              <Stat n="2 of 57" t="oxygen concentrators tested in Nigerian hospitals were fit for use." s="Bakare et al., 2020" u="https://pmc.ncbi.nlm.nih.gov/articles/PMC6964224/" i={100} />
              <Stat n="2x" t="as many broken devices in rural Nepali hospitals with no biomedical technician." s="Thapa et al., 2022" u="https://pmc.ncbi.nlm.nih.gov/articles/PMC8895523/" i={160} />
              <Stat n="35%" t="fewer child pneumonia deaths once hospitals had working oxygen." s="Duke et al., Lancet 2008" u="https://pubmed.ncbi.nlm.nih.gov/18708248/" i={220} />
            </ul>
            <p className="mt-10 text-base"><Link href="/references" className="font-semibold text-accent underline underline-offset-4">All 22 sources behind the numbers on this site</Link></p>
          </div>
        </div>
      </section>

      {/* How: the five stages, and which model does what */}
      <section id="how" aria-labelledby="how-h" className="scroll-mt-32 pt-36">
        <h2 id="how-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">How it works<Info k="tier_routing" /></h2>
        <p data-reveal style={d(60)} className="mt-4 max-w-2xl text-xl leading-relaxed">Models read and draft. Tables, rules and a verifier decide what reaches the technician.</p>
        <div className="mt-12 grid gap-14 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:gap-16">
          <ol className="space-y-9">
            <Stage i={0} title="Look at the machine" text="Reads the nameplate and the lights from one photo, then names the machine only when two different vision models agree." model="NVIDIA Nemotron 3.5 Super VL and a second reader" tech="The registry, not the model, picks the device: an auto-selection needs both reads to point to the same machine; otherwise the technician chooses from the top matches." />
            <Stage i={1} title="Ask what changes the answer" text="Asks up to three questions, such as whether the unit smells of burning, before writing anything." model="NVIDIA Nemotron 3 Nano" tech="Chosen from a fixed question bank, so a question is never invented; a burning smell or smoke ends the repair immediately." />
            <Stage i={2} title="Find the right pages" text="Searches 9,462 pages from 167 real service manuals, limited to this machine's own documents." model="Qwen3-Embedding-8B with full-text search" tech="SQLite FTS5 BM25 fused by reciprocal rank with embeddings from Token Factory; retrieval is scoped to the device so an EverFlo question never returns another brand's page." />
            <Stage i={3} title="Write the plan and check it" text="Writes one check at a time, each pointing at a numbered sentence of the manual, then audits the plan against the entire manual." model="NVIDIA Nemotron 3 Super, audited by Nemotron 3 Ultra" tech="Code copies the cited sentence word for word; Nemotron 3 Ultra reads the whole manual in its one-million-token context; YAML rules gate both the request and every output." />
            <Stage i={4} title="Record the repair" text="Files the work order, prints a QR sticker for the machine and adds the repair to the fleet view." model="NVIDIA Nemotron 3.5 Lightning for the weekly fleet brief" tech="FDA recalls and malfunction reports are checked for the model; the fleet brief reads the whole log plus 647 FDA reports in one 140,000-token call." />
          </ol>
          <div data-reveal style={d(120)}>
            <div className="rounded-[20px] bg-surface p-5 sm:p-6">
              <h3 className="text-lg font-semibold">Which model does what<Info term="Model routing" text="Each job goes to the smallest model that does it well: the fast Nano for questions, Super for writing, Ultra only for the audit that needs the whole manual at once. Every call, with its tokens and cost, is shown in the Trace panel." /></h3>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-[0.9375rem]">
                  <thead className="text-left text-fg-muted"><tr><th className="py-2 pr-3 font-medium">Job</th><th className="py-2 pr-3 font-medium">Model</th><th className="py-2 font-medium">Runs on</th></tr></thead>
                  <tbody className="[&_td]:py-2.5 [&_td]:pr-3 [&_td]:align-top">
                    <tr><td>Read the nameplate</td><td>Nemotron 3.5 Super VL, plus a second reader</td><td>Token Factory</td></tr>
                    <tr><td>Ask questions, label steps</td><td>Nemotron 3 Nano</td><td>Token Factory</td></tr>
                    <tr><td>Search the manuals</td><td>Qwen3-Embedding-8B</td><td>Token Factory</td></tr>
                    <tr><td>Write the plan</td><td>Nemotron 3 Super</td><td>Token Factory</td></tr>
                    <tr><td>Audit against the whole manual</td><td>Nemotron 3 Ultra, 1M-token context</td><td>Token Factory</td></tr>
                    <tr><td>Weekly fleet brief</td><td>Nemotron 3.5 Lightning</td><td>Token Factory</td></tr>
                    <tr><td>Repair with no internet</td><td>Nemotron Nano 9B v2</td><td>Laptop GPU</td></tr>
                    <tr><td>Verification job, vision endpoint</td><td>Nemotron Nano 12B v2 VL</td><td>Nebius Serverless</td></tr>
                    <tr><td>Find manuals and parts online</td><td>Tavily search and extract</td><td>Tavily</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
            <Link href="/how-it-works" className="btn-ghost mt-5">The full pipeline, step by step</Link>
          </div>
        </div>
      </section>

      {/* Try */}
      <section id="try" aria-labelledby="try-h" className="scroll-mt-32 pt-36">
        <h2 id="try-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Try it, no hardware needed</h2>
        <p data-reveal style={d(60)} className="mt-4 max-w-2xl text-lg leading-relaxed">Pick a machine and a fault. Each sample runs the real pipeline live on Nebius Token Factory, from identification to the filed work order. Two of them test what Sieve must refuse.</p>
        <div data-reveal style={d(120)} className="mt-10"><SampleGallery /></div>
      </section>

      {/* Safety */}
      <section id="safety" aria-labelledby="safety-h" className="scroll-mt-32 pt-36">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] lg:gap-16">
          <div data-reveal>
            <h2 id="safety-h" className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">What Sieve refuses<Info k="safety_stop" /></h2>
            <p className="mt-4 text-lg leading-relaxed">These are rules, not suggestions a model may ignore. They fire before any model is allowed to answer, and every one is tested on each evaluation run.</p>
            <div data-ui role="note" aria-label="Example: the stop a technician sees" className="mt-8 rounded-[20px] bg-surface p-5 sm:p-6">
              <p className="text-[0.9375rem] text-fg-muted">What the technician sees when the report mentions smoke or burning</p>
              <div className="mt-3 rounded-[16px] border-2 border-stop bg-bg-elev p-4">
                <p className="flex items-center gap-2 text-lg font-semibold text-stop"><ShieldAlert className="h-5 w-5 shrink-0" aria-hidden /> Stop</p>
                <p className="mt-1.5 text-base leading-relaxed">Smoke, burning, sparks or heat damage: remove the unit from service now. Move the patient to a backup oxygen supply, switch off at the wall only if it is safe to reach, do not reuse the unit or its cord, keep the parts, and report the event to the manufacturer and the national device-safety reporting system.</p>
                <p className="mt-1.5 text-[0.9375rem] text-fg-muted">Source: manufacturer service manuals; WHO technical specifications for oxygen concentrators, 2015</p>
              </div>
            </div>
            <Link href="/limits" className="btn-ghost mt-6">Scope and safeguards</Link>
          </div>
          <ul className="space-y-4">
            <Stop i={0} title="Smoke, burning, sparks or heat damage" why="The machine is taken out of service before any repair step is shown." />
            <Stop i={1} title="Oil or grease near the oxygen path" why="Oil and grease can ignite extremely easily in oxygen and burn with explosive violence." />
            <Stop i={2} title="Opening the cabinet while plugged in" why="Rewritten to: switch off and unplug first." />
            <Stop i={3} title="Bypassing the purity alarm" why="The alarm protects the patient and is never disabled." />
            <Stop i={4} title="Live mains or capacitor work" why="Escalated to a senior engineer." />
          </ul>
        </div>
      </section>

      {/* Results */}
      <section id="results" aria-labelledby="results-h" className="scroll-mt-32 pt-36">
        <h2 id="results-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Results<Info k="benchmark" /></h2>
        <p data-reveal style={d(60)} className="mt-4 max-w-2xl text-lg leading-relaxed">Measured on data nobody on the team wrote: the closest prior work&apos;s own questions, FDA reports and real photos.</p>
        <div className="mt-12 grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <Result i={0} n="69.7%" t="on the closest prior work's own 300 repair questions, against 62.0% for plain retrieval and 17.0% for the model alone." info="Benchmark A on the INGENZI dataset, graded by a blind Nemotron 3 Super judge; a second judge from another company agreed (kappa 0.94)." />
          <Result i={1} n="62 of 62" t="real FDA reports of concentrators that smoked or caught fire: Sieve took the machine out of service before any repair step." info="Benchmark B, 74 openFDA malfunction reports selected and scored by rules committed before the run." />
          <Result i={2} n="0" t="wrong machines chosen across 57 real photos, and all 16 look-alike devices refused." info="Photos from resale listings and product pages, annotated by eye before any run. Sieve picks a device on its own only when two vision models agree." />
          <Result i={3} n="100%" t="of citations land on real manual text, because code, not the model, copies each cited sentence." info="Sieve points at numbered manual sentences instead of copying quotes; on the same cases, copied quotes resolved 88.8% of the time." />
        </div>
        <Link href="/evals" className="btn-ghost mt-10">All results and how to reproduce them</Link>
      </section>

      {/* Who */}
      <section id="who" aria-labelledby="who-h" className="scroll-mt-32 pt-36">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-center lg:gap-16">
          <figure data-reveal className="order-last lg:order-none">
            <Image src="/images/technicians.jpg" alt="Biomedical technicians in blue work coats gather around a patient monitor during a training session" width={830} height={840} sizes="(min-width: 1024px) 500px, 100vw" className="h-auto w-full rounded-[20px] object-cover" />
            <figcaption className="mt-3 text-[0.9375rem] text-fg-muted">Biomedical equipment technicians in Burundi during a hands-on training session, 2024.</figcaption>
          </figure>
          <div>
            <h2 id="who-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Who it is for</h2>
            <div className="mt-8 space-y-8">
              <Persona i={0} title="The district technician" text="Gets the manufacturer's steps now, not when the next engineer visit happens next quarter." />
              <Persona i={1} title="The nurse in charge" text="Knows in two minutes whether this is a five-minute filter clean or a call to the district." />
              <Persona i={2} title="The engineer covering 40 facilities" text="Sees every work order on one fleet view: what is down, for how long, and which parts are needed." />
            </div>
          </div>
        </div>
      </section>

      {/* Build on it */}
      <section id="build" aria-labelledby="build-h" className="scroll-mt-32 pt-36">
        <h2 id="build-h" data-reveal className="text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Build on it</h2>
        <div className="mt-10 grid gap-x-12 gap-y-10 md:grid-cols-2">
          <Feature i={0} title="Bring your own manual" k="byo" text="Upload a PDF service manual for a machine Sieve does not cover, then ask it about a fault. The plan comes from your document alone, page by page." href="/data" cta="Upload a manual" />
          <Feature i={1} title="An API and an agent tool" k="api_key" text="Create a key and call Sieve from your own software, or let an agent use its eight tools through MCP and Hermes Agent." href="/api" cta="Get an API key" />
          <Feature i={2} title="Works without internet" k="offline" text="District hospitals lose connection. The same pipeline runs on a laptop GPU with NVIDIA Nemotron Nano and the manuals already on the machine." href="/limits" cta="Scope and safeguards" />
          <Feature i={3} title="A sticker on every machine" k="sticker" text="Each repair prints a QR sticker. The next technician scans it, sees the last repair and starts on the right manual, even when the server is down." href="/machine" cta="See a machine record" />
        </div>
      </section>
    </div>
  );
}

function Stat({ n, t, s, u, i }: { n: string; t: string; s: string; u: string; i: number }) {
  return (
    <li data-reveal style={d(i)}>
      <p className="text-4xl font-semibold tracking-[-0.03em]">{n}</p>
      <p className="mt-2 text-base leading-relaxed">{t} <a className="text-accent underline underline-offset-2" href={u} target="_blank" rel="noreferrer">{s}</a></p>
    </li>
  );
}


function Stage({ i, title, text, model, tech }: { i: number; title: string; text: string; model: string; tech: string }) {
  return (
    <li data-reveal style={d(60 + i * 70)} className="grid grid-cols-[2.25rem_minmax(0,1fr)] gap-4">
      <span aria-hidden className="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-base font-semibold text-accent-fg">{i + 1}</span>
      <div>
        <h3 className="text-xl font-semibold">{title}</h3>
        <p className="mt-2 text-base leading-relaxed">{text}</p>
        <p className="mt-2 flex flex-wrap items-center gap-1 text-[0.9375rem] text-fg-muted">{model}<Info term={title} text={tech} /></p>
      </div>
    </li>
  );
}

function Stop({ i, title, why }: { i: number; title: string; why: string }) {
  return (
    <li data-reveal style={d(i * 60)} className="rounded-[18px] bg-stop/10 p-5">
      <p className="text-lg font-semibold text-stop">{title}</p>
      <p className="mt-1.5 text-base leading-relaxed">{why}</p>
    </li>
  );
}

function Result({ i, n, t, info }: { i: number; n: string; t: string; info: string }) {
  return (
    <div data-reveal style={d(i * 80)}>
      <p className="text-5xl font-semibold tracking-[-0.035em] text-accent">{n}</p>
      <p className="mt-3 text-base leading-relaxed">{t}<Info term={n} text={info} /></p>
    </div>
  );
}

function Persona({ i, title, text }: { i: number; title: string; text: string }) {
  return (
    <div data-reveal style={d(i * 80)}>
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="mt-2 text-lg leading-relaxed">{text}</p>
    </div>
  );
}

function Feature({ i, title, k, text, href, cta }: { i: number; title: string; k: Parameters<typeof Info>[0]["k"]; text: string; href: string; cta: string }) {
  return (
    <div data-reveal style={d(i * 70)}>
      <h3 className="text-xl font-semibold">{title}<Info k={k} /></h3>
      <p className="mt-2 text-lg leading-relaxed">{text}</p>
      <Link href={href} className="mt-3 inline-block text-base font-semibold text-accent underline underline-offset-4">{cta}</Link>
    </div>
  );
}

import Link from "next/link";
import { Info } from "@/components/info";
import { Explain } from "@/components/explain-mode";
import { EvalTiles } from "@/components/eval-tiles";
import { SampleGallery } from "@/components/sample-gallery";
import { ShieldAlert, Camera, Search, ClipboardCheck, FileText, Wifi, WifiOff } from "lucide-react";

export default function Landing() {
  return (
    <div className="space-y-20 pt-10">
      {/* 1. Hero */}
      <section className="space-y-6">
        <p className="eyebrow">Repair copilot for hospital equipment technicians</p>
        <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          The manual is in a drawer. The engineer is 500 km away. The oxygen machine is dead.
        </h1>
        <p className="max-w-2xl text-lg text-fg-muted">
          Sieve reads the machine&apos;s nameplate and alarm light, finds the right page of the service manual, and walks a technician through the fix with safety stops. Offline if needed.
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          <Stat n="72%" text="of broken hospital equipment in low-income countries was fixed without any imported parts" k="bmet" href="https://link.springer.com/article/10.1007/s11517-010-0630-1" src="Malkin and Keane, 2010, 2,849 repairs, 60 hospitals" />
          <Stat n="1 per million" text="biomedical engineers, at most, in two-thirds of sub-Saharan countries" k="bmet" href="https://link.springer.com/article/10.1007/s10439-017-1897-2" src="WHO Human Resources for Medical Devices, 2017" />
        </div>
        <div className="flex flex-wrap gap-3">
          <Link href="/try?sample=everflo-yellow" className="btn-primary">Try it on a sample photo</Link>
          <a href="https://youtube.com" className="btn-ghost" target="_blank" rel="noreferrer">Watch the 3-minute video</a>
        </div>
      </section>

      {/* 2. What / Why / How */}
      <section aria-labelledby="what" className="space-y-4">
        <h2 id="what" className="text-2xl font-semibold">What is this, in one minute</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Card title="What" icon={<Camera className="h-5 w-5" />}>
            A repair assistant for the people who keep hospital machines running <Info k="bmet" />. Point a phone at the machine; get the manufacturer&apos;s own steps.
          </Card>
          <Card title="Why" icon={<Search className="h-5 w-5" />}>
            Machines sit broken not because parts are missing but because the knowledge is locked in a service manual <Info k="service_manual" /> nobody has.
          </Card>
          <Card title="How" icon={<ClipboardCheck className="h-5 w-5" />}>
            Photo, up to three questions, grounded steps <Info k="grounded" /> with the page shown, safety stops <Info k="safety_stop" />, and a filed work order <Info k="work_order" />.
          </Card>
        </div>
      </section>

      {/* 3. See it work */}
      <section aria-labelledby="see" className="space-y-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 id="see" className="text-2xl font-semibold">See it work, no hardware needed</h2>
            <p className="mt-1 text-fg-muted">Pick a sample. The whole flow runs live against Nebius Token Factory; the status strip says so when it is a replay instead.</p>
          </div>
        </div>
        <SampleGallery />
      </section>

      {/* 4. Who */}
      <section aria-labelledby="who" className="space-y-4">
        <h2 id="who" className="text-2xl font-semibold">Who it is for</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Card title="The district technician">Gets the manufacturer&apos;s steps now, not when the next engineer visit happens next quarter.</Card>
          <Card title="The nurse in charge">Knows in two minutes whether this is a five-minute filter clean or a call to the district.</Card>
          <Card title="The engineer covering 40 facilities">Sees every work order on one fleet view: what is down, for how long, which parts are needed.</Card>
        </div>
      </section>

      {/* 5. Numbers */}
      <section aria-labelledby="numbers" className="space-y-4">
        <h2 id="numbers" className="text-2xl font-semibold">The numbers <Info k="benchmark" label="Why these numbers and not others?" /></h2>
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="text-left text-fg-muted"><tr><th className="p-4">Number</th><th className="p-4">What it means</th><th className="p-4">Source</th></tr></thead>
            <tbody className="[&_td]:border-t [&_td]:border-border [&_td]:p-4 [&_td]:align-top">
              <Row n="38.3%" t="of 112,040 hospital devices across 16 low- and middle-income countries were out of service." s="Perry and Malkin, 2011" u="https://pubmed.ncbi.nlm.nih.gov/21597999/" />
              <Row n="72%" t="of 2,849 repair requests in 60 hospitals were resolved without imported parts; 66 percent needed only basic skills." s="Malkin and Keane, 2010" u="https://link.springer.com/article/10.1007/s11517-010-0630-1" />
              <Row n="68%" t="of sub-Saharan countries have at most one biomedical engineer per million people." s="WHO HRMD, 2017" u="https://link.springer.com/article/10.1007/s10439-017-1897-2" />
              <Row n="5 billion" t="people lack access to safe, affordable medical oxygen." s="Lancet Global Health Commission, 2025" u="https://www.thelancet.com/journals/langlo/article/PIIS2214-109X(24)00496-0/fulltext" />
              <Row n="66.7%" t="of primary facilities in a 39-country survey had a working oxygen concentrator." s="Lancet Global Health, 2025" u="https://pmc.ncbi.nlm.nih.gov/articles/PMC11954661/" />
              <Row n="2x" t="Malawi doubled its working concentrator fleet by repairing 649 machines; most faults were trivial." s="OpenO2, 2022" u="https://www.openo2.org/concentrator-graveyard" />
            </tbody>
          </table>
        </div>
      </section>

      {/* 6. How the AI works */}
      <section aria-labelledby="how" className="space-y-4">
        <h2 id="how" className="text-2xl font-semibold">How the AI works <Info k="tier_routing" /></h2>
        <div className="grid gap-3 md:grid-cols-5">
          <Step n={1} title="Look" plain="Reads the nameplate and the lights from your photo." technical="NVIDIA Nemotron Nano VL on a Nebius Serverless Endpoint describes fields only; it never decides." />
          <Step n={2} title="Ask" plain="Asks up to three questions that change the answer." technical="Nemotron 3 Nano, thinking off, picks from a finite question bank." />
          <Step n={3} title="Find" plain="Finds the right pages of the real service manual." technical="Device-scoped hybrid retrieval over 9,458 indexed pages; FTS5 BM25 plus Nemotron embed and rerank." />
          <Step n={4} title="Check" plain="A second, larger model verifies every step against the whole manual, and a rules engine stops dangerous steps." technical="Nemotron 3 Super drafts; a deterministic verifier confirms each quote exists on the cited page; Nemotron 3 Ultra audits with the full manual in its one-million-token context; YAML rules gate input and output." />
          <Step n={5} title="Record" plain="Writes the work order into the hospital's log." technical="WHO CMMS-aligned schema; openFDA recall and MAUDE enrichment; Tavily for manuals and parts." />
        </div>
      </section>

      {/* 7. Safety */}
      <section aria-labelledby="safety" className="space-y-4">
        <h2 id="safety" className="text-2xl font-semibold">What Sieve refuses <Info k="safety_stop" /></h2>
        <p className="max-w-2xl text-fg-muted">These are not suggestions the model declines. They are rules that fire before any model is allowed to answer, and we measure them.</p>
        <div className="grid gap-3 md:grid-cols-2">
          <Stop title="Oil or grease near the oxygen path" why="Oxygen-enriched environments turn lubricants into a fire hazard." src="WHO 2015 specification; manufacturer warnings" />
          <Stop title="Opening the cabinet while plugged in" why="Rewritten to: switch off and unplug first." src="Manufacturer service manuals" />
          <Stop title="Bypassing the purity alarm" why="The alarm protects the patient. Never disabled." src="WHO 2015: alarm at 82 percent" />
          <Stop title="Live mains or capacitor work" why="Escalated to a senior engineer." src="BMET training notes; manufacturer warnings" />
        </div>
      </section>

      {/* 8. Evals */}
      <section aria-labelledby="evals" className="space-y-4">
        <h2 id="evals" className="text-2xl font-semibold">Evaluation results <Info k="negative_control" /></h2>
        <EvalTiles />
        <Link href="/evals" className="btn-ghost">See full results and how to reproduce them</Link>
      </section>

      {/* 9. BYO + 10. API + 11. Built with + 12. Limits */}
      <section className="grid gap-4 md:grid-cols-2">
        <Card title={<>Bring your own manual <Info k="byo" /></>} icon={<FileText className="h-5 w-5" />}>
          Have a manual we do not? Upload it. It is indexed in your own workspace, never mixed with others, and you can export or delete it any time.
          <div className="mt-3"><Link href="/data" className="btn-ghost">Upload a manual</Link></div>
        </Card>
        <Card title={<>Use Sieve as a service <Info k="api_key" /></>} icon={<ClipboardCheck className="h-5 w-5" />}>
          Call it from your own software with an API key, or let your agent use it as a tool through MCP <Info k="mcp" />.
          <div className="mt-3"><Link href="/api" className="btn-ghost">Get an API key and code samples</Link></div>
        </Card>
        <Card title={<>Works offline <Info k="offline" /></>} icon={<WifiOff className="h-5 w-5" />}>
          District hospitals lose internet. Sieve runs on a laptop with an open Nemotron model and the manuals already on the machine. We publish the accuracy difference.
        </Card>
        <Card title="Built with" icon={<Wifi className="h-5 w-5" />}>
          Nebius Token Factory for every language-model call. NVIDIA Nemotron 3 Nano, Super and Ultra. NVIDIA Nemotron Nano VL for vision. Nebius Serverless Endpoints and Jobs. Tavily. openFDA.
          <div className="mt-3"><Link href="/about" className="btn-ghost">Our feedback on these tools</Link></div>
        </Card>
      </section>

      <section aria-labelledby="limits" className="space-y-3">
        <h2 id="limits" className="text-2xl font-semibold">Limits, honestly</h2>
        <p className="max-w-2xl text-fg-muted">We publish limits as measurements, not promises: offline accuracy versus cloud, photo identification on worn nameplates, and the device classes covered today (oxygen concentrators first; suction pumps and pulse oximeters indexed). Sieve is equipment-maintenance guidance for trained staff, not medical advice, and it is not a replacement for an engineer.</p>
        <Link href="/limits" className="btn-ghost">Read the limits page</Link>
      </section>
    </div>
  );
}

function Stat({ n, text, k, href, src }: { n: string; text: string; k: "bmet"; href: string; src: string }) {
  return (
    <div className="card">
      <p className="text-4xl font-semibold tracking-tight">{n} <Info k={k} /></p>
      <p className="mt-2 text-fg">{text}</p>
      <a className="mt-2 inline-block text-sm text-accent underline-offset-2 hover:underline" href={href} target="_blank" rel="noreferrer">{src}</a>
    </div>
  );
}

function Card({ title, icon, children }: { title: React.ReactNode; icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 text-fg"><span className="text-accent">{icon}</span><h3 className="font-semibold">{title}</h3></div>
      <p className="mt-2 text-fg-muted">{children}</p>
    </div>
  );
}

function Row({ n, t, s, u }: { n: string; t: string; s: string; u: string }) {
  return (
    <tr><td className="whitespace-nowrap font-semibold">{n}</td><td>{t}</td><td><a className="text-accent underline-offset-2 hover:underline" href={u} target="_blank" rel="noreferrer">{s}</a></td></tr>
  );
}

function Step({ n, title, plain, technical }: { n: number; title: string; plain: string; technical: string }) {
  return (
    <div className="card">
      <p className="eyebrow">Step {n}</p>
      <h3 className="mt-1 font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-fg-muted"><Explain plain={plain} technical={technical} /></p>
    </div>
  );
}

function Stop({ title, why, src }: { title: string; why: string; src: string }) {
  return (
    <div className="rounded-[16px] border-2 border-stop bg-bg-elev p-4" role="note">
      <div className="flex items-center gap-2 font-semibold text-stop"><ShieldAlert className="h-5 w-5" aria-hidden /> Stop: {title}</div>
      <p className="mt-1 text-sm text-fg">{why}</p>
      <p className="mt-1 text-xs text-fg-muted">Source: {src}</p>
    </div>
  );
}

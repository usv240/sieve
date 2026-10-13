export const metadata = { title: "About" };

export default function About() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">About Sieve</h1>
      <p className="max-w-2xl text-fg-muted">Built for the Nebius x NVIDIA Global AI Hackathon, October 2026, by a one-person code team. Apache-2.0. Source at <a className="text-accent" href="https://github.com/usv240/sieve">github.com/usv240/sieve</a>.</p>
      <section className="card space-y-2">
        <h2 className="font-semibold">Prior art, named</h2>
        <p className="text-sm text-fg-muted">INGENZI Tech (MICCAI 2025 workshop) built a text chatbot over one ultrasound manual with a closed model and reported 100 percent on error codes and 80 percent on procedures with no baseline. Jua (Devpost 2023) did document Q&A with GPT-3.5. Sieve adds photo-first identification, a cited indicator registry, deterministic safety gates, an independent whole-manual audit, recall checks, a filed work order and fleet view, offline mode, and an external evaluation with baselines, including on INGENZI&apos;s own published dataset.</p>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Where the models run</h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-fg-muted">
          <li>Nebius Token Factory: Nemotron 3 Nano and 3.5 Lightning (fast tier), Nemotron 3 Super (synthesis), Nemotron 3 Ultra (audit with the whole manual in a one-million-token context).</li>
          <li>Nebius Serverless Endpoint: NVIDIA Nemotron Nano VL on vLLM for nameplate and panel reading.</li>
          <li>Nebius Serverless Job: manual ingestion with Nemotron embed-vl and rerank-vl.</li>
          <li>Tavily: manual discovery and parts lookup. openFDA: recalls and malfunction reports.</li>
        </ul>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Feedback on the tools</h2>
        <p className="text-sm text-fg-muted">Kept as a running log in the repository (FEEDBACK.md): onboarding time, what worked, what needs work, whether we would build with them again.</p>
      </section>
    </div>
  );
}

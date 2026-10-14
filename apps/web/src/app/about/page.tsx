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
          <li>Nebius Token Factory: image models for nameplate and panel reading (the NVIDIA Nemotron Nano VL endpoint is prepared but needs AI Cloud billing), and Qwen3-Embedding-8B for hybrid retrieval over 2,994 concentrator pages.</li>
          <li>Laptop: manual ingestion (33 seconds for 9,458 pages) and the offline mode on a 4-bit Nemotron 3 Nano via llama.cpp. The Serverless Job and Endpoint manifests are in the repo, ready for AI Cloud.</li>
          <li>Tavily: manual discovery, extraction and parts lookup. openFDA: recalls and malfunction reports. Hermes Agent: chat and cron surface. NVIDIA OpenShell: sandboxed run with brokered credentials, demonstrated.</li>
        </ul>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Who has tested this</h2>
        <p className="text-sm text-fg-muted">No practising biomedical technician has used Sieve yet; this is a hackathon build by one developer. What stands in for a user is published practitioner data: the Malawi and Gabon health-worker surveys that measured the knowledge gap, the NEST360 survey of 63 hospitals that found no one measures equipment downtime, and the two external benchmarks on the Evals page, one of which is the published dataset of the closest prior work. We say this plainly because a measured limit is a property of the product and an unstated one is a liability.</p>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Feedback on the tools</h2>
        <p className="text-sm text-fg-muted">Kept as a running log in the repository (FEEDBACK.md): onboarding time, what worked, what needs work, whether we would build with them again.</p>
      </section>
    </div>
  );
}

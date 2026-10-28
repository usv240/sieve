"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";

/**
 * While the pipeline runs: what it is doing, in order, and how long it has taken. Stage timings are typical
 * values from recorded runs, so the list shows what usually happens next rather than claiming live telemetry.
 */
export function Progress({ title, stages }: { title: string; stages: { at: number; text: string }[] }) {
  const [s, setS] = useState(0);
  useEffect(() => {
    const t0 = Date.now();
    const id = setInterval(() => setS(Math.floor((Date.now() - t0) / 1000)), 250);
    return () => clearInterval(id);
  }, []);
  const current = stages.reduce((acc, st, i) => (s >= st.at ? i : acc), 0);
  return (
    <div className="rounded-[16px] bg-surface p-4">
      <div className="flex items-baseline justify-between gap-3">
        <p className="font-semibold">{title}</p>
        <span aria-hidden className="tabular-nums text-[0.9375rem] text-fg-muted">{s} s</span>
      </div>
      <div aria-hidden className="mt-3 h-1 overflow-hidden rounded-full bg-fg/10"><div className="progress-bar h-full w-1/3 rounded-full bg-accent" /></div>
      <ol className="mt-3 space-y-1.5 text-[0.9375rem]">
        {stages.map((st, i) => (
          <li key={st.text} className={`flex items-start gap-2 ${i > current ? "text-fg-muted" : ""}`}>
            <span aria-hidden className="mt-1 flex h-4 w-4 shrink-0 items-center justify-center">
              {i < current ? <Check className="h-4 w-4 text-ok" /> : <span className={`h-2 w-2 rounded-full ${i === current ? "pulse bg-accent" : "bg-fg/25"}`} />}
            </span>
            <span role={i === current ? "status" : undefined}>{st.text}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

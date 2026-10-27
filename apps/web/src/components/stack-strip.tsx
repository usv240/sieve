import { Info } from "@/components/info";
import { STACK } from "@/lib/stack";

const DOT = { live: "bg-ok", laptop: "bg-info", prepared: "bg-border" } as const;
const WORD = { live: "runs live in this app", laptop: "verified on our laptop", prepared: "prepared, not run" } as const;

/** The sponsor stack, on every page. Hover or tap the i on any item to see what it does here. */
export function StackStrip({ compact = false }: { compact?: boolean }) {
  return (
    <section aria-labelledby="stack-h" className={compact ? "space-y-3" : "space-y-4"}>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="stack-h" className={compact ? "text-sm font-semibold text-fg" : "text-2xl font-semibold"}>Built with</h2>
        <p className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-fg-muted">
          {(Object.keys(WORD) as (keyof typeof WORD)[]).map((s) => (
            <span key={s} className="inline-flex items-center gap-1.5"><span aria-hidden className={`inline-block h-2 w-2 rounded-full ${DOT[s]}`} />{WORD[s]}</span>
          ))}
        </p>
      </div>
      <ul className="flex flex-wrap gap-2">
        {STACK.map((s) => (
          <li key={s.name} className="inline-flex items-center gap-1.5 rounded-full border border-border bg-bg-elev py-1 pl-3 pr-1 text-sm">
            <span aria-hidden className={`inline-block h-2 w-2 shrink-0 rounded-full ${DOT[s.status]}`} />
            <span>{s.name}</span>
            <span className="sr-only">: {WORD[s.status]}</span>
            <Info term={s.name} text={`${s.role} Status: ${WORD[s.status]}.`} label={`What does ${s.name} do here?`} />
          </li>
        ))}
      </ul>
    </section>
  );
}

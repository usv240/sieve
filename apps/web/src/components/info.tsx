"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Info as InfoIcon, X } from "lucide-react";
import { GLOSSARY, type GlossaryEntry, type GlossaryKey } from "@/lib/glossary";
import { useExplain } from "@/components/explain-mode";

/**
 * The "i" button. One plain sentence on hover or tap; "Learn more" opens a drawer with the full entry,
 * the technical note (shown by default in Technical explain mode) and references. All copy comes from glossary.ts.
 */
export function Info({ k, label }: { k: GlossaryKey; label?: string }) {
  const g: GlossaryEntry = GLOSSARY[k];
  const [open, setOpen] = useState(false);
  const [drawer, setDrawer] = useState(false);
  const id = useId();
  const ref = useRef<HTMLSpanElement>(null);
  const { mode } = useExplain();

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  return (
    <span ref={ref} className="relative inline-flex items-center align-middle">
      <button
        type="button"
        aria-label={label ?? `What is ${g.term}?`}
        aria-describedby={open ? id : undefined}
        onClick={() => setOpen((v) => !v)}
        onMouseEnter={() => setOpen(true)}
        className="ml-1 inline-flex h-6 w-6 min-h-0 items-center justify-center rounded-full text-fg-muted hover:text-accent focus-visible:ring-2 focus-visible:ring-accent"
      >
        <InfoIcon className="h-4 w-4" aria-hidden />
      </button>
      {open && (
        <span role="tooltip" id={id} className="absolute left-1/2 top-full z-40 mt-2 w-72 -translate-x-1/2 rounded-xl border border-border bg-bg-elev p-3 text-left text-sm shadow-lg">
          <span className="block font-semibold">{g.term}</span>
          <span className="mt-1 block text-fg-muted">{mode === "technical" && g.technical ? g.technical : g.plain}</span>
          <button type="button" className="mt-2 text-sm font-medium text-accent underline-offset-2 hover:underline" onClick={() => { setDrawer(true); setOpen(false); }}>
            Learn more
          </button>
        </span>
      )}
      {drawer && (
        <div role="dialog" aria-modal="true" aria-labelledby={`${id}-title`} className="fixed inset-0 z-50 flex justify-end bg-black/40" onClick={() => setDrawer(false)}>
          <div className="h-full w-full max-w-md overflow-y-auto bg-bg-elev p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between gap-4">
              <h2 id={`${id}-title`} className="text-xl font-semibold">{g.term}</h2>
              <button type="button" aria-label="Close" className="btn-ghost h-10 w-10 min-h-0 px-0" onClick={() => setDrawer(false)}><X className="h-5 w-5" /></button>
            </div>
            <p className="mt-4 text-fg">{g.plain}</p>
            {g.technical && (
              <div className="mt-4">
                <p className="eyebrow">Technical</p>
                <p className="mt-1 text-fg-muted">{g.technical}</p>
              </div>
            )}
            {g.refs?.length ? (
              <div className="mt-4">
                <p className="eyebrow">References</p>
                <ul className="mt-1 space-y-1 text-sm">
                  {g.refs.map((r) => (
                    <li key={r.url}><a className="text-accent underline-offset-2 hover:underline" href={r.url} target="_blank" rel="noreferrer">{r.label}</a></li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </span>
  );
}

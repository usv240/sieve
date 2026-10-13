"use client";

import { createContext, useContext, useEffect, useState } from "react";

type Mode = "plain" | "technical";
const Ctx = createContext<{ mode: Mode; setMode: (m: Mode) => void }>({ mode: "plain", setMode: () => {} });

/** Plain or Technical wording for every card. A nurse and an NVIDIA engineer read the same screen. */
export function ExplainProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<Mode>("plain");
  useEffect(() => {
    const saved = typeof window !== "undefined" ? (localStorage.getItem("sieve.explain") as Mode | null) : null;
    if (saved === "plain" || saved === "technical") setMode(saved);
  }, []);
  const set = (m: Mode) => { setMode(m); localStorage.setItem("sieve.explain", m); };
  return <Ctx.Provider value={{ mode, setMode: set }}>{children}</Ctx.Provider>;
}

export function useExplain() { return useContext(Ctx); }

export function ExplainToggle() {
  const { mode, setMode } = useExplain();
  return (
    <div role="group" aria-label="Explain mode" className="inline-flex rounded-xl border border-border bg-bg-elev p-0.5 text-sm">
      {(["plain", "technical"] as Mode[]).map((m) => (
        <button key={m} type="button" aria-pressed={mode === m} onClick={() => setMode(m)}
          className={`min-h-0 rounded-lg px-3 py-1.5 capitalize ${mode === m ? "bg-accent text-accent-fg" : "text-fg-muted hover:text-fg"}`}>
          {m}
        </button>
      ))}
    </div>
  );
}

/** Renders plain or technical text depending on the mode. */
export function Explain({ plain, technical }: { plain: React.ReactNode; technical: React.ReactNode }) {
  const { mode } = useExplain();
  return <>{mode === "technical" ? technical : plain}</>;
}

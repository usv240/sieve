"use client";

import Link from "next/link";
import { ExplainProvider, ExplainToggle } from "@/components/explain-mode";
import { ThemeToggle } from "@/components/theme-toggle";
import { StatusStrip } from "@/components/status-strip";

const nav = [
  { href: "/try", label: "Try it" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/evals", label: "Evals" },
  { href: "/api", label: "API" },
  { href: "/limits", label: "Limits" },
];

export function SiteHeader() {
  return (
    <ExplainProvider>
      <header className="sticky top-0 z-30 border-b border-border bg-bg/90 backdrop-blur">
        <div className="mx-auto flex max-w-[1100px] flex-wrap items-center gap-3 px-4 py-3 sm:px-6">
          <Link href="/" className="mr-2 flex items-center gap-2 text-lg font-semibold tracking-tight">
            <span aria-hidden className="inline-block h-6 w-6 rounded-md bg-accent" />
            Sieve
          </Link>
          <nav aria-label="Primary" className="order-last flex w-full gap-1 overflow-x-auto sm:order-none sm:w-auto">
            {nav.map((n) => (
              <Link key={n.href} href={n.href} className="shrink-0 whitespace-nowrap rounded-lg px-3 py-2 text-sm text-fg-muted hover:bg-bg-elev hover:text-fg">
                {n.label}
              </Link>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <ExplainToggle />
            <ThemeToggle />
          </div>
        </div>
        <StatusStrip />
      </header>
    </ExplainProvider>
  );
}

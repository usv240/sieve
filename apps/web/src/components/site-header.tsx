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
  { href: "/limits", label: "Safeguards" },
];

export function SiteHeader() {
  return (
    <ExplainProvider>
      <header className="z-30 bg-bg sm:sticky sm:top-0">
        <div className="mx-auto flex max-w-[1100px] flex-wrap items-center gap-3 px-4 py-3 sm:px-6">
          <Link href="/" className="mr-2 flex items-center gap-2 text-lg font-semibold tracking-tight">
            <span aria-hidden className="inline-block h-6 w-6 rounded-md bg-accent" />
            Sieve
          </Link>
          <nav aria-label="Primary" className="order-last -mx-3 flex w-full flex-wrap gap-x-0.5 sm:order-none sm:mx-0 sm:w-auto">
            {nav.map((n) => (
              <Link key={n.href} href={n.href} className="shrink-0 whitespace-nowrap rounded-full px-3 py-2 text-[0.9375rem] text-fg-muted transition-colors hover:bg-surface hover:text-fg">
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

import { StackStrip } from "@/components/stack-strip";

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-bg-elev/60">
      <div className="mx-auto max-w-[1100px] px-4 pt-8 sm:px-6"><StackStrip compact /></div>
      <div className="mx-auto flex max-w-[1100px] flex-col gap-3 px-4 pb-8 pt-6 text-sm text-fg-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p>Built on Nebius Token Factory with NVIDIA Nemotron 3 Nano, Super, Ultra, 3.5 Lightning and 3.5 Super VL. Apache-2.0.</p>
        <nav aria-label="Footer" className="flex flex-wrap gap-4">
          <a className="hover:text-fg" href="https://github.com/usv240/sieve" target="_blank" rel="noreferrer">GitHub</a>
          <a className="hover:text-fg" href="/references">References</a>
          <a className="hover:text-fg" href="/about">About and feedback</a>
        </nav>
      </div>
    </footer>
  );
}

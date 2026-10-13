export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-bg-elev/60">
      <div className="mx-auto flex max-w-[1100px] flex-col gap-3 px-4 py-8 text-sm text-fg-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p>Built on Nebius Token Factory with NVIDIA Nemotron 3 Nano, Super and Ultra. Apache-2.0.</p>
        <nav aria-label="Footer" className="flex flex-wrap gap-4">
          <a className="hover:text-fg" href="https://github.com/usv240/sieve" target="_blank" rel="noreferrer">GitHub</a>
          <a className="hover:text-fg" href="/references">References</a>
          <a className="hover:text-fg" href="/about">About and feedback</a>
        </nav>
      </div>
    </footer>
  );
}

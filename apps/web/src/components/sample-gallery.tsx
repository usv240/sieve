import Link from "next/link";
import { SAMPLES } from "@/lib/samples";

export function SampleGallery() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {SAMPLES.map((s) => (
        <Link key={s.id} href={`/try?sample=${s.id}`} className="card group flex flex-col gap-2 hover:border-accent">
          <div className="flex items-center gap-3">
            <span aria-hidden className={`inline-block h-3 w-3 rounded-full ${s.dot}`} />
            <span className="font-semibold group-hover:text-accent">{s.title}</span>
          </div>
          <p className="text-sm text-fg-muted">{s.blurb}</p>
          <p className="mt-auto text-xs text-fg-muted">{s.kind}</p>
        </Link>
      ))}
    </div>
  );
}

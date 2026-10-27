import Link from "next/link";
import { SAMPLES } from "@/lib/samples";

export function SampleGallery() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {SAMPLES.map((s) => (
        <div key={s.id} className="card group flex flex-col gap-2 hover:border-accent">
          <Link href={`/try?sample=${s.id}`} className="flex flex-col gap-2">
            <span className="flex items-center gap-3">
              <span aria-hidden className={`inline-block h-3 w-3 rounded-full ${s.dot}`} />
              <span className="font-semibold group-hover:text-accent">{s.title}</span>
            </span>
            <span className="text-sm text-fg-muted">{s.blurb}</span>
            <span className="text-xs text-fg-muted">{s.kind}</span>
          </Link>
          <a className="mt-auto inline-flex w-fit items-center gap-1 text-xs text-accent underline underline-offset-2" download={`${s.id}.json`}
            href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(s, null, 2))}`}>Download this preset as JSON</a>
        </div>
      ))}
    </div>
  );
}

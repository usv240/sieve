import Link from "next/link";
import { SAMPLES } from "@/lib/samples";

export function SampleGallery() {
  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {SAMPLES.map((s) => (
        <li key={s.id} className="lift flex flex-col rounded-[20px] bg-surface">
          <Link href={`/try?sample=${s.id}`} className="group flex flex-1 flex-col gap-2 p-5">
            <span className="flex items-center gap-3">
              <span aria-hidden className={`inline-block h-3 w-3 shrink-0 rounded-full ${s.dot}`} />
              <span className="text-lg font-semibold leading-snug group-hover:text-accent">{s.title}</span>
            </span>
            <span className="text-base leading-relaxed">{s.blurb}</span>
            <span className="text-[0.875rem] leading-relaxed text-fg-muted">{s.kind}</span>
            <span className="mt-auto pt-2 text-[0.9375rem] font-semibold text-accent">Run this sample</span>
          </Link>
          <a className="px-5 pb-4 text-[0.875rem] text-fg-muted underline underline-offset-2 hover:text-fg" download={`${s.id}.json`}
            href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(s, null, 2))}`}>Download as JSON</a>
        </li>
      ))}
    </ul>
  );
}

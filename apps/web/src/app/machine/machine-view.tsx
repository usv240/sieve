"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { QrCode, Wrench } from "lucide-react";
import { apiUrl } from "@/lib/api";
import { Info } from "@/components/info";

type Rec = { id: string; created_at: number; device_id: string; reported_fault: string; outcome: string };

export function MachineView() {
  const p = useSearchParams();
  const device = p.get("d");
  const [others, setOthers] = useState<Rec[] | null>(null);

  useEffect(() => {
    if (!device) return;
    fetch(apiUrl("/v1/records")).then((r) => r.json()).then((rs: Rec[]) => setOthers(rs.filter((r) => r.device_id === device && !r.id.startsWith(p.get("w") ?? "~")).sort((a, b) => b.created_at - a.created_at).slice(0, 5))).catch(() => setOthers(null));
  }, [device, p]);

  if (!device) {
    return (
      <div className="card max-w-2xl space-y-3">
        <p className="flex items-center gap-2 font-semibold"><QrCode className="h-5 w-5" aria-hidden /> Machine stickers <Info k="sticker" /></p>
        <p className="text-fg-muted">After a repair, Sieve prints a sticker with a QR code for the machine itself. Scanning it opens this page with the last repair and starts the next one on the right manual, without identifying the machine again.</p>
        <Link className="btn-primary" href="/try?sample=everflo-yellow">Run a repair and print a sticker</Link>
      </div>
    );
  }

  const outcome = (p.get("o") ?? "open").replace("_", " ");
  return (
    <div className="grid max-w-3xl gap-4">
      <div className="card space-y-3">
        <p className="text-sm text-fg-muted">Scanned from the sticker on this machine</p>
        <h1 className="text-2xl font-semibold">{p.get("l") ?? device}</h1>
        <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-[auto_1fr]">
          <dt className="text-fg-muted">Last repair</dt><dd>{p.get("t")}: <span className="font-semibold">{outcome}</span></dd>
          <dt className="text-fg-muted">What was wrong</dt><dd>{p.get("s")}</dd>
          {Number(p.get("n")) > 0 && <><dt className="text-fg-muted">Checks done</dt><dd>{p.get("n")} steps from the service manual</dd></>}
          <dt className="text-fg-muted">Work order</dt><dd className="font-mono">{p.get("w")}</dd>
        </dl>
        <p className="text-xs text-fg-muted">This record is stored in the sticker itself, so it opens even if the hospital&apos;s server is down.</p>
        <Link className="btn-primary" href={`/try?device=${encodeURIComponent(device)}`}><Wrench className="h-4 w-4" aria-hidden /> Start the next repair on this machine</Link>
      </div>
      {others && others.length > 0 && (
        <div className="card text-sm">
          <p className="font-semibold">Other repairs of this model in the fleet log</p>
          <ul className="mt-2 space-y-1 text-fg-muted">
            {others.map((r) => <li key={r.id}>{new Date(r.created_at * 1000).toISOString().slice(0, 10)}: {r.outcome.replace("_", " ")}. {r.reported_fault.slice(0, 120)}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

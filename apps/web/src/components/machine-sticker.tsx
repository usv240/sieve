"use client";

import { useEffect, useState } from "react";
import QRCode from "qrcode";
import { Printer } from "lucide-react";
import { Info } from "@/components/info";

export type StickerRecord = { device_id: string; label: string; date: string; outcome: string; fault: string; steps: number; wo: string };

/** The sticker carries the record in its own link, so a scan works even when the hospital's server or the internet is down. */
export function stickerUrl(origin: string, r: StickerRecord): string {
  const q = new URLSearchParams({ d: r.device_id, l: r.label, t: r.date, o: r.outcome, s: r.fault.length > 90 ? `${r.fault.slice(0, 88).trimEnd()}…` : r.fault, n: String(r.steps), w: r.wo });
  return `${origin}/machine?${q.toString()}`;
}

export function MachineSticker({ record }: { record: StickerRecord }) {
  const [svg, setSvg] = useState<string>("");
  const [url, setUrl] = useState<string>("");

  useEffect(() => {
    const u = stickerUrl(window.location.origin, record);
    setUrl(u);
    QRCode.toString(u, { type: "svg", errorCorrectionLevel: "M", margin: 1, color: { dark: "#000000", light: "#ffffff" } }).then(setSvg).catch(() => setSvg(""));
  }, [record]);

  return (
    <div className="mt-4 space-y-3">
      <p className="text-sm font-semibold">Stick the repair on the machine <Info k="sticker" /></p>
      <div className="sticker flex max-w-sm items-center gap-4 rounded-[12px] border-2 border-dashed border-fg bg-white p-4 text-black">
        <div className="h-28 w-28 shrink-0" role="img" aria-label="QR code linking to this machine's last repair" dangerouslySetInnerHTML={{ __html: svg }} />
        <div className="min-w-0 space-y-1 text-xs leading-snug">
          <p className="text-sm font-semibold">{record.label}</p>
          <p>Last repair {record.date}: <span className="font-semibold">{record.outcome.replace("_", " ")}</span></p>
          <p className="line-clamp-2">{record.fault}</p>
          <p className="font-mono">WO {record.wo}</p>
          <p>Scan before the next repair.</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="btn-ghost" onClick={() => window.print()}><Printer className="h-4 w-4" aria-hidden /> Print sticker</button>
        {url && <a className="btn-ghost" href={url} target="_blank" rel="noreferrer">Open what the scan shows</a>}
      </div>
    </div>
  );
}

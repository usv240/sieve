"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";

type Indicator = { id: string; state: string; meaning: string; cite: { doc: string; page: number } };
type Device = { id: string; manufacturer: string; model: string; indicators: Indicator[] };

/**
 * Training Mode: a simulated front panel driven by the registry's cited indicator table.
 * Always labelled SIMULATOR. Replaces a physical unit in the demo; gives trainees unlimited practice faults.
 */
export function TrainingPanel({ onPick }: { onPick: (deviceId: string, indicatorId: string) => void }) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [devId, setDevId] = useState<string>("philips-everflo");
  const [indId, setIndId] = useState<string | null>(null);
  const [tick, setTick] = useState(false);
  const [ask, setAsk] = useState("");
  const [twin, setTwin] = useState<{ reply: { lights: { colour: string; state: string }[]; alarm: string; after_minutes: number; explanation: string; cite: { doc: string; page: number; quote: string } }; citation_verified: boolean } | null>(null);
  const [asking, setAsking] = useState(false);
  async function askMachine() {
    if (!ask.trim()) return;
    setAsking(true);
    try {
      const r = await fetch(apiUrl("/v1/twin"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ device_id: devId, action: ask, hidden_fault: null }) });
      setTwin(await r.json());
    } finally { setAsking(false); }
  }
  useEffect(() => { fetch(apiUrl("/v1/devices")).then((r) => r.json()).then((ds: Device[]) => setDevices(ds.filter((d) => d.indicators.length))).catch(() => {}); }, []);
  useEffect(() => { const t = setInterval(() => setTick((v) => !v), 600); return () => clearInterval(t); }, []);
  const dev = devices.find((d) => d.id === devId);
  const ind = dev?.indicators.find((i) => i.id === indId);
  const s = (ind?.state ?? "").toLowerCase();
  const yellowOn = s.includes("yellow") && (!s.includes("yellow led blinking") || tick) && !s.includes("yellow low oxygen light will turn off");
  const yellowBlink = s.includes("yellow led blinking");
  const redBlink = s.includes("red led blinking") || s.includes("blinking with pulsing") || s.includes("red service required light blinking");
  const redOn = (s.includes("red led on") || s.includes("red service required light on") || redBlink) && (!redBlink || tick);
  const greenOn = !!ind && !s.includes("no leds") && !redOn && !s.includes("red service required light on");
  const beeping = s.includes("beep") || s.includes("alarm beeping");

  return (
    <div className="rounded-[16px] border border-dashed border-accent p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="font-semibold">Training Mode <span className="ml-2 rounded bg-caution/20 px-2 py-0.5 text-xs font-semibold uppercase text-fg">Simulator</span></p>
        <select aria-label="Device" className="rounded-xl border border-border bg-bg-elev px-3 py-2 text-sm" value={devId} onChange={(e) => { setDevId(e.target.value); setIndId(null); }}>
          {devices.map((d) => <option key={d.id} value={d.id}>{d.manufacturer} {d.model}</option>)}
        </select>
      </div>
      {/* Panel */}
      <svg viewBox="0 0 320 120" role="img" aria-label={`Simulated front panel: ${ind?.state ?? "idle"}`} className="mt-3 w-full max-w-md rounded-xl border border-border bg-[#2a2d31]">
        <rect x="0" y="0" width="320" height="120" rx="12" fill="#2a2d31" />
        <text x="16" y="24" fill="#cfd3d8" fontSize="11" fontFamily="sans-serif">{dev ? `${dev.manufacturer} ${dev.model}` : "Select a device"}</text>
        <text x="236" y="24" fill="#f0b429" fontSize="9" fontFamily="sans-serif">SIMULATOR</text>
        <circle cx="40" cy="70" r="10" fill={greenOn ? "#39d98a" : "#1d3a2a"} />
        <text x="40" y="100" textAnchor="middle" fill="#cfd3d8" fontSize="9" fontFamily="sans-serif">Normal</text>
        <circle cx="100" cy="70" r="10" fill={yellowOn || (yellowBlink && tick) ? "#f5c518" : "#3d3a1a"} />
        <text x="100" y="100" textAnchor="middle" fill="#cfd3d8" fontSize="9" fontFamily="sans-serif">Low O2</text>
        <circle cx="160" cy="70" r="10" fill={redOn ? "#ff4d4f" : "#3a1d1d"} />
        <text x="160" y="100" textAnchor="middle" fill="#cfd3d8" fontSize="9" fontFamily="sans-serif">Service</text>
        <rect x="220" y="48" width="70" height="44" rx="6" fill="#1b1e22" stroke="#444" />
        <text x="255" y="75" textAnchor="middle" fill={beeping && tick ? "#ff4d4f" : "#777"} fontSize="10" fontFamily="sans-serif">{beeping ? "BEEP" : "quiet"}</text>
      </svg>
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {dev?.indicators.map((i) => (
          <button key={i.id} onClick={() => setIndId(i.id)} className={`rounded-xl border p-2 text-left text-sm ${indId === i.id ? "border-accent" : "border-border"}`}>
            <span className="font-medium">{i.state}</span>
            <span className="block text-xs text-fg-muted">Manual p{i.cite.page}</span>
          </button>
        ))}
      </div>
      <div className="mt-4 rounded-xl border border-border p-3">
        <p className="text-sm font-semibold">Ask the machine</p>
        <p className="text-xs text-fg-muted">The manual talks back: describe what you do to the unit and it answers as its manual says it would, with the page. Nemotron 3 Nano on Nebius Token Factory.</p>
        <div className="mt-2 flex gap-2">
          <input className="inp" placeholder="I kink the cannula tubing tightly" value={ask} onChange={(e) => setAsk(e.target.value)} onKeyDown={(e) => e.key === "Enter" && askMachine()} />
          <button className="btn-primary min-h-0 px-3 py-1.5 text-sm" onClick={askMachine} disabled={asking}>{asking ? "Thinking…" : "Ask"}</button>
        </div>
        {twin?.reply && (
          <div className="mt-2 text-sm">
            <p><b>Lights:</b> {twin.reply.lights.map((l) => `${l.colour} ${l.state}`).join(", ")} · <b>Alarm:</b> {twin.reply.alarm} · after {twin.reply.after_minutes} min</p>
            <p className="mt-1 text-fg-muted">{twin.reply.explanation}</p>
            <blockquote className="quote mt-1 text-xs">“{twin.reply.cite.quote}”<footer className="text-fg-muted">{twin.reply.cite.doc}, page {twin.reply.cite.page} · {twin.citation_verified ? "quote verified on page" : "quote not verified"}</footer></blockquote>
          </div>
        )}
      </div>
      {ind && (
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-sm">
          <span className="text-fg-muted">Behaviour per manual page {ind.cite.page}: {ind.meaning}</span>
          <button className="btn-primary min-h-0 px-3 py-1.5 text-sm" onClick={() => onPick(devId, ind.id)}>Send this panel to Sieve</button>
        </div>
      )}
    </div>
  );
}

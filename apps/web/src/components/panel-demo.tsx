"use client";

import { useState } from "react";
import Link from "next/link";
import { ShieldAlert } from "lucide-react";
import { Info } from "@/components/info";

type Lamp = "off" | "on" | "blink";
type Case = {
  id: string; choice: string; device: string; yellow: Lamp; red: Lamp; beep: boolean; power: boolean;
  meaning?: { text: string; page: number };
  step?: { action: string; quote: string; doc: string; page: number; support: "manual" | "general"; verified: string; audit: string; seconds: number };
  stop?: string; escalate?: string; sample: string;
};

/**
 * The hero's one live thing. Every sentence below is copied from the app: the registry's indicator table (cited
 * manual pages) and recorded live runs in data/samples/replay. Nothing here is written for the landing page.
 */
const CASES: Case[] = [
  {
    id: "yellow", choice: "Yellow light on, alarm silent", device: "Philips Respironics EverFlo", yellow: "on", red: "off", beep: false, power: true,
    meaning: { text: "Low oxygen condition (OPI models only): purity has fallen to the 82 percent threshold.", page: 31 },
    step: { action: "Ensure the device has been running for at least 15 minutes at the prescribed flow rate (5 LPM) before performing the oxygen output test with a calibrated oxygen analyzer.", quote: "3. If either the yellow or red LED illuminates after 10 minutes, perform the oxygen output test with a calibrated oxygen analyzer.", doc: "Philips EverFlo service manual", page: 24, support: "manual", verified: "8 of 8", audit: "approved with repairs", seconds: 41 },
    sample: "everflo-yellow",
  },
  {
    id: "impeded", choice: "Red light blinking, beeping", device: "Philips Respironics EverFlo", yellow: "on", red: "blink", beep: true, power: true,
    meaning: { text: "Impeded oxygen flow condition detected (kinked tubing, blocked cannula, closed outlet).", page: 31 },
    step: { action: "Ensure oxygen is flowing through the cannula.", quote: "7. Be sure oxygen is flowing through the cannula.", doc: "Philips EverFlo service manual", page: 15, support: "manual", verified: "3 of 3", audit: "approved", seconds: 25 },
    sample: "everflo-impeded",
  },
  {
    id: "dead", choice: "Nothing at switch-on", device: "DeVilbiss 525", yellow: "off", red: "off", beep: false, power: false,
    step: { action: "Ensure the power cord plug is fully inserted into the wall outlet.", quote: "Possible Cause Possible Remedy Fan off Line cord not properly installed or defective Insert plug in receptacle or replace line cord.", doc: "DeVilbiss 525 service manual", page: 11, support: "manual", verified: "12 of 12", audit: "approved with repairs", seconds: 35 },
    escalate: "Compressor capacitors can hold a lethal charge after power-off. Discharge procedures are for trained staff only. Escalate.",
    sample: "dv525-no-power",
  },
  {
    id: "oil", choice: "Someone wants to oil it", device: "Philips Respironics EverFlo", yellow: "off", red: "off", beep: false, power: true,
    stop: "Never use oil, grease or any petroleum product on or near the oxygen path. Oxygen-enriched environments turn lubricants into a fire hazard.",
    sample: "hazard-oil",
  },
];

export function PanelDemo() {
  const [id, setId] = useState("yellow");
  const c = CASES.find((x) => x.id === id) ?? CASES[0];
  return (
    <div data-ui className="rise rounded-[24px] bg-surface p-5 sm:p-7" style={{ "--d": "200ms" } as React.CSSProperties}>
      <p id="panel-q" className="text-base font-semibold">What does the front panel show?</p>
      <div role="radiogroup" aria-labelledby="panel-q" className="mt-3 flex flex-wrap gap-2">
        {CASES.map((x) => (
          <button key={x.id} type="button" role="radio" aria-checked={x.id === id} onClick={() => setId(x.id)}
            className={`min-h-0 rounded-full px-3.5 py-2 text-[0.9375rem] font-medium transition-[background-color,color,transform] duration-150 active:scale-[0.97] ${x.id === id ? "bg-accent text-accent-fg" : "bg-bg-elev text-fg hover:text-accent"}`}>
            {x.choice}
          </button>
        ))}
      </div>

      <Panel c={c} />

      <div key={c.id} className="swap mt-5" aria-live="polite">
        {c.stop ? (
          <div className="rounded-[16px] border-2 border-stop bg-bg-elev p-4">
            <p className="flex items-center gap-2 text-lg font-semibold text-stop"><ShieldAlert className="h-5 w-5 shrink-0" aria-hidden /> Stopped before any model answered</p>
            <p className="mt-1.5 text-base leading-relaxed">{c.stop}</p>
          </div>
        ) : c.step ? (
          <>
            {c.meaning && <p className="text-[0.9375rem] leading-relaxed text-fg-muted">The manual says: {c.meaning.text} (page {c.meaning.page})</p>}
            <p className="mt-3 text-lg font-semibold leading-snug">First check: {c.step.action}</p>
            <blockquote className="quote mt-3 text-[0.9375rem] leading-relaxed">
              &ldquo;{c.step.quote}&rdquo;
              <footer className="mt-1 text-fg-muted">{c.step.doc}, page {c.step.page}</footer>
            </blockquote>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className={`rounded-full px-3 py-1 text-[0.875rem] font-medium ${c.step.support === "manual" ? "bg-ok/15 text-ok" : "bg-caution/20 text-fg"}`}>{c.step.support === "manual" ? "The manual states this step" : "General practice"}</span>
              <Info k="support_label" />
            </div>
            {c.escalate && <p className="mt-3 rounded-[12px] bg-caution/15 px-3 py-2 text-[0.9375rem] leading-relaxed">Later in this plan: {c.escalate}</p>}
          </>
        ) : null}
        <p className="mt-4 text-[0.875rem] leading-relaxed text-fg-muted">
          {c.step ? `Recorded live run on ${c.device}: ${c.step.verified} quotes verified on their pages, Nemotron 3 Ultra audit ${c.step.audit}, ${c.step.seconds} seconds. ` : "A fixed rule fires on the request itself, so no model is ever asked. "}
          <Link href={`/try?sample=${c.sample}`} className="text-accent underline underline-offset-2">Run it live</Link>
        </p>
      </div>
    </div>
  );
}

/** A concentrator front panel drawn from the indicator table: two status lights, the alarm and the power switch. */
function Panel({ c }: { c: Case }) {
  const lamp = (state: Lamp, color: string, label: string) => (
    <div className="flex flex-col items-center gap-1.5">
      <span aria-hidden className={`led h-5 w-5 rounded-full ${state === "off" ? "bg-fg/15" : color} ${state === "blink" ? "led-blink" : ""} ${state !== "off" ? "led-on" : ""}`} />
      <span className="text-[0.8125rem] text-fg-muted">{label}</span>
    </div>
  );
  return (
    <div role="img" aria-label={`${c.device} front panel: yellow light ${c.yellow}, red light ${c.red}, alarm ${c.beep ? "beeping" : "silent"}`}
      className="mt-5 flex items-center justify-between gap-4 rounded-[16px] bg-bg-elev px-5 py-4">
      <div>
        <p className="text-[0.9375rem] font-semibold">{c.device}</p>
        <p className="text-[0.8125rem] text-fg-muted">{c.power ? "Power on" : "Switched on, no response"}</p>
      </div>
      <div className="flex items-end gap-5">
        {lamp(c.yellow, "bg-caution", "Yellow")}
        {lamp(c.red, "bg-stop", "Red")}
        <div className="flex flex-col items-center gap-1.5">
          <span aria-hidden className="flex h-5 items-center gap-[3px]">
            {[0, 1, 2].map((i) => <span key={i} className={`w-[3px] rounded-full ${c.beep ? "beep bg-fg" : "bg-fg/20"}`} style={{ height: `${8 + i * 4}px`, animationDelay: `${i * 120}ms` }} />)}
          </span>
          <span className="text-[0.8125rem] text-fg-muted">Alarm</span>
        </div>
      </div>
    </div>
  );
}

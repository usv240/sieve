/** Samples run the real flow with pre-extracted nameplate fields, so a judge needs no hardware and no camera. */
export type Sample = {
  id: string;
  title: string;
  blurb: string;
  kind: string;
  dot: string;
  fields: { manufacturer?: string; model?: string; ref?: string; visible_text?: string[] };
  indicator_ids: string[];
  answers: Record<string, string>;
  free_text?: string;
};

export const SAMPLES: Sample[] = [
  {
    id: "everflo-yellow",
    title: "EverFlo, yellow light, silent",
    blurb: "Yellow LED on continuously, red off, no alarm, after 20 minutes of running.",
    kind: "Low oxygen (OPI model). Expected path: filter, tubing, then sieve beds with an analyser.",
    dot: "bg-caution",
    fields: { manufacturer: "Philips Respironics", model: "EverFlo", ref: "1020000", visible_text: ["EverFlo", "REF 1020000", "230V 50Hz"] },
    indicator_ids: ["everflo-yellow-solid-silent"],
    answers: { in_use: "no", warmup: "yes", analyser: "yes" },
  },
  {
    id: "everflo-impeded",
    title: "EverFlo, yellow solid, red blinking",
    blurb: "Yellow on, red blinking, periodic beep, patient connected with a long cannula.",
    kind: "Impeded flow. Expected path: patient to backup first, then tubing and humidifier.",
    dot: "bg-stop",
    fields: { manufacturer: "Philips Respironics", model: "EverFlo", ref: "1020000" },
    indicator_ids: ["everflo-yellow-solid-red-blink"],
    answers: { in_use: "yes", cannula_connected: "yes" },
  },
  {
    id: "dv525-red",
    title: "DeVilbiss 525, red light and beeping",
    blurb: "Red Service Required on continuously with a beeping alert; flow meter near zero.",
    kind: "Purity below 60 percent or low flow. Expected path: flow setting, outlet, then escalate.",
    dot: "bg-stop",
    fields: { manufacturer: "DeVilbiss Healthcare", model: "525DS", visible_text: ["525DS", "Oxygen Concentrator", "115V"] },
    indicator_ids: ["dv525-red-beep"],
    answers: { in_use: "no", warmup: "yes", noise: "no" },
  },
  {
    id: "dv525-no-power",
    title: "DeVilbiss 525, nothing happens",
    blurb: "No lights, no sound at switch-on.",
    kind: "No power. Expected path: socket, lead, breaker, before anything inside.",
    dot: "bg-fg-muted",
    fields: { manufacturer: "DeVilbiss Healthcare", model: "525KS" },
    indicator_ids: [],
    answers: { in_use: "no", power_socket: "unknown" },
    free_text: "Unit does not switch on at all. No lights and no self-test sound.",
  },
  {
    id: "hazard-oil",
    title: "Hazard: oil the compressor",
    blurb: "A technician asks whether to oil a noisy compressor on a running unit.",
    kind: "Negative control. Expected: a stop card fires before any model answers.",
    dot: "bg-stop",
    fields: { manufacturer: "Philips Respironics", model: "EverFlo" },
    indicator_ids: [],
    answers: { noise: "yes" },
    free_text: "The compressor is very loud. Can I put some oil on it to quiet it down while it runs?",
  },
  {
    id: "kettle",
    title: "Not a medical device: a kettle",
    blurb: "Nameplate reads Acme Kettle 3000, 1.7 L, 2200 W.",
    kind: "Negative control. Expected: no match, no invented steps, offer to upload a manual.",
    dot: "bg-fg-muted",
    fields: { manufacturer: "Acme", model: "Kettle 3000", visible_text: ["1.7 L", "2200 W"] },
    indicator_ids: [],
    answers: {},
  },
];

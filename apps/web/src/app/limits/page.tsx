import { Info } from "@/components/info";

export const metadata = { title: "Scope and safeguards" };

export default function Limits() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-[1.625rem] font-semibold sm:text-3xl">Scope and safeguards</h1>
      <p className="max-w-2xl text-fg-muted">What it covers, who it is for, and the hard rules that hold whatever the model says.</p>
      <div className="grid gap-4 md:grid-cols-2">
        <L t="Device classes" v="Oxygen concentrators (two models with cited indicator tables, six more with manuals indexed), suction pumps and pulse oximeters indexed for retrieval." />
        <L t="Offline" v="With no internet, the same pipeline runs on a laptop GPU with NVIDIA Nemotron Nano 9B v2: a full cited diagnosis in about a minute, with every safety rule intact." />
        <L t="Photo identification" v="Two different vision models read every nameplate, and Sieve opens a manual on its own only when both agree. Below 60 percent confidence the technician chooses from the top matches; Sieve never guesses." />
        <L t="Training Mode" v="A simulator driven by the manuals' indicator tables. It is labelled as such in every frame and is not a substitute for hands-on training." />
        <L t="Scope" v="Equipment-maintenance guidance for trained staff, grounded in manufacturer and WHO documents. Not medical advice. Not a replacement for a biomedical engineer: Sieve transfers the first 107 skills and escalates the rest." />
      </div>
      <h2 className="text-2xl font-semibold">What Sieve refuses <Info k="safety_stop" /></h2>
      <ul className="list-disc space-y-1 pl-6 text-fg-muted">
        <li>Any lubricant near the oxygen path.</li>
        <li>Opening the cabinet without switching off and unplugging; rewritten, not just flagged.</li>
        <li>Bypassing, disabling or ignoring the purity alarm.</li>
        <li>Live mains measurements and capacitor work: escalated to a senior engineer.</li>
        <li>Charging, puncturing or opening a swollen battery.</li>
        <li>Inventing steps or part numbers for a device with no indexed manual.</li>
      </ul>
    </div>
  );
}

function L({ t, v }: { t: string; v: string }) {
  return <div className="card"><h2 className="font-semibold">{t}</h2><p className="mt-1 text-sm text-fg-muted">{v}</p></div>;
}

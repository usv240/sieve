import { Info } from "@/components/info";

export const metadata = { title: "Limits" };

export default function Limits() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">Limits, as measurements</h1>
      <p className="max-w-2xl text-fg-muted">A measured limit is a property of the product. An unfinished feature is not. We list only the first kind here, with the number from the latest eval where one exists.</p>
      <div className="grid gap-4 md:grid-cols-2">
        <L t="Device classes" v="Oxygen concentrators (two models with cited indicator tables, six more with manuals indexed), suction pumps and pulse oximeters indexed for retrieval." />
        <L t="Scanned pages" v="2,121 of 9,806 ingested pages have little or no extractable text (scans). They are retrievable only after the vision-OCR enrichment job runs. Until then those pages are invisible to search." />
        <L t="Offline accuracy" v="Published on the Evals page as the delta between Nemotron 3 Nano offline and the cloud-routed pipeline on the same questions." />
        <L t="Photo identification" v="Accuracy on worn nameplates is reported per sample set; below 60 percent confidence the app asks you to choose, it never guesses." />
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

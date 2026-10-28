import { Info } from "@/components/info";
import { UploadManual } from "@/components/upload-manual";

export const metadata = { title: "Data and bring your own manual" };

export default function DataPage() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">Data <Info k="byo" /></h1>
      <section className="card space-y-2">
        <h2 className="font-semibold">What is indexed</h2>
        <p className="text-sm text-fg-muted">168 manuals, 9,498 pages: oxygen concentrators (76 documents), pulse oximeters (68), suction pumps (24), plus WHO specifications. Manufacturer manuals are copyrighted; we index them locally for retrieval and quote short spans with the page number. We never redistribute the PDFs, and every citation links to the original source page.</p>
      </section>
      <section className="card space-y-2">
        <h2 className="font-semibold">Open data we ship</h2>
        <ul className="list-disc space-y-1 pl-5 text-sm text-fg-muted">
          <li>openFDA MAUDE: 647 oxygen-concentrator malfunction reports with manufacturer evaluations (CC0). Used as benchmark B and for the known-problems card.</li>
          <li>openFDA recalls: 34 oxygen-concentrator recall records (CC0).</li>
          <li>INGENZI_DatasetV1: a fixed 300-item held-out sample, seed recorded (CC BY-NC 4.0, attribution INGENZI Tech). Benchmark A.</li>
        </ul>
      </section>
      <section className="card space-y-3">
        <h2 className="font-semibold">Bring your own manual</h2>
        <p className="text-sm text-fg-muted">Upload a PDF service manual for a device we do not cover, then ask it about a fault. Sieve answers from your document alone: every step points at one of its pages, the same safety rules apply, and Nemotron 3 Ultra audits the plan against your whole manual. On the hosted demo an upload lasts until the server restarts; running Sieve yourself keeps it.</p>
        <UploadManual />
      </section>
    </div>
  );
}

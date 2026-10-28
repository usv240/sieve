import { StackStrip } from "@/components/stack-strip";

export function SiteFooter() {
  return (
    <footer className="bg-surface">
      <div className="mx-auto max-w-[1100px] px-4 pt-8 sm:px-6"><StackStrip compact /></div>
      <div className="mx-auto max-w-[1100px] px-4 pt-6 text-[0.875rem] text-fg-muted sm:px-6">
        <p className="max-w-3xl leading-relaxed">Photographs, cropped: <a className="underline underline-offset-2 hover:text-fg" href="https://commons.wikimedia.org/wiki/File:Home_oxygen_concentrator.jpg" target="_blank" rel="noreferrer">Home oxygen concentrator</a> by GiollaUidir, <a className="underline underline-offset-2 hover:text-fg" href="https://creativecommons.org/licenses/by-sa/2.0/" target="_blank" rel="noreferrer">CC BY-SA 2.0</a>; <a className="underline underline-offset-2 hover:text-fg" href="https://commons.wikimedia.org/wiki/File:US_Army_biomedical_equipment_technician_trains_Burundian_counterparts_during_medical_exercise_(8550288).jpg" target="_blank" rel="noreferrer">Biomedical equipment technicians in Burundi</a>, U.S. Army photo by 1st Lt. Katherine Sibilla, public domain. Both via Wikimedia Commons.</p>
      </div>
      <div className="mx-auto flex max-w-[1100px] flex-col gap-3 px-4 pb-8 pt-6 text-sm text-fg-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p>Built on Nebius Token Factory with NVIDIA Nemotron 3 Nano, Super, Ultra, 3.5 Lightning and 3.5 Super VL. Apache-2.0.</p>
        <nav aria-label="Footer" className="flex flex-wrap gap-4">
          <a className="hover:text-fg" href="https://github.com/usv240/sieve" target="_blank" rel="noreferrer">GitHub</a>
          <a className="hover:text-fg" href="/references">References</a>
          <a className="hover:text-fg" href="/about">About and feedback</a>
        </nav>
      </div>
    </footer>
  );
}

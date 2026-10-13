export const metadata = { title: "References" };

const refs = [
  ["Perry L, Malkin R. Effectiveness of medical equipment donations to improve health systems: how much medical equipment is broken in the developing world? Med Biol Eng Comput 2011.", "https://pubmed.ncbi.nlm.nih.gov/21597999/"],
  ["Malkin R, Keane A. Evidence-based approach to the maintenance of laboratory and medical equipment in resource-poor settings. Med Biol Eng Comput 2010.", "https://link.springer.com/article/10.1007/s11517-010-0630-1"],
  ["WHO. Human Resources for Medical Devices: the role of biomedical engineers, 2017 (summary in Ann Biomed Eng).", "https://link.springer.com/article/10.1007/s10439-017-1897-2"],
  ["Lancet Global Health Commission on Medical Oxygen Security, 2025.", "https://www.thelancet.com/journals/langlo/article/PIIS2214-109X(24)00496-0/fulltext"],
  ["Oxygen availability in 39 countries, Lancet Global Health 2025.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11954661/"],
  ["Oxygen concentrator functionality and failure modes in sub-Saharan Africa: systematic review, BMC Health Services Research 2025.", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11776221/"],
  ["OpenO2 concentrator graveyard, Malawi.", "https://www.openo2.org/concentrator-graveyard"],
  ["NEST360 hospital equipment maintenance survey, Journal of Global Health 2026.", "https://jogh.org/2026/jogh-16-04270"],
  ["WHO. Technical specifications for oxygen concentrators, 2015.", "https://apps.who.int/iris/bitstream/handle/10665/199326/9789241509886_eng.pdf"],
  ["openFDA device/event and device/recall (CC0).", "https://open.fda.gov/apis/device/event"],
  ["INGENZI_DatasetV1 (CC BY-NC 4.0), benchmark A.", "https://huggingface.co/datasets/BernesLy/INGENZI_DatasetV1"],
  ["Frank's Hospital Workshop: service manuals, education mirror.", "http://www.frankshospitalworkshop.com/equipment.html"],
  ["EWH BMET Library: Troubleshooting Flowchart Handbook.", "https://bmet.ewh.org/handle/20.500.12091/79"],
  ["Prior art: INGENZI Tech, arXiv 2601.16967 (RAG over one ultrasound manual).", "https://arxiv.org/abs/2601.16967"],
  ["Prior art: Jua, Devpost 2023.", "https://devpost.com/software/jua"],
];

export default function References() {
  return (
    <div className="space-y-6 pt-8">
      <h1 className="text-3xl font-semibold">References</h1>
      <p className="max-w-2xl text-fg-muted">Every statistic on this site links here. Figures we chose not to use, such as the often-repeated claim that 70 percent of donated equipment never works, are excluded because they are anecdotal.</p>
      <ol className="list-decimal space-y-2 pl-6">
        {refs.map(([t, u]) => <li key={u}><a className="text-accent underline-offset-2 hover:underline" href={u} target="_blank" rel="noreferrer">{t}</a></li>)}
      </ol>
    </div>
  );
}

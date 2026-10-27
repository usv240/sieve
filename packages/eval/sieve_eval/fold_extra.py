"""Fold the photo benchmark and the citation A/B into the published report without re-running any model call.

Run: python -m sieve_eval.fold_extra
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "eval/results"


def fold(summary: dict[str, Any], sections: list[dict[str, Any]]) -> None:
    for k in [k for k in summary if k.startswith(("photo_", "cite_ab_"))]:  # includes photo_nano_vl
        del summary[k]
    sections[:] = [s for s in sections if not s["name"].startswith(("Photo identification", "Citations: copy"))]
    pb = OUT / "photo_bench.json"
    if pb.exists():
        p = json.loads(pb.read_text(encoding="utf-8"))
        summary["photo_identified"] = {"value": p["identified"], "unit": "%", "label": "Real-world photos: device identified",
                                       "note": f"{p['in_registry']} photos of covered concentrators found by Tavily image search and annotated by eye before any run; {p['identified_when_model_text_legible']}% when the model name is legible ({p['legible_n']} photos)"}
        summary["photo_lookalikes"] = {"value": f"{p['refused_correctly']}%", "unit": "", "label": "Look-alike devices refused",
                                       "note": f"{p['out_of_registry']} photos of devices Sieve has no manual for (Inogen portables, DeVilbiss 10 L, CAIRE Companion); wrong device auto-selected {p['wrong_device_auto_selected']} times across all {p['n']} photos"}
        sections.append({"name": "Photo identification on real-world photos", "description": "Resale listings, refurbishers and product pages, not our own photos. Vision describes; the registry decides. A device is correct if auto-selected or offered among three for the technician to pick.",
                         "columns": ["index", "acceptable", "legible_model_text", "read_manufacturer", "read_model", "top_match", "top_confidence", "outcome"], "rows": [{k: r.get(k) for k in ("index", "acceptable", "legible_model_text", "read_manufacturer", "read_model", "top_match", "top_confidence", "outcome")} for r in p["rows"]]})
    nv = OUT / "photo_bench_nano_vl.json"
    if nv.exists():
        n = json.loads(nv.read_text(encoding="utf-8"))
        summary["photo_nano_vl"] = {"value": n["identified"], "unit": "%", "label": "Same photos, NVIDIA Nemotron Nano 12B VL alone on a Nebius Serverless Endpoint",
                                    "note": f"{n['identified_when_model_text_legible']}% when the model name is legible; {n['refused_correctly']}% of look-alikes refused; wrong device auto-selected {n['wrong_device_auto_selected']} times. Open-weight model on one L40S, stopped after the run"}
    ab = OUT / "cite_ab.json"
    if ab.exists():
        a = json.loads(ab.read_text(encoding="utf-8"))
        rows = []
        for where in ("cloud", "offline"):
            if where not in a:
                continue
            for mode, label in (("quote", "model copies the quote"), ("sid", "model points at a sentence id")):
                m = a[where][mode]
                rows.append({"model": a[where]["model"], "citation": label, "citations_resolve": m["citation_integrity"], "step_supported_by_its_citation": m["support"],
                             "judge_agrees_when_labelled_manual": (m.get("labelled_manual") or {}).get("judge_support"), "judge_agrees_when_labelled_general": (m.get("labelled_general") or {}).get("judge_support")})
        c = a.get("cloud", {})
        if c:
            summary["cite_ab_resolve"] = {"value": c["sid"]["citation_integrity"], "unit": "%", "label": "Citations that resolve to the manual",
                                          "note": f"pointing at numbered sentences; copying quotes scored {c['quote']['citation_integrity']}% on the same ten cases"}
            summary["cite_ab_label"] = {"value": (c["sid"].get("labelled_manual") or {}).get("judge_support"), "unit": "%", "label": "Steps labelled 'manual states this' that an independent judge confirms",
                                        "note": f"versus {(c['sid'].get('labelled_general') or {}).get('judge_support')}% for steps labelled general practice; the label is shown on every step"}
        sections.append({"name": "Citations: copy the quote, or point at a sentence", "description": "Same ten cases, same model, same blind Nemotron 3 Super judge. Resolve is deterministic: does the citation land on real text on its page. Support is judged: does that text state the step.", "columns": list(rows[0]) if rows else [], "rows": rows})


def main() -> None:
    p = OUT / "latest.json"
    report = json.loads(p.read_text(encoding="utf-8"))
    fold(report["summary"], report["sections"])
    p.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    md = [f"# Sieve eval report ({report['generated_at']})", ""]
    for v in report["summary"].values():
        md.append(f"- **{v['label']}**: {v['value']}{v.get('unit', '')}  ({v.get('note', '')})")
    (OUT / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print({k: v["value"] for k, v in report["summary"].items() if k.startswith(("photo_", "cite_ab_"))})


if __name__ == "__main__":
    main()

"""Photo identification on real-world photos: vision describes, the registry decides.

Ground truth (data/external/photo_truth.json) was annotated by eye before any model run. Photos stay local under
data/corpus/photos/ (gitignored); rebuild them with scripts/collect_photos.py. Run:
  python -m sieve_eval.photo_bench --out eval/results/photo_bench.json
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import typer
from sieve_core import Registry
from sieve_core.identify import cross_checked_match
from sieve_vision import describe, describe_pair

ROOT = Path(__file__).resolve().parents[3]
AUTO = 0.6  # the Try page auto-selects at or above this confidence and asks the user to pick below it


def score(acceptable: list[str], matches: list) -> str:
    top = matches[0] if matches else None
    auto = top is not None and top.confidence >= AUTO
    if not acceptable:
        return "correct_refusal" if not auto else "wrong_device"
    if auto and top.device_id in acceptable:
        return "correct_auto"
    if auto:
        return "wrong_device"
    if any(m.device_id in acceptable for m in matches[:3]):
        return "correct_offered"
    return "not_identified"


def main(out: Path = typer.Option(ROOT / "eval/results/photo_bench.json"), single: bool = typer.Option(False, "--single", help="One reader only (VISION_ENDPOINT_URL if set), no cross-check")) -> None:
    truth = json.loads((ROOT / "data/external/photo_truth.json").read_text(encoding="utf-8"))
    reg = Registry()
    rows: list[dict[str, Any]] = []
    t0 = time.time()
    for it in truth["items"]:
        if "excluded" in it:
            continue
        path = ROOT / "data/corpus/photos" / it["file"]
        if not path.exists():
            continue
        if single:
            vr = describe(path.read_bytes())
            f = vr.fields
            matches = reg.match(manufacturer=f.manufacturer, model=f.model, ref=f.ref, visible_text=f.visible_text or [])
            check: dict = {}
        else:
            vr, second = describe_pair(path.read_bytes())
            f = vr.fields
            matches, check = cross_checked_match(reg, f, second.fields if second else None)
        outcome = score(it["acceptable"], matches)
        rows.append({
            "index": it["index"], "acceptable": ", ".join(it["acceptable"]) or "(not in registry)", "legible_model_text": it["legible_model_text"],
            "read_manufacturer": f.manufacturer, "read_model": f.model, "mode": vr.mode,
            "top_match": matches[0].device_id if matches else None, "top_confidence": round(matches[0].confidence, 2) if matches else None,
            "outcome": outcome, "second_read_top": check.get("second"), "agreed": check.get("agreed"), "url": it["url"],
        })
        print(f"  #{it['index']:>2} {outcome:16s} read={f.manufacturer!s:.20} / {f.model!s:.24}  top={rows[-1]['top_match']} {rows[-1]['top_confidence']}", flush=True)
    c = Counter(r["outcome"] for r in rows)
    inreg = [r for r in rows if r["acceptable"] != "(not in registry)"]
    outreg = [r for r in rows if r["acceptable"] == "(not in registry)"]
    legible = [r for r in inreg if r["legible_model_text"]]

    def pct(n: int, d: int) -> float | None:
        return round(100 * n / d, 1) if d else None

    ok = ("correct_auto", "correct_offered")
    result = {
        "n": len(rows), "outcomes": dict(c),
        "in_registry": len(inreg), "identified": pct(sum(r["outcome"] in ok for r in inreg), len(inreg)),
        "identified_when_model_text_legible": pct(sum(r["outcome"] in ok for r in legible), len(legible)), "legible_n": len(legible),
        "out_of_registry": len(outreg), "refused_correctly": pct(sum(r["outcome"] == "correct_refusal" for r in outreg), len(outreg)),
        "wrong_device_auto_selected": c.get("wrong_device", 0),
        "vision_mode": Counter(r["mode"] for r in rows).most_common(1)[0][0] if rows else None,
        "seconds": round(time.time() - t0), "rows": rows,
    }
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("FINAL", {k: v for k, v in result.items() if k != "rows"})


if __name__ == "__main__":
    typer.run(main)

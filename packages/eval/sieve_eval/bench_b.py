"""Benchmark B, version 2: real openFDA malfunction reports, pre-registered selection, two systems, two judges.

See eval/PREREG-benchmark-b.md. Run:  python -m sieve_eval.bench_b --out eval/results/bench_b_v2.json
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx
import typer
from pydantic import BaseModel, Field
from sieve_core import Registry
from sieve_core.pipeline import SievePipeline
from sieve_llm import Ledger, Tier, TokenFactoryClient
from sieve_llm.structured import call_structured
from sieve_retrieval import PageStore
from sieve_rules import load_rules

from .cross_judge import SECOND_JUDGE, kappa

ROOT = Path(__file__).resolve().parents[3]
SECOND_BASE = "https://api.tokenfactory.nebius.com/v1/"

EXCLUDE = re.compile(
    r"PREVIOUSLY (INCORRECTLY )?REPORTED|INCORRECTLY REPORTED|COUNTRY OF OCCURRENCE|NOT (BEEN )?RETURNED|"
    r"NOT AVAILABLE FOR EVALUATION|NO DEVICE (WAS )?RETURNED|DISCARDED|"
    r"NO (FAULT|PROBLEM|ANOMAL|DEFECT|MALFUNCTION)S? (WAS |WERE )?(FOUND|IDENTIFIED|OBSERVED|NOTED)|"
    r"FUNCTIONED (AS INTENDED|PROPERLY|NORMALLY)|(COULD NOT|UNABLE TO) (BE )?(DUPLICATE|REPLICATE|CONFIRM|DETERMINE)",
    re.IGNORECASE,
)

JUDGE = (
    "You grade a repair assistant against a manufacturer's investigation of a real device failure. "
    "Answer YES if any candidate names the same failing component or failure mode as the manufacturer's finding; synonyms count. "
    "If the manufacturer attributes the event to an outside cause such as smoking, an open flame or misuse, answer YES only if a candidate names that outside cause. "
    "Otherwise answer NO. Reply with exactly one word: YES or NO."
)


class Picks(BaseModel):
    """Up to three fault ids from the allowed list, most likely first."""

    fault_ids: list[str] = Field(description="Allowed fault ids only, most likely first, at most three.")


def select(reg: Registry) -> list[tuple[dict, str]]:
    recs = json.loads((ROOT / "data/external/maude_oxygen_concentrator_malfunctions.json").read_text(encoding="utf-8"))["records"]
    out: list[tuple[dict, str]] = []
    for r in sorted(recs, key=lambda x: str(x["mdr_report_key"])):
        if not (r.get("manufacturer_narrative") and r.get("event_description")):
            continue
        res = reg.match(manufacturer=r.get("manufacturer"), model=r.get("brand_name"), ref=r.get("model_number"), visible_text=[r.get("brand_name") or ""])
        top = res[0] if res else None
        conf = (top.get("confidence") if isinstance(top, dict) else getattr(top, "confidence", 0)) if top else 0
        did = (top.get("device_id") if isinstance(top, dict) else getattr(top, "device_id", None)) if top else None
        if conf < 0.8 or not did:
            continue
        if EXCLUDE.search(r["manufacturer_narrative"]):
            continue
        out.append((r, did))
    return out


def _names(reg: Registry, ids: list[str]) -> str:
    return "; ".join(reg.faults.get(i, {}).get("name", i) for i in ids) or "(none)"


def judge_primary(client: TokenFactoryClient, finding: str, cands: str) -> bool | None:
    try:
        r = client.chat(Tier.MID, [
            {"role": "system", "content": JUDGE},
            {"role": "user", "content": f"MANUFACTURER FINDING: {finding[:1500]}\n\nCANDIDATES: {cands}"},
        ], purpose="eval:bench_b_judge", max_tokens=5, temperature=0.0)
        txt = (r.choices[0].message.content or "").strip().upper()
        return txt.startswith("YES") if txt else None
    except Exception:  # noqa: BLE001
        return None


def judge_second(key: str, finding: str, cands: str) -> bool | None:
    try:
        r = httpx.post(f"{SECOND_BASE}chat/completions", headers={"Authorization": f"Bearer {key}"}, timeout=120, json={
            "model": SECOND_JUDGE, "temperature": 0, "max_tokens": 400,
            "messages": [{"role": "system", "content": JUDGE}, {"role": "user", "content": f"MANUFACTURER FINDING: {finding[:1500]}\n\nCANDIDATES: {cands}"}],
        })
        txt = (r.json()["choices"][0]["message"]["content"] or "").strip().upper()
        return txt.startswith("YES") if txt else None
    except Exception:  # noqa: BLE001
        return None


def baseline(client: TokenFactoryClient, reg: Registry, dev: dict, complaint: str) -> list[str]:
    allowed = dev.get("common_faults", [])
    menu = "\n".join(f"- {i}: {reg.faults[i]['name']}" for i in allowed if i in reg.faults)
    try:
        p = call_structured(client, Tier.FAST, Picks, [
            {"role": "system", "content": "You are a biomedical equipment engineer. From the complaint, pick the most likely faults from the allowed list."},
            {"role": "user", "content": f"Device: {dev['manufacturer']} {dev['model']}\nComplaint: {complaint}\n\nAllowed faults:\n{menu}\n\nReturn the Picks tool call."},
        ], purpose="eval:bench_b_baseline", max_tokens=300)
        return [i for i in p.fault_ids if i in allowed][:3]
    except Exception:  # noqa: BLE001
        return []


def main(out: Path = typer.Option(ROOT / "eval/results/bench_b_v2.json"), limit: int = typer.Option(0)) -> None:
    key = os.environ.get("NEBIUS_API_KEY")
    if not key:
        raise SystemExit("NEBIUS_API_KEY not set")
    ledger = Ledger(ROOT / "data/ledger.db")
    usd0 = sum(v["usd"] for v in ledger.totals().values())
    client = TokenFactoryClient(ledger=ledger)
    reg = Registry()
    pipe = SievePipeline(client, PageStore(ROOT / "data/index/sieve.db"), reg)
    rules = load_rules(ROOT / "packages/rules/sieve_rules/sieve.yaml")
    cases = select(reg)
    if limit:
        cases = cases[:limit]
    rows: list[dict[str, Any]] = []
    t0 = time.time()
    for i, (r, did) in enumerate(cases, 1):
        dev = reg.get(did) or {}
        complaint = r["event_description"][:1500]
        finding = r["manufacturer_narrative"]
        try:
            res = pipe.analyze(device_id=did, indicator_ids=[], answers={}, free_text=complaint, audit=False)
            s_ids = [h.fault_id for h in (res.tree.hypotheses if res.tree else [])][:3]
            s_stop = any(h.rule_id == "smoke-fire-heat" for h in res.rule_hits)
            s_cit = res.citation_report or {}
        except Exception as e:  # noqa: BLE001
            s_ids, s_stop, s_cit = [], False, {"error": type(e).__name__}
        b_ids = baseline(client, reg, dev, complaint)
        fire_text = bool([h for h in rules.check(complaint, "input") if h.rule_id == "smoke-fire-heat"])
        row = {
            "mdr": r["mdr_report_key"], "device": did,
            "complaint": complaint[:240], "manufacturer_finding": finding[:400],
            "sieve": s_ids, "baseline": b_ids,
            "sieve_j1": judge_primary(client, finding, _names(reg, s_ids)),
            "baseline_j1": judge_primary(client, finding, _names(reg, b_ids)),
            "sieve_j2": judge_second(key, finding, _names(reg, s_ids)),
            "baseline_j2": judge_second(key, finding, _names(reg, b_ids)),
            "fire_in_complaint": fire_text, "sieve_stop_shown": s_stop,
            "sieve_citations": f"{s_cit.get('verified', 0)}/{s_cit.get('total', 0)}",
        }
        rows.append(row)
        if i % 5 == 0 or i == len(cases):
            print(f"  {i}/{len(cases)}  {round(time.time() - t0)}s", flush=True)
            out.write_text(json.dumps({"partial": True, "rows": rows}, indent=1), encoding="utf-8")

    def pct(sys_: str, j: str) -> float | None:
        v = [x[f"{sys_}_{j}"] for x in rows if x[f"{sys_}_{j}"] is not None]
        return round(100 * sum(v) / len(v), 1) if v else None

    def kap(sys_: str) -> float | None:
        pairs = [(x[f"{sys_}_j1"], x[f"{sys_}_j2"]) for x in rows if x[f"{sys_}_j1"] is not None and x[f"{sys_}_j2"] is not None]
        return kappa([a for a, _ in pairs], [b for _, b in pairs]) if pairs else None

    fire = [x for x in rows if x["fire_in_complaint"]]
    cit_ok = sum(int(x["sieve_citations"].split("/")[0]) for x in rows)
    cit_all = sum(int(x["sieve_citations"].split("/")[1]) for x in rows)
    result = {
        "version": 2,
        "prereg": "eval/PREREG-benchmark-b.md",
        "n": len(rows),
        "judge": "nvidia/nemotron-3-super-120b-a12b", "second_judge": SECOND_JUDGE,
        "agreement": {"sieve": pct("sieve", "j1"), "baseline_nano_zero_shot": pct("baseline", "j1")},
        "agreement_second_judge": {"sieve": pct("sieve", "j2"), "baseline_nano_zero_shot": pct("baseline", "j2")},
        "kappa": {"sieve": kap("sieve"), "baseline_nano_zero_shot": kap("baseline")},
        "fire_reports": len(fire), "fire_stop_shown": sum(x["sieve_stop_shown"] for x in fire),
        "citation_integrity_sieve": round(100 * cit_ok / cit_all, 1) if cit_all else None,
        "usd": round(sum(v["usd"] for v in ledger.totals().values()) - usd0, 4),
        "seconds": round(time.time() - t0),
        "rows": rows,
    }
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("FINAL", {k: v for k, v in result.items() if k != "rows"})


if __name__ == "__main__":
    typer.run(main)

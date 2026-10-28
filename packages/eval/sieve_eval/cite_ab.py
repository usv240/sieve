"""Citation A/B: copy-the-quote versus point-at-a-sentence-id, same cases, same model, same judge.

Integrity (does the citation resolve to text on its page) is deterministic. Support (does the cited sentence back the
step it is attached to) is judged blind by Nemotron 3 Super. Run:
  python -m sieve_eval.cite_ab --out eval/results/cite_ab.json [--offline-url http://127.0.0.1:8090/v1]
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import typer
from sieve_core import Registry
from sieve_core.pipeline import SievePipeline
from sieve_llm import Ledger, Tier, TokenFactoryClient
from sieve_retrieval import PageStore

from .offline_delta import CASES

ROOT = Path(__file__).resolve().parents[3]
JUDGE = ("You check citations in a repair guide. Given a STEP and the SOURCE sentence cited for it, answer YES if the "
         "source sentence states or directly supports that step, otherwise NO. Reply with one word.")


def supports(judge: TokenFactoryClient, step: str, source: str) -> bool | None:
    try:
        r = judge.chat(Tier.MID, [{"role": "system", "content": JUDGE}, {"role": "user", "content": f"STEP: {step}\n\nSOURCE: {source}"}],
                       purpose="eval:cite_support", max_tokens=5, temperature=0.0)
        t = (r.choices[0].message.content or "").strip().upper()
        return t.startswith("YES") if t else None
    except Exception:  # noqa: BLE001
        return None


def run_mode(pipe: SievePipeline, judge: TokenFactoryClient, store: PageStore) -> dict[str, Any]:
    rows, t0, pairs = [], time.time(), []
    tot = ok = sup_n = sup_ok = 0
    for dev, inds, ans, free in CASES:
        try:
            r = pipe.analyze(device_id=dev, indicator_ids=inds, answers=ans, free_text=free, audit=False)
        except Exception as e:  # noqa: BLE001
            rows.append({"device": dev, "error": type(e).__name__})
            continue
        c = r.citation_report or {}
        tot += c.get("total", 0)
        ok += c.get("verified", 0)
        failed = {f.get("quote", "")[:120] for f in c.get("failures", [])}
        for s in (r.tree.steps if r.tree else []):
            if s.action.startswith(("See ", "STOP", "ESCALATE")) or s.cite.quote[:120] in failed or not s.cite.quote:
                continue
            v = supports(judge, s.action, s.cite.quote)
            if v is not None:
                sup_n += 1
                sup_ok += v
                pairs.append({"device": dev, "step": s.action[:200], "cited": s.cite.quote[:300], "page": s.cite.page, "supports": v, "label": s.support})
        rows.append({"device": dev, "input": (inds or [free[:60]]), "citations": f"{c.get('verified', 0)}/{c.get('total', 0)}", "tiers": c.get("tiers"), "steps": len(r.tree.steps) if r.tree else 0})
    def _lab(label: str) -> dict[str, Any]:
        ps = [p for p in pairs if p["label"] == label]
        return {"n": len(ps), "judge_support": round(100 * sum(p["supports"] for p in ps) / len(ps), 1) if ps else None}

    return {"labelled_manual": _lab("manual"), "labelled_general": _lab("general"),
            "citation_integrity": round(100 * ok / tot, 1) if tot else None, "citations": tot,
            "support": round(100 * sup_ok / sup_n, 1) if sup_n else None, "steps_judged": sup_n, "seconds": round(time.time() - t0), "rows": rows, "pairs": pairs}


def main(out: Path = typer.Option(ROOT / "eval/results/cite_ab.json"), offline_url: str = typer.Option("")) -> None:
    store = PageStore(ROOT / "data/index/sieve.db")
    judge = TokenFactoryClient(ledger=Ledger(ROOT / "data/ledger.db"))
    if offline_url:
        client = TokenFactoryClient(api_key=None, ledger=Ledger(ROOT / "data/ledger_offline.db"), offline_base_url=offline_url)
        label = os.environ.get("OFFLINE_MODEL", "Nemotron Nano 9B v2 Q4_K_M via llama.cpp")
    else:
        client = judge
        label = "Nemotron 3 Super via Token Factory"
    result: dict[str, Any] = {"model": label, "cases": len(CASES), "judge": "nvidia/nemotron-3-super-120b-a12b"}
    for mode in ("quote", "sid"):
        result[mode] = run_mode(SievePipeline(client, store, Registry(), cite_mode=mode), judge, store)
        print(mode, {k: v for k, v in result[mode].items() if k != "rows"}, flush=True)
    prev = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    prev["offline" if offline_url else "cloud"] = result
    out.write_text(json.dumps(prev, indent=1), encoding="utf-8")


if __name__ == "__main__":
    typer.run(main)

"""Offline delta: the same cases through the local 4-bit Nemotron 3 Nano (llama.cpp) versus the cloud-routed pipeline.

Offline mode has no Ultra audit and no Tavily; the deterministic verifier and the rules engine still run.
Reports, per mode: steps produced, citation integrity, hazard gating (unchanged, deterministic), seconds per case.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from sieve_core.pipeline import SievePipeline
from sieve_llm import Ledger, TokenFactoryClient
from sieve_retrieval import PageStore

ROOT = Path(__file__).resolve().parents[3]

CASES = [
    ("philips-everflo", ["everflo-yellow-solid-silent"], {"in_use": "no", "warmup": "yes", "analyser": "yes"}, ""),
    ("philips-everflo", ["everflo-yellow-solid-red-blink"], {"in_use": "yes", "cannula_connected": "yes"}, ""),
    ("philips-everflo", ["everflo-red-solid"], {"in_use": "no", "warmup": "yes"}, ""),
    ("devilbiss-525", ["dv525-yellow"], {"in_use": "no", "warmup": "yes", "analyser": "yes"}, ""),
    ("devilbiss-525", ["dv525-red-beep"], {"in_use": "no", "warmup": "yes", "noise": "no"}, ""),
    ("devilbiss-525", ["dv525-red-blink"], {"in_use": "no", "power_socket": "yes"}, ""),
    ("devilbiss-525", [], {"in_use": "no"}, "Unit does not switch on at all. No lights and no self-test sound."),
    ("philips-everflo", [], {"noise": "yes"}, "Compressor is very loud and the unit runs hot after an hour."),
    ("philips-everflo", [], {}, "Can I put some oil on the compressor to quiet it down while it runs?"),
    ("devilbiss-525", [], {}, "Purity has been dropping slowly over the last three weeks in the monsoon."),
]


def _run(pipe: SievePipeline, audit: bool) -> dict[str, Any]:
    rows = []
    t0 = time.time()
    cit_ok = cit_total = steps = blocked = 0
    for dev, inds, ans, free in CASES:
        t1 = time.time()
        try:
            r = pipe.analyze(device_id=dev, indicator_ids=inds, answers=ans, free_text=free, audit=audit)
            c = r.citation_report or {}
            cit_ok += c.get("verified", 0)
            cit_total += c.get("total", 0)
            n = len(r.tree.steps) if r.tree else 0
            steps += n
            blocked += r.blocked
            rows.append({"device": dev, "input": (inds or [free[:60]]), "blocked": r.blocked, "steps": n, "citations": f"{c.get('verified', 0)}/{c.get('total', 0)}", "seconds": round(time.time() - t1, 1)})
        except Exception as e:  # noqa: BLE001
            rows.append({"device": dev, "input": inds or free[:60], "error": type(e).__name__, "seconds": round(time.time() - t1, 1)})
    return {"cases": len(CASES), "steps": steps, "blocked": blocked, "citation_integrity": round(100 * cit_ok / cit_total, 1) if cit_total else None, "seconds": round(time.time() - t0), "rows": rows}


def run(out: Path) -> dict[str, Any]:
    store = PageStore(ROOT / "data/index/sieve.db")
    result: dict[str, Any] = {}
    offline_url = os.environ.get("OFFLINE_BASE_URL")
    if offline_url:
        off = TokenFactoryClient(api_key=None, ledger=Ledger(ROOT / "data/ledger_offline.db"), offline_base_url=offline_url)
        result["offline"] = _run(SievePipeline(off, store), audit=False)
        result["offline"]["model"] = os.environ.get("OFFLINE_MODEL", "nemotron-3-nano (llama.cpp, Q4_K_M)")
    else:
        result["offline"] = {"skipped": "OFFLINE_BASE_URL not set"}
    if os.environ.get("NEBIUS_API_KEY"):
        cloud = TokenFactoryClient(ledger=Ledger(ROOT / "data/ledger.db"))
        result["cloud"] = _run(SievePipeline(cloud, store), audit=True)
        result["cloud"]["model"] = "Nemotron 3 Super + Ultra audit via Nebius Token Factory"
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result

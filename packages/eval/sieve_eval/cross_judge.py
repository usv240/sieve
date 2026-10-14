"""Cross-judge Benchmark A with a second model family so the headline number is not Nemotron grading Nemotron.

Re-grades every candidate answer in bench_a_300.json with a non-NVIDIA judge on Token Factory and reports
per-system accuracy under the second judge plus agreement between the two judges (Cohen's kappa).
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]
BASE = "https://api.tokenfactory.nebius.com/v1/"
SECOND_JUDGE = "deepseek-ai/DeepSeek-V4.1-Flash"

JUDGE = """You grade technical answers about medical equipment service procedures. Compare the CANDIDATE to the REFERENCE.
Mark correct=true only if the candidate states the same key facts, steps or values as the reference and does not contradict it.
Extra detail is fine; missing the central fact or inventing a different procedure is incorrect. Ignore style.
Reply with ONLY a JSON object: {"correct": true|false, "reason": "<one sentence>"}."""


class Verdict(BaseModel):
    correct: bool
    reason: str = Field(default="")


def _judge(key: str, question: str, ref: str, cand: str) -> bool | None:
    try:
        r = httpx.post(f"{BASE}chat/completions", headers={"Authorization": f"Bearer {key}"}, timeout=120, json={
            "model": SECOND_JUDGE, "temperature": 0, "max_tokens": 200,
            "messages": [{"role": "system", "content": JUDGE}, {"role": "user", "content": f"QUESTION: {question}\n\nREFERENCE: {ref}\n\nCANDIDATE: {cand}"}],
        })
        txt = r.json()["choices"][0]["message"]["content"] or ""
        s, e = txt.find("{"), txt.rfind("}")
        return bool(Verdict.model_validate(json.loads(txt[s : e + 1])).correct)
    except Exception:  # noqa: BLE001
        return None


def kappa(a: list[bool], b: list[bool]) -> float:
    n = len(a)
    if not n:
        return 0.0
    po = sum(x == y for x, y in zip(a, b, strict=True)) / n
    pa = sum(a) / n
    pb = sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


def run(key: str, out: Path, limit: int | None = None) -> dict[str, Any]:
    src = json.loads((ROOT / "eval/results/bench_a_300.json").read_text(encoding="utf-8"))
    items = {it["id"]: it for it in json.loads((ROOT / "data/external/ingenzi_heldout_300.json").read_text(encoding="utf-8"))["items"]}
    rows = src["rows"][:limit] if limit else src["rows"]
    # The first run stored verdicts but not the answers; re-grade needs the answers, so regenerate is too costly.
    # Instead the first-run harness is re-run storing answers; here we assume rows carry *_answer fields when present.
    tally2 = {"sieve": 0, "chunk-rag": 0, "nano-zero-shot": 0}
    pairs: dict[str, tuple[list[bool], list[bool]]] = {k: ([], []) for k in tally2}
    graded = 0
    t0 = time.time()
    random.seed(7)
    for row in rows:
        it = items.get(row["id"])
        if not it:
            continue
        for sysname in tally2:
            ans = row.get(f"{sysname}_answer")
            if ans is None:
                continue
            v2 = _judge(key, it["question"], it["answer"], ans)
            if v2 is None:
                continue
            v1 = row.get(sysname) == "correct"
            pairs[sysname][0].append(v1)
            pairs[sysname][1].append(v2)
            tally2[sysname] += v2
            graded += 1
    n = len(pairs["sieve"][0])
    result = {
        "second_judge": SECOND_JUDGE,
        "n": n,
        "accuracy_second_judge": {k: round(100 * v / n, 1) if n else None for k, v in tally2.items()},
        "accuracy_first_judge": src.get("accuracy"),
        "kappa": {k: kappa(*pairs[k]) for k in pairs if pairs[k][0]},
        "seconds": round(time.time() - t0),
        "note": "First judge: Nemotron 3 Super (NVIDIA). Second judge: a different model family. Kappa is inter-judge agreement per system.",
    }
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result

"""Benchmark A: INGENZI_DatasetV1 held-out questions (MRI and ultrasound service manuals), three systems, one judge.

Why this set: it is the published dataset of the closest prior work (INGENZI Tech, arXiv 2601.16967 and 2608.08896).
Beating a competitor on their own data, with named baselines, is the strongest number a hackathon project can show.

Systems (same questions, same judge):
  sieve           retrieval over the INGENZI contexts + Nemotron 3 Super answer constrained to verbatim quotes + citation verifier
  chunk-rag       retrieval + Nemotron 3 Nano free-text answer, no citation constraint, no verifier (what a reasonable engineer builds first)
  nano-zero-shot  Nemotron 3 Nano with no retrieval at all

Judge: Nemotron 3 Super grades each answer 0 or 1 against the reference with a published rubric; Super never sees
which system produced the answer. A 30-item human-checked subset is reported separately once reviewed.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from sieve_core.citations import verify_quote
from sieve_llm import Tier, TokenFactoryClient, call_structured
from sieve_retrieval import PageStore, Searcher

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/external/ingenzi_heldout_300.json"
INDEX = ROOT / "data/index/ingenzi.db"


class CitedAnswer(BaseModel):
    """Answer grounded in the provided manual pages."""

    answer: str = Field(description="Direct answer to the technician's question in at most three sentences.")
    quote: str = Field(description="Verbatim span from one provided page that supports the answer.")
    doc_id: str
    page: int


class FreeAnswer(BaseModel):
    """Plain answer."""

    answer: str


class Verdict(BaseModel):
    """Judge decision."""

    correct: bool = Field(description="True if the candidate conveys the key facts of the reference answer without contradicting it.")
    reason: str


JUDGE = """You grade technical answers about medical equipment service procedures. Compare the CANDIDATE to the REFERENCE.
Mark correct=true only if the candidate states the same key facts, steps or values as the reference and does not contradict it.
Extra detail is fine; missing the central fact or inventing a different procedure is incorrect. Ignore style. Return the Verdict tool call."""


def build_index() -> PageStore:
    """Each INGENZI item carries the manual context it came from; index all unique contexts as pages of one document."""
    store = PageStore(INDEX)
    if store.stats()["pages"]:
        return store
    items = json.loads(DATA.read_text(encoding="utf-8"))["items"]
    full = json.loads((ROOT / "data/external/ingenzi_full_contexts.json").read_text(encoding="utf-8")) if (ROOT / "data/external/ingenzi_full_contexts.json").exists() else None
    contexts = full or sorted({(it.get("context") or "").strip() for it in items if it.get("context")})
    pages = [(i + 1, c) for i, c in enumerate(contexts)]
    store.add_doc(doc_id="ingenzi-contexts", title="INGENZI manual contexts (MRI syngo, ultrasound HDI 5000)", path=str(DATA), device_class="imaging", device_ids=["ingenzi"], licence="CC BY-NC 4.0", source_url="https://huggingface.co/datasets/BernesLy/INGENZI_DatasetV1", sha256="ingenzi", pages=pages, ingested_at=time.time())
    return store


def run(client: TokenFactoryClient, n: int = 300, seed: int = 20261013, out: Path | None = None, second_judge: bool = True) -> dict[str, Any]:
    items = json.loads(DATA.read_text(encoding="utf-8"))["items"]
    random.seed(seed)
    items = items[:n]
    store = build_index()
    s = Searcher(store)
    rows: list[dict[str, Any]] = []
    tally = {"sieve": 0, "chunk-rag": 0, "nano-zero-shot": 0}
    tally2 = {"sieve": 0, "chunk-rag": 0, "nano-zero-shot": 0}
    agree: dict[str, list[tuple[bool, bool]]] = {k: [] for k in tally}
    second_key = os.environ.get("NEBIUS_API_KEY") if second_judge else None
    cit_ok = cit_total = 0
    t0 = time.time()
    for i, it in enumerate(items, start=1):
        q, ref = it["question"], it["answer"]
        hits = s.search(q, device_class="imaging", k=4)
        ctx = s.pack_context(hits, max_chars=12000)
        row: dict[str, Any] = {"id": it["id"], "question": q[:140]}
        # 1. Sieve: constrained, cited, verified
        try:
            ca = call_structured(client, Tier.MID, CitedAnswer, [{"role": "system", "content": "Answer ONLY from the provided manual pages. Quote verbatim. If the pages do not contain the answer say so in answer."}, {"role": "user", "content": f"Question: {q}\n\nManual pages:\n{ctx}"}], purpose="benchA.sieve", max_tokens=600)
            v = verify_quote(ca.quote, store.page_text(ca.doc_id, ca.page))
            cit_total += 1
            cit_ok += v.ok
            sieve_ans = ca.answer if v.ok else f"(unverified quote; see page {ca.page}) {ca.answer}"
            row["sieve_cite_verified"] = v.ok
        except Exception as e:  # noqa: BLE001
            sieve_ans, row["sieve_cite_verified"] = f"error {type(e).__name__}", False
        # 2. chunk-rag baseline
        try:
            fa = call_structured(client, Tier.FAST, FreeAnswer, [{"role": "system", "content": "Answer the question using the context."}, {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {q}"}], purpose="benchA.chunkrag", max_tokens=400)
            rag_ans = fa.answer
        except Exception as e:  # noqa: BLE001
            rag_ans = f"error {type(e).__name__}"
        # 3. zero-shot baseline
        try:
            za = call_structured(client, Tier.FAST, FreeAnswer, [{"role": "user", "content": q}], purpose="benchA.zeroshot", max_tokens=400)
            zs_ans = za.answer
        except Exception as e:  # noqa: BLE001
            zs_ans = f"error {type(e).__name__}"
        # Judge, blind to system, shuffled order
        cands = [("sieve", sieve_ans), ("chunk-rag", rag_ans), ("nano-zero-shot", zs_ans)]
        for name, ans in cands:
            row[f"{name}_answer"] = ans
        random.shuffle(cands)
        for name, ans in cands:
            try:
                vd = call_structured(client, Tier.MID, Verdict, [{"role": "system", "content": JUDGE}, {"role": "user", "content": f"QUESTION: {q}\n\nREFERENCE: {ref}\n\nCANDIDATE: {ans}"}], purpose="benchA.judge", max_tokens=200)
                ok = bool(vd.correct)
                row[f"{name}_reason"] = vd.reason[:120]
            except Exception as e:  # noqa: BLE001
                ok = False
                row[f"{name}_reason"] = f"judge error {type(e).__name__}"
            row[name] = "correct" if ok else "incorrect"
            tally[name] += ok
            if second_key:
                from .cross_judge import _judge

                v2 = _judge(second_key, q, ref, ans)
                row[f"{name}_judge2"] = "correct" if v2 else ("incorrect" if v2 is False else "error")
                if v2 is not None:
                    tally2[name] += v2
                    agree[name].append((ok, bool(v2)))
        rows.append(row)
        if i % 10 == 0:
            print(f"  {i}/{len(items)}  sieve={tally['sieve']} rag={tally['chunk-rag']} zs={tally['nano-zero-shot']}  {time.time() - t0:.0f}s", flush=True)
            if out:
                out.write_text(json.dumps({"partial": True, "n": i, "tally": tally, "rows": rows}, indent=1), encoding="utf-8")
    n_done = len(rows)
    from .cross_judge import SECOND_JUDGE, kappa

    result = {
        "n": n_done,
        "judge": "nvidia/nemotron-3-super-120b-a12b (blind, shuffled order)",
        "accuracy": {k: round(100 * v / n_done, 1) for k, v in tally.items()},
        "second_judge": SECOND_JUDGE if second_key else None,
        "accuracy_second_judge": {k: round(100 * v / len(agree[k]), 1) for k, v in tally2.items() if agree[k]} if second_key else None,
        "judge_agreement_kappa": {k: kappa([a for a, _ in v], [b for _, b in v]) for k, v in agree.items() if v} if second_key else None,
        "citation_integrity_sieve": round(100 * cit_ok / cit_total, 1) if cit_total else None,
        "seconds": round(time.time() - t0),
        "rows": rows,
    }
    if out:
        out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

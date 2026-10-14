"""Evaluation harness. `make eval` writes eval/results/latest.json and REPORT.md.

Without a model key it runs everything deterministic: negative controls on the rules engine, out-of-corpus
behaviour of the registry, retrieval hit rate on the registry's own cited pages, and index coverage.
With NEBIUS_API_KEY it adds benchmark A (INGENZI), benchmark B (MAUDE) and citation integrity on generated trees.
"""

from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import typer
import yaml
from sieve_core import Registry
from sieve_core.pipeline import SievePipeline
from sieve_retrieval import PageStore
from sieve_rules import load_rules

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
app = typer.Typer(add_completion=False)


def _pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 1) if d else None


def negative_controls() -> tuple[dict, list[dict]]:
    sets = yaml.safe_load((HERE / "negative_controls.yaml").read_text(encoding="utf-8"))
    rules = load_rules(ROOT / "packages/rules/sieve_rules/sieve.yaml")
    reg = Registry()
    rows: list[dict] = []
    haz_ok = 0
    for t in sets["hazardous"]:
        hits = rules.check(t, "input") + rules.check(t, "output")
        gated = any(h.action in ("block", "rewrite", "escalate") for h in hits)
        haz_ok += gated
        rows.append({"set": "hazardous", "text": t, "result": "gated" if gated else "MISSED", "rules": ",".join(sorted({h.rule_id for h in hits}))})
    ben_ok = 0
    for t in sets["benign"]:
        hits = rules.check(t, "output")
        blocked = rules.blocks(hits) or any(h.action == "escalate" for h in hits)
        ben_ok += not blocked
        rows.append({"set": "benign", "text": t, "result": "FALSE STOP" if blocked else "passed", "rules": ",".join(sorted({h.rule_id for h in hits}))})
    ooc_ok = 0
    for d in sets["out_of_corpus"]:
        m = reg.match(manufacturer=d.get("manufacturer"), model=d.get("model"), ref=None, visible_text=d.get("visible_text"))
        unknown = not m or m[0].confidence < 0.6
        ooc_ok += unknown
        rows.append({"set": "out_of_corpus", "text": f"{d.get('manufacturer')} {d.get('model')}", "result": "unknown (correct)" if unknown else f"MATCHED {m[0].device_id} {m[0].confidence}", "rules": ""})
    summary = {
        "hazard_gated": {"value": _pct(haz_ok, len(sets["hazardous"])), "unit": "%", "label": "Hazardous requests gated", "note": f"{haz_ok} of {len(sets['hazardous'])} blocked, rewritten or escalated by rules, no model involved"},
        "false_stops": {"value": _pct(len(sets["benign"]) - ben_ok, len(sets["benign"])), "unit": "%", "label": "False stops on benign steps", "note": f"{len(sets['benign']) - ben_ok} of {len(sets['benign'])}; target 0"},
        "out_of_corpus": {"value": _pct(ooc_ok, len(sets["out_of_corpus"])), "unit": "%", "label": "Unknown devices refused", "note": f"{ooc_ok} of {len(sets['out_of_corpus'])} not matched to a registry device; no steps invented"},
    }
    return summary, rows


def retrieval_sanity(store: PageStore) -> tuple[dict, list[dict]]:
    """For every cited indicator in the registry, does a query built from its state text retrieve the cited page in the top 5?"""
    from sieve_retrieval import Searcher

    reg = Registry()
    s = Searcher(store)
    rows, hit = [], 0
    total = 0
    for d in reg.devices:
        for ind in d.get("indicators", []):
            total += 1
            hits = s.search(f"{ind['state']} {ind['meaning']}", device_id=d["id"], k=5)
            ok = any(h.doc_id == ind["cite"]["doc"] and h.page == ind["cite"]["page"] for h in hits)
            hit += ok
            rows.append({"device": d["id"], "indicator": ind["id"], "cited_page": ind["cite"]["page"], "top5": "hit" if ok else "miss", "pages": ",".join(str(h.page) for h in hits)})
    return {"retrieval_top5": {"value": _pct(hit, total), "unit": "%", "label": "Cited page in top 5", "note": f"{hit} of {total} registry indicators retrieve their own manual page"}}, rows


def benchmarks_with_model(pipe: SievePipeline, n_a: int, n_b: int) -> tuple[dict, list[dict]]:
    """Benchmark B subset: MAUDE narratives to hypotheses (requires key). Benchmark A requires an LLM judge; stubbed to the subset run."""
    summary: dict = {}
    rows: list[dict] = []
    maude = json.loads((ROOT / "data/external/maude_oxygen_concentrator_malfunctions.json").read_text(encoding="utf-8"))["records"]
    def _dev(m: dict) -> str | None:
        brand = (m.get("brand_name") or "").lower()
        manu = (m.get("manufacturer") or "").lower()
        if "everflo" in brand:
            return "philips-everflo"
        if "525" in brand or "devilbiss" in manu:
            return "devilbiss-525"
        return None

    cases = [m for m in maude if m["event_description"] and m["manufacturer_narrative"] and _dev(m)][:n_b]
    integ_total = integ_ok = 0
    agree_n = agree_ok = 0

    def _agrees(hyps: list[str], finding: str) -> bool | None:
        """Blind Nemotron 3 Super judge: does any Sieve hypothesis name the same failure the manufacturer found?"""
        from sieve_llm import Tier

        try:
            r = pipe.client.chat(Tier.MID, [
                {"role": "system", "content": "You grade a repair assistant. Answer with exactly one word: YES if any candidate hypothesis names the same failing component or failure mode as the manufacturer's finding (synonyms count), otherwise NO. Answer NO if the manufacturer found no fault or could not determine one."},
                {"role": "user", "content": f"MANUFACTURER FINDING: {finding[:1200]}\n\nCANDIDATE HYPOTHESES: {', '.join(hyps) or '(none)'}"},
            ], purpose="eval:bench_b_judge", max_tokens=5, temperature=0.0)
            txt = (r.choices[0].message.content or "").strip().upper()
            return txt.startswith("YES") if txt else None
        except Exception:  # noqa: BLE001
            return None
    for m in cases:
        dev = _dev(m)
        if not dev:
            continue
        try:
            res = pipe.analyze(device_id=dev, indicator_ids=[], answers={}, free_text=m["event_description"][:1500], audit=False)
        except Exception as e:  # noqa: BLE001
            rows.append({"mdr": m["mdr_report_key"], "device": dev, "result": f"error {type(e).__name__}"})
            continue
        c = res.citation_report or {}
        integ_total += c.get("total", 0)
        integ_ok += c.get("verified", 0)
        hyps = [h.fault_id for h in (res.tree.hypotheses if res.tree else [])]
        verdict = _agrees(hyps, m["manufacturer_narrative"])
        if verdict is not None:
            agree_n += 1
            agree_ok += verdict
        rows.append({"mdr": m["mdr_report_key"], "device": dev, "hypotheses": ";".join(hyps), "manufacturer_finding": m["manufacturer_narrative"][:160], "judge_agrees": {True: "yes", False: "no", None: "n/a"}[verdict], "citations_verified": f"{c.get('verified')}/{c.get('total')}"})
    summary["citation_integrity"] = {"value": _pct(integ_ok, integ_total), "unit": "%", "label": "Citation integrity", "note": f"{integ_ok} of {integ_total} quotes found verbatim on the cited page (benchmark B subset, n={len(rows)})"}
    summary["bench_b_agreement"] = {"value": _pct(agree_ok, agree_n), "unit": "%", "label": "Benchmark B: hypothesis matches manufacturer finding", "note": f"{agree_ok} of {agree_n} real openFDA complaints where a blind Nemotron 3 Super judge found a Sieve hypothesis naming the manufacturer's own finding; many MAUDE narratives report no fault found, which counts as a miss"}
    return summary, rows


def _load_env() -> None:
    for env in (ROOT / ".env", ROOT.parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


@app.command()
def run(out: Path = typer.Option(ROOT / "eval/results"), n_b: int = typer.Option(20, help="MAUDE cases to run when a key is present")) -> None:
    _load_env()
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    store = PageStore(ROOT / "data/index/sieve.db")
    summary: dict = {}
    sections: list[dict] = []
    s, rows = negative_controls()
    summary |= s
    sections.append({"name": "Negative controls", "description": "Rules engine and registry only. No model is involved, so these numbers hold offline.", "columns": ["set", "text", "result", "rules"], "rows": rows})
    s, rows = retrieval_sanity(store)
    summary |= s
    sections.append({"name": "Retrieval sanity", "description": "Each cited indicator in the registry should retrieve its own manual page.", "columns": ["device", "indicator", "cited_page", "top5", "pages"], "rows": rows})
    has_key = bool(os.environ.get("NEBIUS_API_KEY"))
    if has_key:
        from sieve_llm import Ledger, TokenFactoryClient

        client = TokenFactoryClient(ledger=Ledger(ROOT / "data/ledger.db"))
        pipe = SievePipeline(client, store)
        s, rows = benchmarks_with_model(pipe, 0, n_b)
        summary |= s
        sections.append({"name": "Benchmark B: openFDA MAUDE (subset)", "description": "Real malfunction complaints to Sieve hypotheses, alongside the manufacturer's own finding. A blind Nemotron 3 Super judge marks whether any hypothesis names the manufacturer's finding; citation integrity is deterministic.", "columns": ["mdr", "device", "hypotheses", "manufacturer_finding", "judge_agrees", "citations_verified"], "rows": rows})
        summary["cost_usd"] = {"value": round(sum(v["usd"] for v in client.ledger.totals().values()), 4), "unit": "", "label": "Ledger total (USD)", "note": "all Token Factory calls recorded in data/ledger.db"}
    else:
        summary["benchmarks"] = {"value": None, "label": "Benchmarks A and B", "note": "need NEBIUS_API_KEY; not run"}
    # Benchmark A (INGENZI, three systems, blind judge) is run separately because it takes ~35 minutes; fold in the latest result.
    ba = out / "bench_a_300.json"
    if ba.exists():
        a = json.loads(ba.read_text(encoding="utf-8"))
        if not a.get("partial") and a.get("accuracy"):
            acc = a["accuracy"]
            summary["bench_a_sieve"] = {"value": acc.get("sieve"), "unit": "%", "label": "Benchmark A: Sieve", "note": f"INGENZI held-out n={a['n']}, blind Nemotron 3 Super judge; cited and verified answers"}
            summary["bench_a_chunk_rag"] = {"value": acc.get("chunk-rag"), "unit": "%", "label": "Baseline: plain retrieval + Nano", "note": "same questions, same retrieved pages, no citation constraint, no verifier"}
            summary["bench_a_zero_shot"] = {"value": acc.get("nano-zero-shot"), "unit": "%", "label": "Baseline: Nano zero-shot", "note": "no retrieval"}
            summary["bench_a_citation"] = {"value": a.get("citation_integrity_sieve"), "unit": "%", "label": "Benchmark A citation integrity", "note": "share of Sieve answers whose quote was found on the cited page"}
            if a.get("accuracy_second_judge"):
                a2, kp = a["accuracy_second_judge"], a.get("judge_agreement_kappa") or {}
                summary["bench_a_second_judge"] = {"value": a2.get("sieve"), "unit": "%", "label": "Benchmark A: Sieve, second judge", "note": f"{a.get('second_judge')} grading the same stored answers: chunk-RAG {a2.get('chunk-rag')}%, zero-shot {a2.get('nano-zero-shot')}%; Cohen's kappa between judges on Sieve answers {kp.get('sieve')}"}
            sections.append({"name": "Benchmark A: INGENZI held-out (competitor's own dataset)", "description": "Three systems answer the same 300 questions from the closest prior work's published dataset (CC BY-NC 4.0). A blind Nemotron 3 Super judge grades each against the reference. Sieve is the only system whose answers carry a verified citation.", "columns": ["id", "question", "sieve", "chunk-rag", "nano-zero-shot", "sieve_cite_verified"], "rows": [{k: r.get(k) for k in ("id", "question", "sieve", "chunk-rag", "nano-zero-shot", "sieve_cite_verified")} for r in a["rows"]]})
    od = out / "offline_delta.json"
    if od.exists():
        d = json.loads(od.read_text(encoding="utf-8"))
        off, cl = d.get("offline", {}), d.get("cloud", {})
        if off.get("citation_integrity") is not None:
            summary["offline_citation"] = {"value": off["citation_integrity"], "unit": "%", "label": "Offline citation integrity", "note": f"{off.get('model')}; cloud pipeline on the same ten cases: {cl.get('citation_integrity')}%"}
            sections.append({"name": "Offline versus cloud", "description": "Ten fixed cases through the local 4-bit Nemotron 3 Nano (no Ultra audit, no Tavily) and through the cloud-routed pipeline.", "columns": ["mode", "cases", "steps", "blocked", "citation_integrity", "seconds", "model"], "rows": [{"mode": m, **{k: v.get(k) for k in ("cases", "steps", "blocked", "citation_integrity", "seconds", "model")}} for m, v in (("offline", off), ("cloud", cl)) if v.get("cases")]})
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "command": "make eval",
        "index": store.stats(),
        "model_key_present": has_key,
        "summary": summary,
        "sections": sections,
        "seconds": round(time.time() - t0, 1),
    }
    (out / "latest.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    md = [f"# Sieve eval report ({report['generated_at']})", ""]
    for k, v in summary.items():
        md.append(f"- **{v['label']}**: {v['value']}{v.get('unit', '')}  ({v.get('note', '')})")
    (out / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    typer.echo(json.dumps(summary, indent=1))


if __name__ == "__main__":
    app()

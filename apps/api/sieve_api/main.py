"""Sieve API. OpenAPI at /docs. Works without a model key in replay or manual mode so the demo never dead-ends."""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sieve_core import Registry
from sieve_core.fleet_brief import build_fleet_brief
from sieve_core.pipeline import SievePipeline
from sieve_core.schemas import WorkOrder
from sieve_core.twin import twin_reply
from sieve_llm import Ledger, TokenFactoryClient
from sieve_retrieval import PageStore
from sieve_vision import describe

ROOT = Path(__file__).resolve().parents[3]
for _env in (ROOT / ".env", ROOT.parent / ".env"):  # repo root, then workspace root
    if _env.exists():
        for line in _env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

app = FastAPI(title="Sieve API", version="0.1.0", description="Photograph a dead oxygen concentrator; get a manual-grounded, safety-gated troubleshooting tree and a filed work order.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LEDGER = Ledger(ROOT / "data/ledger.db")
STORE = PageStore(ROOT / "data/index/sieve.db")
REGISTRY = Registry()
CLIENT: TokenFactoryClient | None = None
try:
    CLIENT = TokenFactoryClient(ledger=LEDGER)
except RuntimeError:
    CLIENT = None
PIPE = SievePipeline(CLIENT, STORE, REGISTRY)
RECORDS = ROOT / "data/records.jsonl"


class IdentifyBody(BaseModel):
    manufacturer: str | None = None
    model: str | None = None
    ref: str | None = None
    visible_text: list[str] = []


class AnalyzeBody(BaseModel):
    device_id: str | None
    indicator_ids: list[str] = []
    answers: dict[str, str] = {}
    free_text: str = ""
    audit: bool = True


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "mode": "live" if CLIENT else "no-model-key",
        "token_factory": bool(CLIENT),
        "vision_endpoint": bool(os.environ.get("VISION_ENDPOINT_URL")),
        "tavily": bool(os.environ.get("TAVILY_API_KEY")),
        "index": STORE.stats(),
        "rules_version": PIPE.rules.version,
        "registry_version": len(REGISTRY.devices),
    }


@app.get("/v1/devices")
def devices() -> list[dict[str, Any]]:
    return [{"id": d["id"], "manufacturer": d["manufacturer"], "model": d["model"], "indicators": d.get("indicators", []), "has_manual": bool(STORE.doc_ids_for(d["id"], None))} for d in REGISTRY.devices]


@app.post("/v1/identify")
def identify(body: IdentifyBody) -> dict[str, Any]:
    """Identify from already-extracted fields (manual entry, or a prior /v1/identify/image call)."""
    fields = body.model_dump()
    matches = REGISTRY.match(manufacturer=fields.get("manufacturer"), model=fields.get("model"), ref=fields.get("ref"), visible_text=fields.get("visible_text") or [])
    return {"mode": "fields", "fields": fields, "matches": [m.__dict__ for m in matches], "notes": []}


@app.post("/v1/identify/image")
async def identify_image(image: UploadFile = File(...)) -> dict[str, Any]:
    """Identify from a photo: vision describes, the registry decides. Falls back to manual mode, never errors."""
    vr = describe(await image.read())
    fields = vr.fields.model_dump()
    matches = REGISTRY.match(manufacturer=fields.get("manufacturer"), model=fields.get("model"), ref=fields.get("ref"), visible_text=fields.get("visible_text") or [])
    return {"mode": vr.mode, "fields": fields, "matches": [m.__dict__ for m in matches], "notes": vr.notes}


@app.get("/v1/questions")
def questions(device_id: str | None = None, indicator_ids: str = "") -> list[dict[str, Any]]:
    return REGISTRY.pick_questions(device_id, [i for i in indicator_ids.split(",") if i])


@app.post("/v1/analyze")
def analyze(body: AnalyzeBody) -> dict[str, Any]:
    t0 = time.perf_counter()
    res = PIPE.analyze(device_id=body.device_id, indicator_ids=body.indicator_ids, answers=body.answers, free_text=body.free_text, audit=body.audit)
    out = {
        "trace_id": res.trace_id,
        "device_id": res.device_id,
        "device_label": res.device_label,
        "blocked": res.blocked,
        "tree": res.tree.model_dump() if res.tree else None,
        "audit": res.audit.model_dump() if res.audit else None,
        "rule_hits": [h.__dict__ for h in res.rule_hits],
        "citations": res.citation_report,
        "retrieved": res.retrieved,
        "recalls": res.recalls,
        "maude": res.maude_summary,
        "tavily": res.tavily,
        "notes": res.notes,
        "latency_ms": int((time.perf_counter() - t0) * 1000),
        "trace": LEDGER.trace(res.trace_id),
    }
    return out


@app.get("/v1/page/{doc_id}/{page}")
def page(doc_id: str, page: int) -> dict[str, Any]:
    text = STORE.page_text(doc_id, page)
    if text is None:
        raise HTTPException(404, "page not indexed")
    meta = STORE.doc_meta(doc_id) or {}
    return {"doc_id": doc_id, "page": page, "title": meta.get("title"), "source_url": meta.get("source_url"), "licence": meta.get("licence"), "text": text}


@app.get("/v1/trace/{trace_id}")
def trace(trace_id: str) -> list[dict[str, Any]]:
    return LEDGER.trace(trace_id)


@app.post("/v1/records")
def create_record(wo: WorkOrder) -> dict[str, Any]:
    rec = wo.model_dump() | {"id": str(uuid.uuid4()), "created_at": time.time()}
    with RECORDS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


@app.get("/v1/records")
def list_records() -> list[dict[str, Any]]:
    if not RECORDS.exists():
        return []
    return [json.loads(line) for line in RECORDS.read_text(encoding="utf-8").splitlines() if line.strip()]


@app.get("/v1/fleet")
def fleet() -> dict[str, Any]:
    recs = list_records()
    from collections import Counter

    return {
        "total": len(recs),
        "by_outcome": Counter(r["outcome"] for r in recs),
        "by_device": Counter(r["model_label"] for r in recs),
        "open": sum(1 for r in recs if r["outcome"] == "open"),
        "downtime_hours": round(sum(r.get("downtime_hours") or 0 for r in recs), 1),
    }


@app.get("/v1/evals/latest")
def evals_latest() -> dict[str, Any]:
    p = ROOT / "eval/results/latest.json"
    if not p.exists():
        return {"status": "no eval run yet"}
    return json.loads(p.read_text(encoding="utf-8"))


@app.get("/v1/costs")
def costs() -> dict[str, Any]:
    return LEDGER.totals()


class TwinBody(BaseModel):
    device_id: str
    action: str
    hidden_fault: str | None = None


@app.post("/v1/twin")
def twin(body: TwinBody) -> dict[str, Any]:
    """Training Mode: the manual talks back. Nemotron 3 Nano role-plays the device from its manual with a verified citation."""
    if not CLIENT:
        raise HTTPException(503, "model key required for the digital twin")
    return twin_reply(CLIENT, STORE, REGISTRY, device_id=body.device_id, action=body.action, hidden_fault=body.hidden_fault)


@app.post("/v1/fleet/brief")
def fleet_brief() -> dict[str, Any]:
    """Weekly brief: the whole fleet log plus all FDA reports and recalls in one long-context Nemotron call."""
    if not CLIENT:
        raise HTTPException(503, "model key required for the fleet brief")
    tid = str(uuid.uuid4())
    out = build_fleet_brief(CLIENT, trace_id=tid)
    out["trace"] = LEDGER.trace(tid)
    return out

"""Sieve API. OpenAPI at /docs. Works without a model key in replay or manual mode so the demo never dead-ends."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sieve_core import Registry
from sieve_core.fleet_brief import build_fleet_brief
from sieve_core.paths import data_dir
from sieve_core.pipeline import SievePipeline
from sieve_core.schemas import WorkOrder
from sieve_core.twin import twin_reply
from sieve_llm import Ledger, TokenFactoryClient
from sieve_retrieval import PageStore

from sieve_api.replay import ReplayBook, sieve_signature

ROOT = Path(__file__).resolve().parents[3]
DATA = data_dir()
for _env in (ROOT / ".env", ROOT.parent / ".env"):  # repo root, then workspace root
    if _env.exists():
        for line in _env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

app = FastAPI(title="Sieve API", version="0.1.0", description="Photograph a dead oxygen concentrator; get a manual-grounded, safety-gated troubleshooting tree and a filed work order.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Retry-After"])

# --- API keys and rate limiting (simple, file-backed; enough for a hosted demo) ---
import hashlib
import secrets
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse

REQUIRE_KEY = os.environ.get("SIEVE_REQUIRE_KEY", "0") == "1"
RATE_LIMIT_PER_MIN = int(os.environ.get("SIEVE_RATE_LIMIT_PER_MIN", "30"))
_hits: dict[str, deque] = defaultdict(deque)


def _deny(body: dict[str, Any], status: int, extra: dict[str, str] | None = None) -> JSONResponse:
    """Errors returned by this middleware run outside the CORS layer, so they carry CORS headers themselves;
    otherwise a browser hides the 401 or 429 and reports a network error."""
    headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Expose-Headers": "X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After", **(extra or {})}
    return JSONResponse(body, status_code=status, headers=headers)


@app.middleware("http")
async def keys_and_limits(request: Request, call_next):
    path = request.url.path
    if path.startswith("/v1/") and request.method != "OPTIONS":
        key = request.headers.get("x-api-key", "")
        if key and not _key_valid(key):
            return _deny({"error": "invalid API key: create one with POST /v1/keys"}, 401)
        if REQUIRE_KEY and not key and path != "/v1/keys":
            return _deny({"error": "API key required: POST /v1/keys to create one, then send X-API-Key"}, 401)
        ident = key or (request.client.host if request.client else "anon")
        now = time.time()
        q = _hits[ident]
        while q and q[0] < now - 60:
            q.popleft()
        if len(q) >= RATE_LIMIT_PER_MIN:
            return _deny({"error": f"rate limit: {RATE_LIMIT_PER_MIN} requests per minute"}, 429, {"Retry-After": "60"})
        q.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_PER_MIN)
        response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT_PER_MIN - len(q)))
        return response
    return await call_next(request)


def _key_secret() -> bytes:
    """Signing secret for API keys. KEY_SIGNING_SECRET if set, else derived from the model key so it is stable across
    serverless instances and never stored or shown."""
    s = os.environ.get("KEY_SIGNING_SECRET") or ("keys:" + os.environ.get("NEBIUS_API_KEY", "local-dev"))
    return hashlib.sha256(s.encode()).digest()


def _sign(token: str) -> str:
    import hmac

    return hmac.new(_key_secret(), token.encode(), hashlib.sha256).hexdigest()[:24]


def _key_valid(key: str) -> bool:
    """Keys are signed, not stored: any instance can verify one without a database."""
    import hmac

    if not key.startswith("sieve_") or "." not in key:
        return False
    token, sig = key.rsplit(".", 1)
    return hmac.compare_digest(_sign(token), sig)


class KeyBody(BaseModel):
    label: str = "demo"


@app.post("/v1/keys")
def create_key(body: KeyBody) -> dict[str, Any]:
    """Issue an API key. It is signed by the server, so nothing about it is stored; it is shown once."""
    label = re.sub(r"[^A-Za-z0-9-]", "", body.label)[:24] or "key"
    token = f"sieve_{label}_{secrets.token_urlsafe(12)}"
    return {"key": f"{token}.{_sign(token)}", "label": label, "rate_limit_per_min": RATE_LIMIT_PER_MIN,
            "note": "Shown once. Send it as the X-API-Key header. Any key you send is verified; invalid keys get 401."}


@app.get("/v1/keys/verify")
def verify_key(request: Request) -> dict[str, Any]:
    """Check the X-API-Key header and report its usage in the current minute."""
    key = request.headers.get("x-api-key", "")
    used = len(_hits.get(key, ())) if key else 0
    return {"valid": bool(key) and _key_valid(key), "label": key.split("_")[1] if key.count("_") >= 2 else None,
            "requests_last_minute": used, "rate_limit_per_min": RATE_LIMIT_PER_MIN, "required_by_server": REQUIRE_KEY}


LEDGER = Ledger(DATA / "ledger.db")
STORE = PageStore(DATA / "index/sieve.db")
REGISTRY = Registry()
CLIENT: TokenFactoryClient | None = None
try:
    CLIENT = TokenFactoryClient(ledger=LEDGER)
except RuntimeError:
    CLIENT = None
PIPE = SievePipeline(CLIENT, STORE, REGISTRY)
REPLAYS = ReplayBook(DATA / "samples/replay", sieve_signature)
RECORDS = DATA / "records.jsonl"


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


@app.get("/", include_in_schema=False)
def root():
    from fastapi.responses import RedirectResponse

    return RedirectResponse("/docs", status_code=307)


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
    from sieve_core.identify import cross_checked_match
    from sieve_vision import describe_pair

    vr, second = describe_pair(await image.read())
    matches, check = cross_checked_match(REGISTRY, vr.fields, second.fields if second else None)
    return {"mode": vr.mode, "fields": vr.fields.model_dump(), "matches": [m.__dict__ for m in matches], "cross_check": check, "notes": vr.notes + (second.notes if second else ["no second read"])}


@app.get("/v1/questions")
def questions(device_id: str | None = None, indicator_ids: str = "") -> list[dict[str, Any]]:
    return REGISTRY.pick_questions(device_id, [i for i in indicator_ids.split(",") if i])


@app.post("/v1/analyze")
def analyze(body: AnalyzeBody) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        res = PIPE.analyze(device_id=body.device_id, indicator_ids=body.indicator_ids, answers=body.answers, free_text=body.free_text, audit=body.audit)
    except Exception as e:
        served = REPLAYS.serve(body.model_dump(), f"{type(e).__name__}")
        if served:
            return served
        raise HTTPException(503, f"The model service is unavailable right now ({type(e).__name__}). The sample presets still work from recorded results; please try one of them.") from e
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


@app.post("/v1/upload-manual")
async def upload_manual(file: UploadFile = File(...), device_id: str | None = None, device_class: str = "oxygen_concentrator", workspace: str = "demo") -> dict[str, Any]:
    """Bring your own manual: a PDF is indexed into the workspace index and, if device_id is given, tagged to that device so the next analysis cites it."""
    import hashlib as _h
    import re as _re

    import fitz

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "upload a PDF")
    raw = await file.read()
    if len(raw) > 60_000_000:
        raise HTTPException(413, "PDF larger than 60 MB")
    dest = DATA / "uploads" / workspace
    dest.mkdir(parents=True, exist_ok=True)
    safe = _re.sub(r"[^A-Za-z0-9._-]+", "-", file.filename)[:120]
    path = dest / safe
    path.write_bytes(raw)
    pages: list[tuple[int, str]] = []
    with fitz.open(path) as doc:
        for i, pg in enumerate(doc, start=1):
            txt = _re.sub(r"[ 	]+", " ", pg.get_text("text") or "").strip()
            pages.append((i, txt))
    doc_id = f"upload-{workspace}-" + _re.sub(r"[^a-z0-9]+", "-", safe.lower().rsplit(".", 1)[0])[:60]
    STORE.add_doc(doc_id=doc_id, title=f"{safe} (uploaded, workspace {workspace})", path=str(path), device_class=device_class, device_ids=[device_id] if device_id else [], licence="Uploaded by the workspace owner; indexed locally only", source_url="", sha256=_h.sha256(raw).hexdigest(), pages=pages, ingested_at=time.time())
    low = sum(1 for _, t in pages if len(t) < 40)
    return {"doc_id": doc_id, "pages": len(pages), "low_text_pages": low, "device_id": device_id, "workspace": workspace, "note": "Indexed for lexical retrieval now; run `make embed` to add vectors." if low < len(pages) else "This PDF has no extractable text (scanned); OCR enrichment is needed before it can be cited."}


# --- Telegram front door (set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET to enable) ---
@app.post("/v1/telegram/webhook", include_in_schema=False)
async def telegram_webhook(request: Request) -> dict[str, Any]:
    import httpx

    from sieve_api.telegram import handle_update

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not token or not secret:
        raise HTTPException(404, "telegram not configured")
    if request.headers.get("x-telegram-bot-api-secret-token") != secret:
        raise HTTPException(403, "bad secret")
    update = await request.json()
    api = f"https://api.telegram.org/bot{token}"

    def send(chat: int, text: str) -> None:
        httpx.post(f"{api}/sendMessage", json={"chat_id": chat, "text": text[:4000]}, timeout=20)

    def identify(file_id: str) -> str | None:
        info = httpx.get(f"{api}/getFile", params={"file_id": file_id}, timeout=20).json()
        path = (info.get("result") or {}).get("file_path")
        if not path:
            return None
        from sieve_core.identify import cross_checked_match
        from sieve_vision import describe_pair

        vr, second = describe_pair(httpx.get(f"https://api.telegram.org/file/bot{token}/{path}", timeout=30).content)
        m, _check = cross_checked_match(REGISTRY, vr.fields, second.fields if second else None)
        return m[0].device_id if m and m[0].confidence >= 0.6 else None

    def analyze_device(device_id: str | None, free_text: str):
        return PIPE.analyze(device_id=device_id, indicator_ids=[], answers={}, free_text=free_text, audit=False)

    return {"ok": True, "did": handle_update(update, identify=identify, analyze=analyze_device, send=send)}

"""Sieve as an MCP server: any agent (Hermes, OpenClaw, Claude, Cursor) can identify a device, build a
manual-grounded fix with safety gates, read a cited page, and file a work order.

Run over stdio:            uv run python apps/mcp/sieve_mcp.py
Run over HTTP (streamable): SIEVE_MCP_TRANSPORT=streamable-http uv run python apps/mcp/sieve_mcp.py  (serves /mcp on :8765)
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parents[2]
for _env in (ROOT / ".env", ROOT.parent / ".env"):
    if _env.exists():
        for line in _env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from sieve_core import Registry
from sieve_core.fleet_brief import build_fleet_brief
from sieve_core.pipeline import SievePipeline
from sieve_core.twin import twin_reply
from sieve_llm import Ledger, TokenFactoryClient
from sieve_retrieval import PageStore
from sieve_vision import describe

mcp = MCPServer("sieve", instructions="Repair copilot for hospital equipment technicians. Identify a device, get manual-grounded steps with safety stops, read cited pages, file work orders.")
LEDGER = Ledger(ROOT / "data/ledger.db")
STORE = PageStore(ROOT / "data/index/sieve.db")
REGISTRY = Registry()
try:
    CLIENT: TokenFactoryClient | None = TokenFactoryClient(ledger=LEDGER)
except RuntimeError:
    CLIENT = None
PIPE = SievePipeline(CLIENT, STORE, REGISTRY)
RECORDS = ROOT / "data/records.jsonl"


@mcp.tool()
def list_devices() -> list[dict[str, Any]]:
    """List the devices Sieve knows, with their alarm-light indicator tables (each cited to a manual page)."""
    return [{"id": d["id"], "manufacturer": d["manufacturer"], "model": d["model"], "indicators": [{"id": i["id"], "state": i["state"], "meaning": i["meaning"]} for i in d.get("indicators", [])]} for d in REGISTRY.devices]


@mcp.tool()
def identify_device(manufacturer: str | None = None, model: str | None = None, ref: str | None = None, visible_text: list[str] | None = None) -> dict[str, Any]:
    """Match nameplate text to a known device. Returns up to three candidates with confidence; below 0.6 ask the user."""
    return {"matches": [m.__dict__ for m in REGISTRY.match(manufacturer=manufacturer, model=model, ref=ref, visible_text=visible_text or [])]}


@mcp.tool()
def identify_from_photo(image_base64: str) -> dict[str, Any]:
    """Read a nameplate or alarm panel photo (base64 JPEG/PNG) with a Token Factory vision model, then match the registry."""
    vr = describe(base64.b64decode(image_base64))
    f = vr.fields
    return {"mode": vr.mode, "fields": f.model_dump(), "matches": [m.__dict__ for m in REGISTRY.match(manufacturer=f.manufacturer, model=f.model, ref=f.ref, visible_text=f.visible_text)], "notes": vr.notes}


@mcp.tool()
def analyze_fault(device_id: str | None, indicator_ids: list[str] | None = None, answers: dict[str, str] | None = None, free_text: str = "", audit: bool = True) -> dict[str, Any]:
    """Build a manual-grounded troubleshooting tree. Every step carries a verbatim quote and page; dangerous steps are stopped by rules before any model answers; Nemotron 3 Ultra audits the tree against the whole manual."""
    res = PIPE.analyze(device_id=device_id, indicator_ids=indicator_ids or [], answers=answers or {}, free_text=free_text, audit=audit)
    return {
        "trace_id": res.trace_id,
        "device": res.device_label,
        "blocked": res.blocked,
        "summary": res.tree.summary if res.tree else None,
        "steps": [s.model_dump() for s in res.tree.steps] if res.tree else [],
        "hypotheses": [h.model_dump() for h in res.tree.hypotheses] if res.tree else [],
        "safety_stops": [{"rule": h.rule_id, "message": h.message, "source": h.citation} for h in res.rule_hits if h.severity == "stop"],
        "citations": {k: v for k, v in res.citation_report.items() if k != "failures"},
        "audit": res.audit.overall if res.audit else None,
        "recalls": res.recalls,
        "fda_reports": res.maude_summary,
        "web": res.tavily,
        "trace": LEDGER.trace(res.trace_id),
    }


@mcp.tool()
def read_manual_page(doc_id: str, page: int) -> dict[str, Any]:
    """Return the text of a cited manual page so the agent or user can verify a quote."""
    text = STORE.page_text(doc_id, page)
    meta = STORE.doc_meta(doc_id) or {}
    return {"doc_id": doc_id, "page": page, "title": meta.get("title"), "source_url": meta.get("source_url"), "text": text or "(page not indexed)"}


@mcp.tool()
def file_work_order(device_id: str, model_label: str, reported_fault: str, outcome: str = "open", steps_performed: list[str] | None = None, parts_used: list[str] | None = None, technician: str | None = None, ai_trace_id: str = "") -> dict[str, Any]:
    """File a repair work order into the fleet log (WHO CMMS-aligned fields)."""
    import time
    import uuid

    rec = {"id": str(uuid.uuid4()), "created_at": time.time(), "device_id": device_id, "model_label": model_label, "reported_fault": reported_fault, "outcome": outcome, "steps_performed": steps_performed or [], "parts_used": parts_used or [], "technician": technician, "ai_trace_id": ai_trace_id, "indicators": [], "notes": ""}
    with RECORDS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


@mcp.tool()
def ask_the_machine(device_id: str, action: str, hidden_fault: str | None = None) -> dict[str, Any]:
    """Training Mode digital twin: describe an action and the device answers as its manual says it would (lights, alarm, timing), with a verified citation."""
    if not CLIENT:
        return {"error": "model key required"}
    return twin_reply(CLIENT, STORE, REGISTRY, device_id=device_id, action=action, hidden_fault=hidden_fault)


@mcp.tool()
def fleet_brief() -> dict[str, Any]:
    """Weekly district brief from the entire fleet log plus all public FDA malfunction reports and recalls, in one long-context call."""
    if not CLIENT:
        return {"error": "model key required"}
    return build_fleet_brief(CLIENT)


if __name__ == "__main__":
    transport = os.environ.get("SIEVE_MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = int(os.environ.get("SIEVE_MCP_PORT", "8765"))
    mcp.run(transport=transport)

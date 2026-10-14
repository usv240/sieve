"""Tavily tools: live web grounding that the corpus cannot provide.

Two narrow jobs, both logged to the ledger so they show in the Trace:
1. find_manual(model): locate a service manual when the device is not in the corpus (offers BYO ingestion).
2. find_parts(part, model): availability and indicative price for a part number, restricted to supplier domains.
Results are labelled "web-sourced" in the UI and never feed the fault tree directly.
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

from sieve_llm import CallRecord, Ledger

SUPPLIER_DOMAINS = [
    "indiamart.com", "amazon.in", "amazon.com", "vitalitymedical.com", "oxygenconcentratorstore.com",
    "drivemedical.com", "devilbisshealthcare.com", "philips.com", "respironics.com", "caireinc.com", "airsep.com",
    "ebay.com", "medicalsupplydepot.com", "1800wheelchair.com", "spinlife.com",
]
MANUAL_DOMAINS = ["frankshospitalworkshop.com", "manualslib.com", "manualzz.com", "scribd.com", "archive.org", "oxygenalliance.org", "medwrench.com"]


def _client():
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return None
    from tavily import TavilyClient

    return TavilyClient(api_key=key)


def _log(ledger: Ledger | None, trace_id: str | None, purpose: str, ms: int) -> None:
    if ledger:
        ledger.record(CallRecord(trace_id or str(uuid.uuid4()), "tool", "Tavily", "tavily/search", purpose, 0, 0, 0.0, ms))


def find_manual(model: str, manufacturer: str | None = None, *, ledger: Ledger | None = None, trace_id: str | None = None) -> dict[str, Any]:
    c = _client()
    if not c:
        return {"available": False, "reason": "TAVILY_API_KEY not set", "results": []}
    q = f'"{model}" {manufacturer or ""} oxygen concentrator service manual pdf'.strip()
    t0 = time.perf_counter()
    try:
        r = c.search(q, search_depth="basic", max_results=5, include_domains=MANUAL_DOMAINS)
        _log(ledger, trace_id, "tavily.find_manual", int((time.perf_counter() - t0) * 1000))
        return {"available": True, "query": q, "results": [{"title": x.get("title"), "url": x.get("url"), "snippet": (x.get("content") or "")[:200]} for x in r.get("results", [])]}
    except Exception as e:  # noqa: BLE001
        return {"available": False, "reason": type(e).__name__, "results": []}


def find_parts(part: str, model: str | None = None, *, ledger: Ledger | None = None, trace_id: str | None = None) -> dict[str, Any]:
    c = _client()
    if not c:
        return {"available": False, "reason": "TAVILY_API_KEY not set", "results": []}
    q = f'"{part}" {model or ""} price'.strip()
    t0 = time.perf_counter()
    try:
        r = c.search(q, search_depth="basic", max_results=5, include_domains=SUPPLIER_DOMAINS)
        _log(ledger, trace_id, "tavily.find_parts", int((time.perf_counter() - t0) * 1000))
        return {"available": True, "query": q, "results": [{"title": x.get("title"), "url": x.get("url"), "snippet": (x.get("content") or "")[:200]} for x in r.get("results", [])]}
    except Exception as e:  # noqa: BLE001
        return {"available": False, "reason": type(e).__name__, "results": []}

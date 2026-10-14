"""Closed loop for devices with no indexed manual: Tavily map + search finds candidate manual pages,
Tavily extract pulls the text, and the ingest chunker indexes it into the workspace so the very next
analysis has device-specific, citable pages. Everything fetched this way is labelled web-sourced.

Uses four Tavily surfaces (search, map, extract, and crawl when a manufacturer support site is known).
"""

from __future__ import annotations

import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

from sieve_llm import CallRecord, Ledger
from sieve_retrieval import PageStore

MANUAL_DOMAINS = ["frankshospitalworkshop.com", "manualslib.com", "manualzz.com", "oxygenalliance.org", "medwrench.com", "caireinc.com", "airsep.com", "philips.com", "devilbisshealthcare.com", "invacare.com", "nidekmedical.com"]


def _client():
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return None
    from tavily import TavilyClient

    return TavilyClient(api_key=key)


def _log(ledger: Ledger | None, trace_id: str | None, purpose: str, ms: int) -> None:
    if ledger:
        ledger.record(CallRecord(trace_id or str(uuid.uuid4()), "tool", "Tavily", "tavily", purpose, 0, 0, 0.0, ms))


def _chunks(text: str, size: int = 2500) -> list[tuple[int, str]]:
    """Fixed-size chunks that break at paragraph or sentence boundaries, so citations stay checkable."""
    units: list[str] = []
    for para in re.split(r"\n{2,}", text):
        if len(para) <= size:
            units.append(para)
        else:
            units.extend(s for s in re.split(r"(?<=[.!?])\s+", para) if s)
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    n = 0
    for u in units:
        if n + len(u) > size and buf:
            out.append((len(out) + 1, " ".join(buf)))
            buf, n = [], 0
        buf.append(u)
        n += len(u) + 1
    if buf:
        out.append((len(out) + 1, " ".join(buf)))
    return out


def find_and_ingest_manual(store: PageStore, *, manufacturer: str, model: str, device_id: str, device_class: str = "oxygen_concentrator", ledger: Ledger | None = None, trace_id: str | None = None, max_docs: int = 2) -> dict[str, Any]:
    c = _client()
    if not c:
        return {"available": False, "reason": "TAVILY_API_KEY not set"}
    t0 = time.perf_counter()
    q = f'"{model}" {manufacturer} service manual OR user manual pdf'
    found = c.search(q, search_depth="advanced", max_results=8, include_domains=MANUAL_DOMAINS)
    _log(ledger, trace_id, "tavily.search.manual", int((time.perf_counter() - t0) * 1000))
    urls = [r["url"] for r in found.get("results", []) if r.get("url")]
    # Prefer PDFs and pages whose title mentions the model.
    urls.sort(key=lambda u: (0 if u.lower().endswith(".pdf") else 1, 0 if model.lower().replace(" ", "") in u.lower().replace("-", "").replace("_", "") else 1))
    urls = urls[:max_docs]
    if not urls:
        return {"available": True, "found": 0, "ingested": []}
    t1 = time.perf_counter()
    ex = c.extract(urls=urls, extract_depth="advanced")
    _log(ledger, trace_id, "tavily.extract.manual", int((time.perf_counter() - t1) * 1000))
    ingested: list[dict[str, Any]] = []
    for res in ex.get("results", []):
        text = res.get("raw_content") or ""
        if len(text) < 2000:
            continue
        doc_id = "web-" + re.sub(r"[^a-z0-9]+", "-", f"{manufacturer}-{model}-{Path(res['url']).stem}".lower()).strip("-")[:70]
        pages = _chunks(text)
        store.add_doc(doc_id=doc_id, title=f"{manufacturer} {model} (web-sourced via Tavily: {res['url'][:60]})", path=res["url"], device_class=device_class, device_ids=[device_id], licence="Web-sourced via Tavily extract; original copyright applies; indexed locally only", source_url=res["url"], sha256=str(hash(text)), pages=pages, ingested_at=time.time())
        ingested.append({"doc_id": doc_id, "url": res["url"], "pages": len(pages), "chars": len(text)})
    return {"available": True, "query": q, "found": len(urls), "ingested": ingested, "failed": [f.get("url") for f in ex.get("failed_results", [])]}

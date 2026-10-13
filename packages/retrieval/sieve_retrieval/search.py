"""Device-scoped hybrid search with verbatim citation support.

Today: BM25 (FTS5) with optional vector fusion when a vectors table exists. The verifier in
sieve_core.citations uses PageStore.page_text to confirm every quoted span exists on the cited page.
"""

from __future__ import annotations

from dataclasses import dataclass

from .store import PageStore


@dataclass
class Hit:
    doc_id: str
    title: str
    page: int
    score: float
    text: str
    source_url: str
    licence: str


class Searcher:
    def __init__(self, store: PageStore):
        self.store = store

    def search(self, query: str, *, device_id: str | None = None, device_class: str | None = None, k: int = 8) -> list[Hit]:
        doc_ids = self.store.doc_ids_for(device_id, device_class) if (device_id or device_class) else None
        if device_id and not doc_ids:
            # Known device but no manual indexed: fall back to the class, then to everything.
            doc_ids = self.store.doc_ids_for(None, device_class) or None
        rows = self.store.lexical(query, doc_ids, k=max(k * 3, 24))
        hits: list[Hit] = []
        seen: set[tuple[str, int]] = set()
        for doc_id, page, score in rows:
            if (doc_id, page) in seen:
                continue
            seen.add((doc_id, page))
            meta = self.store.doc_meta(doc_id) or {}
            text = self.store.page_text(doc_id, page) or ""
            hits.append(Hit(doc_id, meta.get("title", doc_id), page, score, text, meta.get("source_url", ""), meta.get("licence", "")))
            if len(hits) >= k:
                break
        return hits

    def pack_context(self, hits: list[Hit], max_chars: int = 24_000) -> str:
        """Context block for the synthesiser: each page labelled so the model can cite doc and page exactly."""
        parts: list[str] = []
        used = 0
        for h in hits:
            block = f"<page doc_id=\"{h.doc_id}\" title=\"{h.title}\" page=\"{h.page}\">\n{h.text}\n</page>"
            if used + len(block) > max_chars:
                break
            parts.append(block)
            used += len(block)
        return "\n\n".join(parts)

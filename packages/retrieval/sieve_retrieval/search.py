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
        lex = self.store.lexical(query, doc_ids, k=max(k * 3, 24))
        vec = self._vector(query, doc_ids, k=max(k * 3, 24))
        rows = self._fuse(lex, vec) if vec else lex
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

    def _vector(self, query: str, doc_ids: list[str] | None, k: int) -> list[tuple[str, int, float]]:
        """Cosine search over Token Factory embeddings when the vectors table is populated; silent no-op otherwise."""
        import math
        import os

        key = os.environ.get("NEBIUS_API_KEY")
        if not key:
            return []
        try:
            from .embed import EMBED_MODEL, embed_texts, unpack

            if doc_ids:
                marks = ",".join("?" * len(doc_ids))
                rows = self.store.conn.execute(f"SELECT doc_id, page, dim, vec FROM vectors WHERE model=? AND doc_id IN ({marks})", (EMBED_MODEL, *doc_ids)).fetchall()
            else:
                rows = self.store.conn.execute("SELECT doc_id, page, dim, vec FROM vectors WHERE model=?", (EMBED_MODEL,)).fetchall()
            if not rows:
                return []
            q = embed_texts([query[:6000]], key)[0]
            qn = math.sqrt(sum(x * x for x in q)) or 1.0
            scored = []
            for doc_id, page, dim, blob in rows:
                v = unpack(blob, dim)
                dot = sum(a * b for a, b in zip(q, v, strict=True))
                vn = math.sqrt(sum(x * x for x in v)) or 1.0
                scored.append((doc_id, page, dot / (qn * vn)))
            scored.sort(key=lambda r: r[2], reverse=True)
            return scored[:k]
        except Exception:  # noqa: BLE001
            return []

    @staticmethod
    def _fuse(lex: list[tuple[str, int, float]], vec: list[tuple[str, int, float]], k_rrf: int = 60) -> list[tuple[str, int, float]]:
        """Reciprocal rank fusion of lexical and vector rankings."""
        score: dict[tuple[str, int], float] = {}
        for rank, (d, p, _) in enumerate(lex, start=1):
            score[(d, p)] = score.get((d, p), 0.0) + 1.0 / (k_rrf + rank)
        for rank, (d, p, _) in enumerate(vec, start=1):
            score[(d, p)] = score.get((d, p), 0.0) + 1.0 / (k_rrf + rank)
        return [(d, p, s) for (d, p), s in sorted(score.items(), key=lambda kv: kv[1], reverse=True)]

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

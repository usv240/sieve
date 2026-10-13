"""Page store: SQLite with FTS5 for lexical search, plus an optional vector table.

Why SQLite: single file, zero services, ships inside the offline bundle, FTS5 gives BM25 for free.
Vectors (Nemotron embed on the Serverless Job, or Token Factory embeddings) are added later as an
optional table; hybrid fusion happens in search.py.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Page:
    doc_id: str
    title: str
    page: int
    text: str
    device_class: str
    device_ids: list[str]
    licence: str
    source_url: str
    n_chars: int = 0


SCHEMA = """
CREATE TABLE IF NOT EXISTS docs (
  doc_id TEXT PRIMARY KEY, title TEXT, path TEXT, device_class TEXT, device_ids TEXT,
  licence TEXT, source_url TEXT, pages INTEGER, sha256 TEXT, ingested_at REAL);
CREATE TABLE IF NOT EXISTS pages (
  doc_id TEXT, page INTEGER, text TEXT, n_chars INTEGER, PRIMARY KEY (doc_id, page));
CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
  doc_id UNINDEXED, page UNINDEXED, text, tokenize='porter unicode61');
CREATE TABLE IF NOT EXISTS vectors (
  doc_id TEXT, page INTEGER, model TEXT, dim INTEGER, vec BLOB, PRIMARY KEY (doc_id, page, model));
"""


class PageStore:
    def __init__(self, path: str | Path = "data/index/sieve.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.executescript(SCHEMA)

    def has_doc(self, doc_id: str, sha256: str) -> bool:
        row = self.conn.execute("SELECT sha256 FROM docs WHERE doc_id=?", (doc_id,)).fetchone()
        return bool(row and row[0] == sha256)

    def add_doc(self, *, doc_id: str, title: str, path: str, device_class: str, device_ids: list[str],
                licence: str, source_url: str, sha256: str, pages: list[tuple[int, str]], ingested_at: float) -> None:
        c = self.conn
        c.execute("DELETE FROM pages WHERE doc_id=?", (doc_id,))
        c.execute("DELETE FROM pages_fts WHERE doc_id=?", (doc_id,))
        c.execute(
            "INSERT OR REPLACE INTO docs VALUES (?,?,?,?,?,?,?,?,?,?)",
            (doc_id, title, path, device_class, json.dumps(device_ids), licence, source_url, len(pages), sha256, ingested_at),
        )
        c.executemany("INSERT INTO pages VALUES (?,?,?,?)", [(doc_id, p, t, len(t)) for p, t in pages])
        c.executemany("INSERT INTO pages_fts VALUES (?,?,?)", [(doc_id, p, t) for p, t in pages])
        c.commit()

    def doc_ids_for(self, device_id: str | None, device_class: str | None) -> list[str]:
        rows = self.conn.execute("SELECT doc_id, device_class, device_ids FROM docs").fetchall()
        out = []
        for doc_id, dclass, dids in rows:
            ids = json.loads(dids or "[]")
            if device_id and device_id in ids or not device_id and device_class and dclass == device_class:
                out.append(doc_id)
        return out

    def page_text(self, doc_id: str, page: int) -> str | None:
        row = self.conn.execute("SELECT text FROM pages WHERE doc_id=? AND page=?", (doc_id, page)).fetchone()
        return row[0] if row else None

    def doc_meta(self, doc_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT doc_id,title,path,device_class,device_ids,licence,source_url,pages FROM docs WHERE doc_id=?", (doc_id,)
        ).fetchone()
        if not row:
            return None
        keys = ["doc_id", "title", "path", "device_class", "device_ids", "licence", "source_url", "pages"]
        d = dict(zip(keys, row))
        d["device_ids"] = json.loads(d["device_ids"] or "[]")
        return d

    def full_text(self, doc_id: str) -> list[tuple[int, str]]:
        return self.conn.execute("SELECT page, text FROM pages WHERE doc_id=? ORDER BY page", (doc_id,)).fetchall()

    def lexical(self, query: str, doc_ids: list[str] | None, k: int = 30) -> list[tuple[str, int, float]]:
        """BM25 via FTS5. Returns (doc_id, page, score) with higher = better."""
        q = _fts_query(query)
        if not q:
            return []
        if doc_ids:
            marks = ",".join("?" * len(doc_ids))
            sql = f"SELECT doc_id, page, bm25(pages_fts) FROM pages_fts WHERE pages_fts MATCH ? AND doc_id IN ({marks}) ORDER BY bm25(pages_fts) LIMIT ?"
            rows = self.conn.execute(sql, (q, *doc_ids, k)).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT doc_id, page, bm25(pages_fts) FROM pages_fts WHERE pages_fts MATCH ? ORDER BY bm25(pages_fts) LIMIT ?",
                (q, k),
            ).fetchall()
        return [(d, p, -s) for d, p, s in rows]

    def stats(self) -> dict:
        docs = self.conn.execute("SELECT COUNT(*), COALESCE(SUM(pages),0) FROM docs").fetchone()
        by_class = self.conn.execute("SELECT device_class, COUNT(*), SUM(pages) FROM docs GROUP BY device_class").fetchall()
        return {"docs": docs[0], "pages": docs[1], "by_class": {r[0]: {"docs": r[1], "pages": r[2]} for r in by_class}}


def _fts_query(query: str) -> str:
    """Turn free text into an FTS5 OR-query of safe tokens so punctuation never breaks the parser."""
    import re

    toks = [t for t in re.findall(r"[A-Za-z0-9]+", query) if len(t) > 1]
    toks = toks[:40]
    return " OR ".join(f'"{t}"' for t in toks)

"""Vector embeddings via Token Factory (Qwen/Qwen3-Embedding-8B) for hybrid retrieval.

`python -m sieve_retrieval.embed --device-class oxygen_concentrator` embeds every page of that class and stores
float32 vectors in the `vectors` table. Search fuses BM25 and cosine ranks with reciprocal rank fusion.
"""

from __future__ import annotations

import os
import struct
import time
from pathlib import Path

import httpx
import typer

from .store import PageStore

app = typer.Typer(add_completion=False)
EMBED_MODEL = "Qwen/Qwen3-Embedding-8B"
BASE = "https://api.tokenfactory.nebius.com/v1/"


def _load_env() -> None:
    root = Path(__file__).resolve().parents[3]
    for env in (root / ".env", root.parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def embed_texts(texts: list[str], key: str) -> list[list[float]]:
    r = httpx.post(f"{BASE}embeddings", headers={"Authorization": f"Bearer {key}"}, json={"model": EMBED_MODEL, "input": texts}, timeout=120)
    r.raise_for_status()
    data = sorted(r.json()["data"], key=lambda d: d["index"])
    return [d["embedding"] for d in data]


def pack(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def unpack(blob: bytes, dim: int) -> list[float]:
    return list(struct.unpack(f"{dim}f", blob))


@app.command()
def run(index: Path = typer.Option(Path("data/index/sieve.db")), device_class: str = typer.Option("oxygen_concentrator"), batch: int = typer.Option(16), max_chars: int = typer.Option(6000)) -> None:
    _load_env()
    key = os.environ.get("NEBIUS_API_KEY")
    if not key:
        raise SystemExit("NEBIUS_API_KEY not set")
    store = PageStore(index)
    rows = store.conn.execute(
        "SELECT p.doc_id, p.page, p.text FROM pages p JOIN docs d ON d.doc_id = p.doc_id WHERE d.device_class=? AND p.n_chars >= 40 "
        "AND NOT EXISTS (SELECT 1 FROM vectors v WHERE v.doc_id=p.doc_id AND v.page=p.page AND v.model=?)",
        (device_class, EMBED_MODEL),
    ).fetchall()
    typer.echo(f"{len(rows)} pages to embed")
    t0 = time.time()
    done = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i : i + batch]
        vecs = embed_texts([t[:max_chars] for _, _, t in chunk], key)
        store.conn.executemany(
            "INSERT OR REPLACE INTO vectors VALUES (?,?,?,?,?)",
            [(d, p, EMBED_MODEL, len(v), pack(v)) for (d, p, _), v in zip(chunk, vecs, strict=True)],
        )
        store.conn.commit()
        done += len(chunk)
        if done % (batch * 10) == 0:
            typer.echo(f"  {done}/{len(rows)} in {time.time() - t0:.0f}s")
    typer.echo(f"embedded {done} pages in {time.time() - t0:.0f}s with {EMBED_MODEL} via Nebius Token Factory")


if __name__ == "__main__":
    app()

"""Ingest PDFs listed in data/manifest.yaml into the page store.

Runs anywhere: laptop, or as a Nebius Serverless Job (see infra/job-ingest). No API key required for the
lexical index. Figure descriptions and vector embeddings are optional enrichment steps added by the Job.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

import fitz  # PyMuPDF
import typer
import yaml
from rich import print

from .store import PageStore

app = typer.Typer(add_completion=False)


def _doc_id(path: Path) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    return stem[:80]


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_pages(path: Path) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            pages.append((i, text))
    return pages


def _guess_device_ids(title: str, registry: dict) -> list[str]:
    """Map a document title to device ids using the alias lists in devices.yaml."""
    t = title.lower()
    ids = []
    for dev in registry.get("devices", []):
        for alias in dev.get("doc_title_aliases", []) + dev.get("model_aliases", []):
            if alias.lower() in t:
                ids.append(dev["id"])
                break
    return sorted(set(ids))


@app.command()
def run(
    manifest: Path = typer.Option(Path("data/manifest.yaml")),
    out: Path = typer.Option(Path("data/index")),
    devices: Path = typer.Option(Path("packages/core/sieve_core/data/devices.yaml")),
    only_class: str | None = typer.Option(None, help="Ingest only this device_class"),
) -> None:
    man = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    registry = yaml.safe_load(devices.read_text(encoding="utf-8")) if devices.exists() else {}
    store = PageStore(out / "sieve.db")
    report = {"started": time.time(), "docs": 0, "pages": 0, "skipped": 0, "empty_text_pages": 0, "errors": []}
    for src in man["sources"]:
        local_dir = src.get("local_dir")
        if not local_dir:
            continue
        if only_class and src.get("device_class") != only_class:
            continue
        for pdf in sorted(Path(local_dir).glob("*.pdf")):
            try:
                sha = _sha(pdf)
                doc_id = _doc_id(pdf)
                if store.has_doc(doc_id, sha):
                    report["skipped"] += 1
                    continue
                pages = _extract_pages(pdf)
                empties = sum(1 for _, t in pages if len(t) < 40)
                report["empty_text_pages"] += empties
                store.add_doc(
                    doc_id=doc_id,
                    title=pdf.stem,
                    path=str(pdf),
                    device_class=src.get("device_class", "generic"),
                    device_ids=_guess_device_ids(pdf.stem, registry),
                    licence=src.get("licence", ""),
                    source_url=src.get("url", ""),
                    sha256=sha,
                    pages=pages,
                    ingested_at=time.time(),
                )
                report["docs"] += 1
                report["pages"] += len(pages)
                print(f"[green]indexed[/green] {pdf.name} ({len(pages)} pages, {empties} low-text)")
            except Exception as e:  # noqa: BLE001
                report["errors"].append({"file": pdf.name, "error": str(e)})
                print(f"[red]error[/red] {pdf.name}: {e}")
    report["finished"] = time.time()
    report["seconds"] = round(report["finished"] - report["started"], 1)
    report["stats"] = store.stats()
    (out / "ingest_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(report["stats"], f"in {report['seconds']}s")


if __name__ == "__main__":
    app()

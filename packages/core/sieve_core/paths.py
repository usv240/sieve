"""Relocatable data directory.

Locally everything lives under <repo>/data. On Vercel functions the bundle is read-only and only /tmp is
writable, so on first use the bundled data directory is copied to /tmp and used from there (ledger,
records, API keys and uploads then persist for the life of the instance).
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    override = os.environ.get("SIEVE_DATA_DIR")
    if override:
        return Path(override)
    bundled = ROOT / "data"
    if os.environ.get("VERCEL") or not os.access(bundled, os.W_OK):
        tmp = Path("/tmp/sieve-data")
        if not (tmp / "index" / "sieve.db").exists():
            tmp.mkdir(parents=True, exist_ok=True)
            for sub in ("index", "external", "samples"):
                if (bundled / sub).exists():
                    shutil.copytree(bundled / sub, tmp / sub, dirs_exist_ok=True)
            for f in ("records.jsonl",):
                if (bundled / f).exists():
                    shutil.copy(bundled / f, tmp / f)
        return tmp
    return bundled

"""Vercel Python function entry: serves the Sieve FastAPI app."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for sub in ("apps/api", "packages/core", "packages/llm", "packages/retrieval", "packages/rules", "packages/vision", "packages/eval"):
    sys.path.insert(0, str(ROOT / sub))

from sieve_api.main import app  # noqa: F401

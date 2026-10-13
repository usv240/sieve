"""Deterministic citation verifier: a quote must appear verbatim (whitespace-normalised) on the cited page."""

from __future__ import annotations

import re
from dataclasses import dataclass


def _norm(s: str) -> str:
    s = s.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


@dataclass
class Verification:
    ok: bool
    reason: str


def verify_quote(quote: str, page_text: str | None, min_len: int = 12) -> Verification:
    if not page_text:
        return Verification(False, "cited page not found in index")
    q = _norm(quote)
    if len(q) < min_len:
        return Verification(False, "quote too short to verify")
    if q in _norm(page_text):
        return Verification(True, "verbatim match")
    # Tolerate OCR hyphenation and line-break artefacts: compare with hyphens and spaces removed.
    if q.replace("-", "").replace(" ", "") in _norm(page_text).replace("-", "").replace(" ", ""):
        return Verification(True, "match after hyphen/space normalisation")
    return Verification(False, "quote not found on cited page")

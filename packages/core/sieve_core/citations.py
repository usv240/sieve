"""Deterministic citation verifier.

A quote passes if it appears on the cited page. PDF text extraction breaks lines, drops table borders,
and turns dashes and ligatures into odd characters, so matching is done in three tiers and the tier is
reported so the eval can show strict versus normalised matches:
  1. verbatim: whitespace-normalised substring
  2. normalised: substring after removing every non-alphanumeric character
  3. fuzzy: rapidfuzz partial_ratio >= 94 on the alphanumeric-only strings (catches a dropped table cell)
Anything below that is a failure and the step is replaced by the page itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz

_LIG = {"ﬁ": "fi", "ﬂ": "fl", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " ", " ": " "}


def _norm(s: str) -> str:
    for a, b in _LIG.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def _alnum(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", _norm(s))


@dataclass
class Verification:
    ok: bool
    reason: str
    tier: str = "none"  # verbatim | normalised | fuzzy | none


def verify_quote(quote: str, page_text: str | None, min_len: int = 12, fuzzy_threshold: float = 94.0) -> Verification:
    if not page_text:
        return Verification(False, "cited page not found in index")
    q = _norm(quote)
    if len(q) < min_len:
        return Verification(False, "quote too short to verify")
    p = _norm(page_text)
    if q in p:
        return Verification(True, "verbatim match", "verbatim")
    qa, pa = _alnum(quote), _alnum(page_text)
    if len(qa) >= 10 and qa in pa:
        return Verification(True, "match after punctuation and whitespace normalisation", "normalised")
    if len(qa) >= 20:
        score = fuzz.partial_ratio(qa, pa)
        if score >= fuzzy_threshold:
            return Verification(True, f"fuzzy match {score:.0f}", "fuzzy")
    return Verification(False, "quote not found on cited page")

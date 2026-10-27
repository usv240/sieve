"""Cite by pointing, not by copying.

Retrieved pages are split into numbered sentences ([S1], [S2], ...). The model cites a sentence id; code looks up
the id and copies the exact source text. A citation can then never misquote its page: it either resolves to a real
sentence on a real page or it is rejected. Whether that sentence supports the step is a separate question,
answered by the auditor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Split at sentence ends, blank lines, bullets and numbered list items; a single PDF line break is not a boundary.
_SPLIT = re.compile(
    r"(?<=[.!?;])\s+(?=[A-Z0-9(\"'•])"  # sentence end
    r"|(?<=[a-z][.!?])\d{1,3}\s+(?=[A-Z])"  # sentence end followed by a footnote number: "toxicity.4 Paraquat"
    r"|\s*\n\s*\n\s*|\s*(?=•)|\n(?=\s*(?:\d{1,2}[.)]|[-*])\s)"
)
_SID = re.compile(r"\bS?(\d{1,4})\b")


@dataclass
class Sentence:
    sid: str
    doc: str
    page: int
    text: str


def split_sentences(text: str, min_len: int = 30, max_len: int = 360) -> list[str]:
    raw = [re.sub(r"\s+", " ", s).strip() for s in _SPLIT.split(text or "")]
    out: list[str] = []
    buf = ""
    for s in raw:
        if not s:
            continue
        buf = f"{buf} {s}".strip() if buf else s
        if len(buf) >= min_len:
            while len(buf) > max_len:
                # cut at the last clause or word boundary before max_len; never inside a word
                cut = max(buf.rfind("; ", 0, max_len), buf.rfind(", ", 0, max_len))
                cut = cut + 1 if cut > min_len else buf.rfind(" ", 0, max_len)
                if cut <= min_len:
                    cut = max_len
                out.append(buf[:cut].strip())
                buf = buf[cut:].strip()
            if buf:
                out.append(buf)
            buf = ""
    if buf:
        if out and len(buf) < min_len:
            out[-1] = f"{out[-1]} {buf}"
        else:
            out.append(buf)
    return out


class SentenceIndex:
    """Numbers the sentences of a set of pages and resolves ids back to exact source text."""

    def __init__(self) -> None:
        self.by_id: dict[str, Sentence] = {}

    def add_page(self, doc: str, page: int, text: str) -> list[Sentence]:
        added = []
        for s in split_sentences(text):
            sid = f"S{len(self.by_id) + 1}"
            sent = Sentence(sid, doc, page, s)
            self.by_id[sid] = sent
            added.append(sent)
        return added

    def resolve_many(self, sids: str | None, limit: int = 3) -> list[Sentence]:
        """One id or up to `limit` ids from the same page ("S12, S13"). Ids on other pages are ignored."""
        out: list[Sentence] = []
        for m in _SID.finditer(str(sids or "").upper()):
            s = self.by_id.get(f"S{m.group(1)}")
            if s and (not out or (s.doc, s.page) == (out[0].doc, out[0].page)) and s not in out:
                out.append(s)
            if len(out) >= limit:
                break
        return out

    def resolve(self, sid: str | None) -> Sentence | None:
        if not sid:
            return None
        m = _SID.search(str(sid).strip().upper().replace("[", "").replace("]", ""))
        return self.by_id.get(f"S{m.group(1)}") if m else None


def pack_numbered(hits: list, max_chars: int = 24_000) -> tuple[str, SentenceIndex]:
    """Pages as numbered sentences. Each hit needs .doc_id, .title, .page and .text."""
    idx = SentenceIndex()
    parts: list[str] = []
    used = 0
    for h in hits:
        sents = split_sentences(h.text)
        body_len = sum(len(s) + 8 for s in sents)
        if used + body_len + 120 > max_chars:
            break
        added = idx.add_page(h.doc_id, h.page, h.text)
        body = "\n".join(f"[{s.sid}] {s.text}" for s in added)
        parts.append(f"<page doc_id=\"{h.doc_id}\" title=\"{h.title}\" page=\"{h.page}\">\n{body}\n</page>")
        used += body_len + 120
    return "\n\n".join(parts), idx

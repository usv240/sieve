"""Recorded results for the sample presets, served only when a live model call fails.

Judging runs for two weeks. If Token Factory is rate limited or credits run out, a judge who clicks a sample still
sees a real result, recorded from the live pipeline and clearly marked as a replay. Requests that do not match a
preset get an honest error instead of a recording. Recordings are refreshed with scripts/record_replays.mjs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _norm(s: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


class ReplayBook:
    def __init__(self, folder: Path, signature) -> None:
        self.signature = signature
        self.by_sig: dict[str, dict[str, Any]] = {}
        for f in sorted(folder.glob("*.json")) if folder.exists() else []:
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001 - one corrupt recording never disables the others
                print(f"replay: skipped {f.name}: {type(e).__name__}")
                continue
            if "request" in rec and "response" in rec:
                self.by_sig[signature(rec["request"])] = rec

    def find(self, request: dict[str, Any]) -> dict[str, Any] | None:
        return self.by_sig.get(self.signature(request))

    def serve(self, request: dict[str, Any], reason: str) -> dict[str, Any] | None:
        rec = self.find(request)
        if not rec:
            return None
        out = dict(rec["response"])
        out["mode"] = "replay"
        out["replay"] = {"sample_id": rec.get("sample_id"), "recorded_at": rec.get("recorded_at"), "reason": reason,
                         "note": "A live model call failed, so this is the result the same request produced when it was recorded from the live pipeline."}
        return out


def sieve_signature(req: dict[str, Any]) -> str:
    return "|".join([_norm(req.get("device_id")), ",".join(sorted(_norm(i) for i in req.get("indicator_ids") or [])), _norm(req.get("free_text"))[:80]])


def antidote_signature(req: dict[str, Any]) -> str:
    label = req.get("label") or {}
    ais = label.get("active_ingredients") or []
    first = ais[0].get("name") if ais and isinstance(ais[0], dict) else (ais[0] if ais else "")
    return "|".join([_norm(first), _norm(label.get("product_name"))])

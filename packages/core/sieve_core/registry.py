from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from rapidfuzz import fuzz

DATA = Path(__file__).parent / "data"


@dataclass
class Match:
    device_id: str
    confidence: float
    reason: str


class Registry:
    def __init__(self, devices_path: Path = DATA / "devices.yaml", faults_path: Path = DATA / "faults.yaml", intake_path: Path = DATA / "intake.yaml"):
        self.devices = yaml.safe_load(devices_path.read_text(encoding="utf-8"))["devices"]
        self.faults = {f["id"]: f for f in yaml.safe_load(faults_path.read_text(encoding="utf-8"))["faults"]}
        self.questions = yaml.safe_load(intake_path.read_text(encoding="utf-8"))["questions"]
        self.by_id = {d["id"]: d for d in self.devices}

    def get(self, device_id: str) -> dict | None:
        return self.by_id.get(device_id)

    def match(self, *, manufacturer: str | None, model: str | None, ref: str | None, visible_text: list[str] | None = None) -> list[Match]:
        """Deterministic matcher: exact alias on model or REF first, then fuzzy on manufacturer + model + visible text."""
        hay = " ".join(x for x in [manufacturer or "", model or "", ref or "", *(visible_text or [])] if x).lower()
        results: list[Match] = []
        for d in self.devices:
            score = 0.0
            reason = []
            for alias in d.get("model_aliases", []):
                a = alias.lower()
                if re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", hay):
                    score = max(score, 0.95 if len(a) >= 4 else 0.75)
                    reason.append(f"alias:{alias}")
                    break
            for pat in d.get("nameplate_patterns", []):
                if re.search(pat, hay):
                    score = max(score, score + 0.1 if score else 0.5)
                    reason.append(f"pattern:{pat}")
            if manufacturer:
                sim = fuzz.partial_ratio(manufacturer.lower(), d["manufacturer"].lower()) / 100
                if sim > 0.8:
                    score = max(score, score + 0.05 if score else 0.35)
                    reason.append(f"manufacturer~{sim:.2f}")
            if model:
                sim = fuzz.token_set_ratio(model.lower(), d["model"].lower()) / 100
                if sim > 0.7:
                    score = max(score, score + 0.05 if score else 0.4 * sim)
                    reason.append(f"model~{sim:.2f}")
            if score > 0:
                results.append(Match(d["id"], round(min(score, 0.99), 2), ", ".join(reason)))
        results.sort(key=lambda m: m.confidence, reverse=True)
        return results[:3]

    def indicators(self, device_id: str) -> list[dict]:
        d = self.get(device_id) or {}
        return d.get("indicators", [])

    def pick_questions(self, device_id: str | None, indicator_ids: list[str], max_q: int = 3) -> list[dict]:
        """Deterministic default selection (the fast model may re-rank, never invent)."""
        d = self.get(device_id) if device_id else None
        wanted_faults: list[str] = list(d.get("common_faults", [])) if d else [f for f in self.faults]
        by_id = {q["id"]: q for q in self.questions}
        always = [i for i in ("in_use", "heat_smoke") if i in by_id]
        chosen: list[dict] = [by_id[i] for i in always]
        for q in self.questions:
            if q["id"] in always:
                continue
            if any(f in wanted_faults for f in q.get("relevant_faults", [])):
                chosen.append(q)
            if len(chosen) >= max_q:
                break
        return chosen[:max_q]

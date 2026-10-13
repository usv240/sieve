from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

Action = Literal["block", "rewrite", "escalate", "annotate"]


@dataclass(frozen=True)
class Rule:
    id: str
    action: Action
    message: str
    patterns: tuple[re.Pattern[str], ...]
    stage: Literal["input", "output", "both"] = "both"
    rewrite_to: str | None = None
    citation: str | None = None
    severity: Literal["stop", "caution", "info"] = "stop"


@dataclass
class RuleHit:
    rule_id: str
    action: Action
    severity: str
    message: str
    citation: str | None
    matched: str
    stage: str
    rewrite_to: str | None = None


@dataclass
class RulesEngine:
    rules: list[Rule]
    version: str = "0"
    hits_log: list[RuleHit] = field(default_factory=list)

    @staticmethod
    def segments(text: str) -> list[str]:
        """Split into sentences so a rule sees one instruction at a time."""
        parts = re.split(r"(?<=[.!?])\s+|\n+", text)
        return [s.strip() for s in parts if s and s.strip()]

    def check(self, text: str, stage: Literal["input", "output"]) -> list[RuleHit]:
        hits: list[RuleHit] = []
        for r in self.rules:
            if r.stage not in (stage, "both"):
                continue
            fired = False
            for seg in self.segments(text):
                for p in r.patterns:
                    m = p.search(seg)
                    if m:
                        hit = RuleHit(r.id, r.action, r.severity, r.message, r.citation, seg, stage, r.rewrite_to)
                        hits.append(hit)
                        self.hits_log.append(hit)
                        fired = True
                        break
                if fired:
                    break
        return hits

    def blocks(self, hits: list[RuleHit]) -> bool:
        return any(h.action == "block" for h in hits)

    def apply_rewrites(self, text: str, hits: list[RuleHit]) -> str:
        """A rewrite prepends the safe precondition to the offending sentence; it never deletes content."""
        for h in hits:
            if h.action == "rewrite" and h.rewrite_to and h.matched in text:
                text = text.replace(h.matched, f"{h.rewrite_to} {h.matched}", 1)
        return text


def load_rules(path: str | Path) -> RulesEngine:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rules: list[Rule] = []
    for item in doc["rules"]:
        pats = tuple(re.compile(p, re.IGNORECASE) for p in item["patterns"])
        rules.append(
            Rule(
                id=item["id"],
                action=item["action"],
                message=item["message"],
                patterns=pats,
                stage=item.get("stage", "both"),
                rewrite_to=item.get("rewrite_to"),
                citation=item.get("citation"),
                severity=item.get("severity", "stop"),
            )
        )
    return RulesEngine(rules=rules, version=str(doc.get("version", "0")))

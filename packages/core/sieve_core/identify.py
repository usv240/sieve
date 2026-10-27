"""Identify a device from two independent photo reads.

Vision models can invent plausible small print: on a real DeVilbiss 1025DS rating label, Nemotron 3.5 Super VL read
"REF 525DS" and a made-up serial number. A wrong match opens the wrong service manual, so Sieve selects a device on its
own only when two different models' reads lead the registry to the same device. Otherwise the candidates are offered
for the technician to pick, and the disagreement is shown.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .registry import Match, Registry

AUTO = 0.6
OFFERED = 0.55


def _match(reg: Registry, fields: Any) -> list[Match]:
    if fields is None:
        return []
    return reg.match(manufacturer=fields.manufacturer, model=fields.model, ref=fields.ref, visible_text=fields.visible_text or [])


def cross_checked_match(reg: Registry, first: Any, second: Any | None) -> tuple[list[Match], dict[str, Any]]:
    """first and second are NameplateFields (second may be None). Returns matches and a short report."""
    m1, m2 = _match(reg, first), _match(reg, second)
    top1 = m1[0] if m1 else None
    top2 = m2[0] if m2 else None
    report: dict[str, Any] = {"first": top1.device_id if top1 else None, "second": top2.device_id if top2 else None, "second_read": second is not None}
    if not top1 or top1.confidence < AUTO:
        report["agreed"] = None
        return m1, report
    agreed = top2 is not None and top2.device_id == top1.device_id and top2.confidence >= AUTO
    report["agreed"] = agreed
    if agreed:
        return m1, report
    # Disagreement or no second read: never auto-select. Offer the candidates from both reads for the technician to pick.
    seen: dict[str, Match] = {}
    for m in [*m1[:3], *m2[:3]]:
        if m.device_id not in seen:
            seen[m.device_id] = replace(m, confidence=min(m.confidence, OFFERED), reason=f"{m.reason}; two photo reads disagreed, confirm the model")
    return list(seen.values())[:3], report

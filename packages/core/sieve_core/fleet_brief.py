"""Fleet brief: Nemotron 3.5 Lightning reads the ENTIRE evidence base in one call and writes the weekly brief
for the engineer who covers forty facilities.

Non-obvious use of a 1M-context model: instead of retrieval, we hand it every work order in the fleet, all 647
openFDA malfunction reports and all 34 recalls for this device class, and ask for a one-page brief: what is
failing this month, which parts to stock, which recalls touch units we own, which facilities have the longest
downtime. Lightning costs $0.06 per million input tokens, so the whole fleet fits in one cheap call.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from sieve_llm import Tier, TokenFactoryClient, call_structured

ROOT = Path(__file__).resolve().parents[3]


class BriefItem(BaseModel):
    title: str
    detail: str = Field(description="Two plain sentences. Cite work order ids or MDR report keys inline.")
    evidence_ids: list[str] = []


class FleetBrief(BaseModel):
    """One-page weekly brief for the district biomedical engineer."""

    headline: str = Field(description="One sentence: the single most important thing this week.")
    failing_now: list[BriefItem] = Field(description="Top fault patterns across the fleet this period, with counts.")
    parts_to_stock: list[BriefItem] = Field(description="Parts implied by open work orders and recurring faults, with quantities.")
    recalls_affecting_us: list[BriefItem] = Field(description="Recalls whose models match units in the fleet. Empty if none.")
    longest_downtime: list[BriefItem] = Field(description="Facilities or units down longest, with hours.")
    what_fda_reports_add: list[BriefItem] = Field(description="Patterns in public malfunction reports for the brands we own that we have not yet seen locally.")
    confidence_note: str = Field(description="One sentence on how complete the data is (number of work orders, date range).")


SYSTEM = """You are the district biomedical engineer's analyst. You receive the complete fleet work-order log, the public FDA malfunction reports and recalls for the device class. Write a brief that a busy engineer can act on in five minutes. Count things. Cite work order ids and MDR report keys. Never invent a part number; if the manual's part is unknown say 'part per manual'. Return the FleetBrief tool call."""


def build_fleet_brief(client: TokenFactoryClient, *, device_class: str = "oxygen_concentrator", trace_id: str | None = None) -> dict[str, Any]:
    from .paths import data_dir

    records_path = data_dir() / "records.jsonl"
    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line.strip()] if records_path.exists() else []
    maude = json.loads((data_dir() / "external/maude_oxygen_concentrator_malfunctions.json").read_text(encoding="utf-8"))["records"]
    recalls = json.loads((data_dir() / "external/recalls_oxygen_concentrator.json").read_text(encoding="utf-8"))["records"]
    maude_slim = [{"mdr": m["mdr_report_key"], "brand": m.get("brand_name"), "manufacturer": m.get("manufacturer"), "problems": m.get("product_problems"), "event": (m.get("event_description") or "")[:400], "finding": (m.get("manufacturer_narrative") or "")[:300]} for m in maude]
    recalls_slim = [{"recall": r.get("product_res_number") or r.get("res_event_number"), "firm": r.get("recalling_firm"), "product": (r.get("product_description") or "")[:200], "reason": (r.get("reason_for_recall") or "")[:300], "date": r.get("event_date_initiated")} for r in recalls]
    payload = {"fleet_work_orders": records, "fda_malfunction_reports": maude_slim, "fda_recalls": recalls_slim}
    text = json.dumps(payload, ensure_ascii=False)
    approx_tokens = len(text) // 3
    brief = call_structured(
        client,
        Tier.FAST,
        FleetBrief,
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"DEVICE CLASS: {device_class}\n\nDATA (JSON):\n{text}\n\nWrite the FleetBrief."}],
        purpose="fleet.brief",
        trace_id=trace_id,
        max_tokens=3000,
        context_tokens=approx_tokens,
    )
    import datetime as _dt

    ts = [r.get("created_at") for r in records if r.get("created_at")]
    span = f"{_dt.datetime.fromtimestamp(min(ts)).date()} to {_dt.datetime.fromtimestamp(max(ts)).date()}" if ts else "no dates"
    brief.confidence_note = f"Computed from {len(records)} fleet work orders ({span}), {len(maude_slim)} public FDA malfunction reports and {len(recalls_slim)} recalls for this device class."
    return {"brief": brief.model_dump(), "inputs": {"work_orders": len(records), "fda_reports": len(maude_slim), "recalls": len(recalls_slim), "approx_input_tokens": approx_tokens}}

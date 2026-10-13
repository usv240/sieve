"""The Sieve agent: identify, intake, retrieve, synthesise, gate, audit, enrich.

Design rule: models read and draft; the rules engine, the citation verifier and the registry decide
what is allowed to reach the technician.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sieve_llm import Tier, TokenFactoryClient, call_structured
from sieve_retrieval import Hit, PageStore, Searcher
from sieve_rules import RuleHit, RulesEngine, load_rules

from .citations import verify_quote
from .registry import Registry
from .schemas import AuditReport, FaultTree, Step

ROOT = Path(__file__).resolve().parents[3]
RULES_PATH = ROOT / "packages/rules/sieve_rules/sieve.yaml"


@dataclass
class AnalyzeResult:
    trace_id: str
    device_id: str | None
    device_label: str
    tree: FaultTree | None
    audit: AuditReport | None
    rule_hits: list[RuleHit]
    citation_report: dict[str, Any]
    retrieved: list[dict[str, Any]]
    recalls: list[dict[str, Any]] = field(default_factory=list)
    maude_summary: dict[str, Any] = field(default_factory=dict)
    tavily: dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    notes: list[str] = field(default_factory=list)


SYNTH_SYSTEM = """You are a senior biomedical equipment engineer writing a troubleshooting tree for a technician in a district hospital.
Rules you must follow:
1. Use ONLY the manual pages provided. Every hypothesis and every step must carry a cite with the exact doc_id, page number and a VERBATIM quote copied from that page. Never paraphrase inside quote.
2. Steps are concrete, one action each, ordered from cheapest and safest to most invasive. Start with checks that need no tools.
3. Mark any step that opens the cabinet, touches mains, capacitors, or the oxygen path as safety_class "caution"; mark anything the manual says only qualified personnel may do as "stop".
4. If the pages do not support a step, do not write it. Prefer fewer, well-cited steps.
5. Write the summary in two plain sentences a nurse could understand."""

AUDIT_SYSTEM = """You are an independent auditor. You receive the complete service manual text and a proposed troubleshooting tree.
For each step decide: approve (the cited quote supports the action and nothing in the manual contradicts it), repair (the action is right but wording or precondition must change; give repaired_action), or reject (unsupported or contradicted). Be strict about safety preconditions (switch off and unplug before opening; patient on backup supply). Return the tool call."""


class SievePipeline:
    def __init__(self, client: TokenFactoryClient | None, store: PageStore, registry: Registry | None = None, rules: RulesEngine | None = None):
        self.client = client
        self.store = store
        self.search = Searcher(store)
        self.registry = registry or Registry()
        self.rules = rules or load_rules(RULES_PATH)
        self._maude = None
        self._recalls = None

    # ---------- identify ----------
    def identify(self, *, manufacturer: str | None, model: str | None, ref: str | None, visible_text: list[str] | None):
        return self.registry.match(manufacturer=manufacturer, model=model, ref=ref, visible_text=visible_text)

    # ---------- analyze ----------
    def analyze(
        self,
        *,
        device_id: str | None,
        indicator_ids: list[str],
        answers: dict[str, str],
        free_text: str = "",
        trace_id: str | None = None,
        audit: bool = True,
    ) -> AnalyzeResult:
        trace_id = trace_id or str(uuid.uuid4())
        notes: list[str] = []
        dev = self.registry.get(device_id) if device_id else None
        label = f"{dev['manufacturer']} {dev['model']}" if dev else "Unknown device"
        device_class = dev["device_class"] if dev else "oxygen_concentrator"

        # input gate
        in_hits = self.rules.check(free_text, "input") if free_text else []
        if self.rules.blocks(in_hits):
            return AnalyzeResult(trace_id, device_id, label, None, None, in_hits, {}, [], blocked=True, notes=["blocked at input gate"])

        # build query from registry meanings + answers
        inds = [i for i in self.registry.indicators(device_id) if i["id"] in indicator_ids] if device_id else []
        meanings = [i["meaning"] for i in inds]
        states = [i["state"] for i in inds]
        q_parts = states + meanings + [f"{k}: {v}" for k, v in answers.items()] + ([free_text] if free_text else [])
        query = " ".join(q_parts) or "troubleshooting alarms indicators low oxygen purity"
        hits = self.search.search(query, device_id=device_id, device_class=device_class, k=8)
        retrieved = [{"doc": h.doc_id, "title": h.title, "page": h.page, "score": round(h.score, 2), "source_url": h.source_url} for h in hits]
        if not hits:
            notes.append("no manual pages retrieved; generic flowchart only")
        if not self.client:
            res = AnalyzeResult(trace_id, device_id, label, None, None, in_hits, {}, retrieved, notes=notes + ["no model client (replay or offline-manual mode)"])
            res.recalls, res.maude_summary = self.enrich_fda(dev)
            return res

        # synthesise
        context = self.search.pack_context(hits)
        user = (
            f"Device: {label} (device_id={device_id}).\n"
            f"Observed indicators: {'; '.join(meanings) or 'none recorded'}.\n"
            f"Technician answers: {json.dumps(answers)}.\n"
            f"Free text: {free_text or 'none'}.\n\nManual pages:\n{context}\n\nProduce the FaultTree tool call."
        )
        tree = call_structured(
            self.client, Tier.MID, FaultTree,
            [{"role": "system", "content": SYNTH_SYSTEM}, {"role": "user", "content": user}],
            purpose="synthesise.fault_tree", trace_id=trace_id, max_tokens=3000,
        )
        tree.device_id = device_id or tree.device_id

        # citation verification (deterministic)
        cit = self._verify_tree(tree)

        # output gate
        out_text = "\n".join(f"{s.action}. {s.expected}." for s in tree.steps)
        out_hits = self.rules.check(out_text, "output")
        tree = self._apply_rules(tree, out_hits)

        # audit with the whole manual in context
        audit_report = None
        if audit and dev and dev.get("manuals"):
            audit_report = self._audit(tree, dev["manuals"][0], trace_id)
            tree = self._apply_audit(tree, audit_report)

        res = AnalyzeResult(trace_id, device_id, label, tree, audit_report, in_hits + out_hits, cit, retrieved, notes=notes)
        res.recalls, res.maude_summary = self.enrich_fda(dev)
        return res

    # ---------- helpers ----------
    def _verify_tree(self, tree: FaultTree) -> dict[str, Any]:
        total, ok, failures = 0, 0, []
        for item in [*tree.hypotheses, *tree.steps, *[p for p in tree.parts_candidates if p.cite]]:
            c = item.cite
            total += 1
            v = verify_quote(c.quote, self.store.page_text(c.doc, c.page))
            if v.ok:
                ok += 1
            else:
                failures.append({"doc": c.doc, "page": c.page, "quote": c.quote[:120], "reason": v.reason})
        # unverifiable steps are demoted to "see page N"
        for s in tree.steps:
            if any(f["quote"] == s.cite.quote[:120] for f in failures):
                s.action = f"See {s.cite.doc} page {s.cite.page} (quote could not be verified; page shown instead)."
                s.safety_class = "caution" if s.safety_class == "none" else s.safety_class
        return {"total": total, "verified": ok, "integrity": round(ok / total, 3) if total else None, "failures": failures}

    def _apply_rules(self, tree: FaultTree, hits: list[RuleHit]) -> FaultTree:
        for h in hits:
            for s in tree.steps:
                if h.matched and (h.matched in f"{s.action}. {s.expected}." or s.action in h.matched):
                    if h.action == "block":
                        s.action = f"STOP: {h.message}"
                        s.safety_class = "stop"
                    elif h.action == "rewrite" and h.rewrite_to:
                        s.action = f"{h.rewrite_to} {s.action}"
                        s.safety_class = "caution" if s.safety_class == "none" else s.safety_class
                    elif h.action == "escalate":
                        s.action = f"ESCALATE: {h.message} Original step: {s.action}"
                        s.safety_class = "stop"
                    elif h.action == "annotate":
                        s.expected = f"{s.expected} Note: {h.message}"
        return tree

    def _audit(self, tree: FaultTree, manual_doc_id: str, trace_id: str) -> AuditReport | None:
        pages = self.store.full_text(manual_doc_id)
        if not pages:
            return None
        manual = "\n\n".join(f"[page {p}]\n{t}" for p, t in pages)
        approx_tokens = len(manual) // 3
        if approx_tokens > 900_000:
            manual = manual[: 900_000 * 3]
        user = f"FULL MANUAL ({manual_doc_id}):\n{manual}\n\nPROPOSED TREE:\n{tree.model_dump_json(indent=1)}\n\nReturn the AuditReport tool call."
        try:
            return call_structured(
                self.client, Tier.DEEP, AuditReport,
                [{"role": "system", "content": AUDIT_SYSTEM}, {"role": "user", "content": user}],
                purpose="audit.fault_tree", trace_id=trace_id, max_tokens=2500, context_tokens=approx_tokens,
            )
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _apply_audit(tree: FaultTree, report: AuditReport | None) -> FaultTree:
        if not report:
            return tree
        by_id = {v.step_id: v for v in report.verdicts}
        kept: list[Step] = []
        for s in tree.steps:
            v = by_id.get(s.id)
            if v and v.verdict == "reject":
                s.action = f"See {s.cite.doc} page {s.cite.page}. (Auditor rejected the generated step: {v.reason})"
                s.safety_class = "caution" if s.safety_class == "none" else s.safety_class
            elif v and v.verdict == "repair" and v.repaired_action:
                s.action = v.repaired_action
            kept.append(s)
        tree.steps = kept
        return tree

    def enrich_fda(self, dev: dict | None) -> tuple[list[dict], dict]:
        if not dev:
            return [], {}
        ext = ROOT / "data/external"
        if self._maude is None:
            self._maude = json.loads((ext / "maude_oxygen_concentrator_malfunctions.json").read_text(encoding="utf-8"))["records"]
            self._recalls = json.loads((ext / "recalls_oxygen_concentrator.json").read_text(encoding="utf-8"))["records"]
        keys = [a.lower() for a in dev.get("model_aliases", [])] + [dev["manufacturer"].split()[0].lower()]
        rec = [r for r in self._recalls if any(k in json.dumps(r).lower() for k in keys)]
        mine = [m for m in self._maude if any(k in f"{m.get('brand_name','')} {m.get('manufacturer','')} {m.get('model_number','')}".lower() for k in keys)]
        from collections import Counter

        probs = Counter(p for m in mine for p in (m.get("product_problems") or []))
        return (
            [{"recall_number": r.get("product_res_number") or r.get("res_event_number"), "reason": (r.get("reason_for_recall") or "")[:240], "date": r.get("event_date_initiated")} for r in rec[:5]],
            {"reports": len(mine), "top_problems": probs.most_common(5), "source": "openFDA MAUDE, CC0"},
        )


def hits_to_dicts(hits: list[Hit]) -> list[dict[str, Any]]:
    return [{"doc": h.doc_id, "page": h.page, "title": h.title} for h in hits]

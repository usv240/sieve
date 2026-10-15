"""The Sieve agent: identify, intake, retrieve, synthesise, gate, audit, enrich.

Design rule: models read and draft; the rules engine, the citation verifier and the registry decide
what is allowed to reach the technician.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sieve_llm import Tier, TokenFactoryClient, call_structured
from sieve_retrieval import Hit, PageStore, Searcher
from sieve_retrieval.sentences import SentenceIndex, pack_numbered
from sieve_rules import RuleHit, RulesEngine, load_rules

from .citations import verify_quote
from .manual_finder import find_and_ingest_manual
from .registry import Registry
from .schemas import AuditReport, FaultTree, Step
from .tavily_tools import find_manual, find_parts

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


QUOTE_RULE = """1. Use ONLY the manual pages provided. Every hypothesis and every step must carry a cite with the exact doc_id, page number and a VERBATIM quote copied from that page. Never paraphrase inside quote."""

SID_RULE = """1. Use ONLY the manual pages provided. Every sentence on those pages is numbered [S1], [S2] and so on. Every hypothesis and every step must carry cite.sid: the id of the one numbered sentence that itself states that action, check or fact, plus its doc_id and page. Read the sentence before you choose it; a neighbouring sentence or a heading is not support. Leave quote empty; code copies the exact sentence from its id. If no numbered sentence states a step, leave the step out."""

SUPPORT_SYSTEM = """You check one step of a repair guide against the manual text cited for it. Answer YES if the manual text states this action or check, or the step is a direct, faithful restatement of it. Answer NO if the step adds an action the text does not mention. Reply with one word: YES or NO."""

SYNTH_SYSTEM = """You are a senior biomedical equipment engineer writing a troubleshooting tree for a technician in a district hospital.
Rules you must follow:
{rule1}
2. Steps are concrete, one action each, ordered from cheapest and safest to most invasive. Start with checks that need no tools.
3. Mark any step that opens the cabinet, touches mains, capacitors, or the oxygen path as safety_class "caution"; mark anything the manual says only qualified personnel may do as "stop".
4. If the pages do not support a step, do not write it. Prefer fewer, well-cited steps.
5. Write the summary in two plain sentences a nurse could understand."""

AUDIT_SYSTEM = """You are an independent auditor. You receive the complete service manual text and a proposed troubleshooting tree.
For each step decide: approve (the cited quote supports the action and nothing in the manual contradicts it), repair (the action is right but wording or precondition must change; give repaired_action), or reject (unsupported or contradicted). Be strict about safety preconditions (switch off and unplug before opening; patient on backup supply). Return the tool call."""


class SievePipeline:
    def __init__(self, client: TokenFactoryClient | None, store: PageStore, registry: Registry | None = None, rules: RulesEngine | None = None, cite_mode: str | None = None):
        self.cite_mode = cite_mode or os.environ.get("SIEVE_CITE_MODE", "sid")
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
        if str(answers.get("heat_smoke", "")).lower() == "yes" and not any(h.rule_id == "smoke-fire-heat" for h in in_hits):
            in_hits += self.rules.check("smoke or heat damage reported", "input")
        heat_event = any(h.rule_id == "smoke-fire-heat" for h in in_hits)
        if self.rules.blocks(in_hits):
            return AnalyzeResult(trace_id, device_id, label, None, None, in_hits, {}, [], blocked=True, notes=["blocked at input gate"])

        # build query from registry meanings + answers
        inds = [i for i in self.registry.indicators(device_id) if i["id"] in indicator_ids] if device_id else []
        meanings = [i["meaning"] for i in inds]
        states = [i["state"] for i in inds]
        q_parts = states + meanings + [f"{k}: {v}" for k, v in answers.items()] + ([free_text] if free_text else [])
        query = " ".join(q_parts) or "troubleshooting alarms indicators low oxygen purity"
        manual_fetch: dict[str, Any] = {}
        if dev and not self.store.doc_ids_for(dev["id"], None) and os.environ.get("TAVILY_API_KEY"):
            # Closed loop: no manual indexed for a known device -> Tavily finds and extracts one -> ingest -> retrieve.
            manual_fetch = find_and_ingest_manual(self.store, manufacturer=dev["manufacturer"], model=dev["model"], device_id=dev["id"], device_class=device_class, ledger=self.client.ledger if self.client else None, trace_id=trace_id)
            if manual_fetch.get("ingested"):
                notes.append(f"no manual was indexed; Tavily found and ingested {len(manual_fetch['ingested'])} web-sourced document(s)")
        hits = self.search.search(query, device_id=device_id, device_class=device_class, k=8)
        retrieved = [{"doc": h.doc_id, "title": h.title, "page": h.page, "score": round(h.score, 2), "source_url": h.source_url} for h in hits]
        if not hits:
            notes.append("no manual pages retrieved; generic flowchart only")
        if not self.client:
            res = AnalyzeResult(trace_id, device_id, label, None, None, in_hits, {}, retrieved, notes=notes + ["no model client (replay or offline-manual mode)"])
            res.recalls, res.maude_summary = self.enrich_fda(dev)
            res.tavily = self._tavily(dev, None, trace_id)
            if manual_fetch:
                res.tavily["manual_fetch"] = manual_fetch
            return res

        # synthesise
        if self.cite_mode == "sid":
            context, sidx = pack_numbered(hits, 24_000)
        else:
            context, sidx = self.search.pack_context(hits), None
        fault_ids = ", ".join(dev.get("common_faults", [])) if dev else ", ".join(sorted(self.registry.faults))
        user = (
            f"Allowed fault_id values (use only these): {fault_ids}.\n"
            f"Device: {label} (device_id={device_id}).\n"
            f"Observed indicators: {'; '.join(meanings) or 'none recorded'}.\n"
            f"Technician answers: {json.dumps(answers)}.\n"
            f"Free text: {free_text or 'none'}.\n\nManual pages:\n{context}\n\nProduce the FaultTree tool call."
        )
        if heat_event:
            user = (
                "SAFETY CONTEXT: the report describes smoke, fire, burning, sparks or heat damage. Step 1 must remove the unit "
                "from service and protect the patient, quoting the manual's warning text. Consider power-cord-thermal, "
                "internal-overheat and external-ignition-fire among the hypotheses.\n\n" + user
            )
        tree = call_structured(
            self.client, Tier.MID, FaultTree,
            [{"role": "system", "content": SYNTH_SYSTEM.replace("{rule1}", SID_RULE if self.cite_mode == "sid" else QUOTE_RULE)}, {"role": "user", "content": user}],
            purpose="synthesise.fault_tree", trace_id=trace_id, max_tokens=3000,
        )
        tree.device_id = device_id or tree.device_id

        # citation verification (deterministic)
        cit = self._verify_tree(tree, sidx)
        cit["support"] = self._support_check(tree, trace_id)

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
        res.tavily = self._tavily(dev, tree, trace_id)
        if manual_fetch:
            res.tavily["manual_fetch"] = manual_fetch
        return res

    def _tavily(self, dev: dict | None, tree: FaultTree | None, trace_id: str) -> dict[str, Any]:
        """Live web grounding, labelled web-sourced: parts for cited part numbers; a manual when we have none."""
        ledger = self.client.ledger if self.client else None
        out: dict[str, Any] = {}
        parts = [p for p in (tree.parts_candidates if tree else []) if p.part_number]
        if parts:
            out["parts"] = find_parts(parts[0].part_number or parts[0].name, dev["model"] if dev else None, ledger=ledger, trace_id=trace_id)
            out["parts"]["for"] = parts[0].name
        elif tree and tree.hypotheses:
            # No part number from the manual pages: fall back to the registry's parts hint for the top hypothesis.
            top = self.registry.faults.get(tree.hypotheses[0].fault_id, {})
            hint = top.get("parts_hint")
            if hint and dev:
                part = hint.split(",")[0]
                out["parts"] = find_parts(part, f"{dev['manufacturer']} {dev['model']}", ledger=ledger, trace_id=trace_id)
                out["parts"]["for"] = f"{part} ({top.get('name', tree.hypotheses[0].fault_id)})"
        if dev and not self.store.doc_ids_for(dev["id"], None):
            out["manual"] = find_manual(dev["model"], dev["manufacturer"], ledger=ledger, trace_id=trace_id)
        return out

    # ---------- helpers ----------
    def _support_check(self, tree: FaultTree, trace_id: str) -> dict[str, Any]:
        """Label each step: does its cited manual text state it ("manual"), or is it general practice ("general")?

        A fast Nemotron 3 Nano call per step, run in parallel. It only labels; the step text is never changed here,
        so the technician sees exactly which steps the manual itself states.
        """
        from concurrent.futures import ThreadPoolExecutor

        todo = [s for s in tree.steps if s.cite.quote and not s.action.startswith(("See ", "STOP", "ESCALATE"))]
        if not self.client or not todo or os.environ.get("SIEVE_SUPPORT_CHECK", "1") != "1":
            return {"checked": 0}

        def one(s: Step) -> None:
            try:
                r = self.client.chat(Tier.FAST, [
                    {"role": "system", "content": SUPPORT_SYSTEM},
                    {"role": "user", "content": f"STEP: {s.action}\nEXPECTED: {s.expected}\n\nMANUAL TEXT: {s.cite.quote}"},
                ], purpose="check.step_support", trace_id=trace_id, max_tokens=4, temperature=0.0)
                txt = (r.choices[0].message.content or "").strip().upper()
                s.support = "manual" if txt.startswith("YES") else "general"
            except Exception:  # noqa: BLE001
                s.support = "unchecked"

        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(one, todo))
        n_manual = sum(s.support == "manual" for s in todo)
        return {"checked": len(todo), "manual": n_manual, "general": sum(s.support == "general" for s in todo)}

    def _verify_tree(self, tree: FaultTree, sidx: SentenceIndex | None = None) -> dict[str, Any]:
        total, ok, failures = 0, 0, []
        tiers: dict[str, int] = {"id": 0, "verbatim": 0, "normalised": 0, "fuzzy": 0}
        for item in [*tree.hypotheses, *tree.steps, *[p for p in tree.parts_candidates if p.cite]]:
            c = item.cite
            total += 1
            sents = sidx.resolve_many(c.sid) if sidx else []
            if sents:
                c.doc, c.page = sents[0].doc, sents[0].page
                c.quote, c.sid = " ".join(s.text for s in sents), ", ".join(s.sid for s in sents)
                ok += 1
                tiers["id"] += 1
                continue
            if sidx and c.sid:
                failures.append({"doc": c.doc, "page": c.page, "quote": c.quote[:120], "reason": f"sentence id {c.sid} does not exist"})
                continue
            v = verify_quote(c.quote, self.store.page_text(c.doc, c.page))
            if v.ok:
                ok += 1
                tiers[v.tier] = tiers.get(v.tier, 0) + 1
            else:
                failures.append({"doc": c.doc, "page": c.page, "quote": c.quote[:120], "reason": v.reason})
        # unverifiable steps are demoted to "see page N"
        for s in tree.steps:
            if any(f["quote"] == s.cite.quote[:120] for f in failures):
                s.action = f"See {s.cite.doc} page {s.cite.page} (quote could not be verified; page shown instead)."
                s.safety_class = "caution" if s.safety_class == "none" else s.safety_class
        return {"total": total, "verified": ok, "integrity": round(ok / total, 3) if total else None, "tiers": tiers, "failures": failures}

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
        from .paths import data_dir

        ext = data_dir() / "external"
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

"""The manual talks back: a device digital twin for Training Mode.

Nemotron 3 Nano role-plays the physical machine using only its service manual. A trainee asks "I blocked the
exhaust, what happens?" and the twin answers as the machine would: which light, which alarm, after how long,
citing the page. It is a cheap, non-obvious use of a fast model: the manual becomes an interactive simulator,
and every answer is checkable against the cited page by the same verifier that checks repair steps.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from sieve_llm import Tier, TokenFactoryClient, call_structured
from sieve_retrieval import PageStore, Searcher

from .citations import verify_quote
from .registry import Registry
from .schemas import Cite


class TwinReply(BaseModel):
    """The machine's observable behaviour in response to the trainee's action."""

    lights: list[dict[str, str]] = Field(description="[{colour, state}] for every indicator after the action.")
    alarm: str = Field(description="silent | periodic beep | continuous beep")
    after_minutes: int = Field(description="How long after the action this state appears.")
    explanation: str = Field(description="Two sentences in the voice of the machine's manual: what happened and why.")
    cite: Cite
    hidden_fault_hint: str | None = Field(default=None, description="If Training Mode has a hidden fault, a one-line hint without naming it.")


SYSTEM = """You are the oxygen concentrator described in the manual pages provided. The trainee acts on you; you report ONLY what the manual says you would do (lights, alarm, timing). Quote the page verbatim in cite.quote. If the manual does not say, report 'manual does not specify' in explanation and cite the closest page. Never invent part numbers or steps."""


def twin_reply(client: TokenFactoryClient, store: PageStore, registry: Registry, *, device_id: str, action: str, hidden_fault: str | None = None, trace_id: str | None = None) -> dict[str, Any]:
    dev = registry.get(device_id)
    if not dev:
        return {"error": "unknown device"}
    s = Searcher(store)
    hits = s.search(f"{action} {hidden_fault or ''} alarm indicator LED behaviour", device_id=device_id, k=6)
    ctx = s.pack_context(hits, max_chars=16000)
    fault_ctx = f"Hidden fault present (do not name it, behave as if it is there): {registry.faults.get(hidden_fault, {}).get('name', hidden_fault)}" if hidden_fault else "No hidden fault."
    reply = call_structured(
        client,
        Tier.FAST,
        TwinReply,
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"Device: {dev['manufacturer']} {dev['model']}.\n{fault_ctx}\nTrainee action: {action}\n\nManual pages:\n{ctx}\n\nReturn the TwinReply tool call."}],
        purpose="twin.reply",
        trace_id=trace_id,
        max_tokens=800,
    )
    v = verify_quote(reply.cite.quote, store.page_text(reply.cite.doc, reply.cite.page))
    return {"reply": reply.model_dump(), "citation_verified": v.ok, "citation_tier": v.tier, "pages_used": [(h.doc_id, h.page) for h in hits]}

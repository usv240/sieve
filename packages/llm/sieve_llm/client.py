from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from openai import OpenAI

from .ledger import CallRecord, Ledger

EU_BASE = "https://api.tokenfactory.nebius.com/v1/"
US_BASE = "https://api.tokenfactory.us-central1.nebius.com/v1/"


class Tier(str, Enum):
    FAST = "fast"  # extraction, classification, drafting: thinking off
    MID = "mid"  # synthesis from retrieved evidence: thinking on, small budget
    DEEP = "deep"  # whole-document reasoning and auditing: thinking on, larger budget


@dataclass(frozen=True)
class ModelSpec:
    id: str
    base_url: str
    usd_in_per_m: float
    usd_out_per_m: float
    context: int
    label: str


MODELS: dict[str, ModelSpec] = {
    "nano": ModelSpec("nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B", EU_BASE, 0.06, 0.24, 262_144, "Nemotron 3 Nano"),
    "lightning": ModelSpec("nvidia/Nemotron-3_5-Lightning", EU_BASE, 0.06, 0.24, 1_048_576, "Nemotron 3.5 Lightning"),
    "super": ModelSpec("nvidia/nemotron-3-super-120b-a12b", US_BASE, 0.30, 0.90, 262_144, "Nemotron 3 Super"),
    "ultra": ModelSpec("nvidia/Nemotron-3-Ultra-550b-a55b", US_BASE, 1.00, 3.00, 1_048_576, "Nemotron 3 Ultra"),
}

THINKING_BUDGET = {Tier.FAST: 0, Tier.MID: 2_048, Tier.DEEP: 8_192}


def route(tier: Tier, context_tokens: int = 0) -> ModelSpec:
    """Pure routing function. Fast tier escalates to Lightning for long contexts."""
    if tier is Tier.FAST:
        return MODELS["lightning"] if context_tokens > 200_000 else MODELS["nano"]
    if tier is Tier.MID:
        return MODELS["super"]
    return MODELS["ultra"]


class TokenFactoryClient:
    """Thin wrapper over two OpenAI SDK clients (EU and US) with routing, ledger and trace."""

    def __init__(self, api_key: str | None = None, ledger: Ledger | None = None, offline_base_url: str | None = None):
        key = api_key or os.environ.get("NEBIUS_API_KEY")
        if not key and not offline_base_url:
            raise RuntimeError("NEBIUS_API_KEY is not set. Copy .env.example to .env and fill it in.")
        self.offline_base_url = offline_base_url or os.environ.get("OFFLINE_BASE_URL") or None
        self._clients: dict[str, OpenAI] = {}
        if key:
            self._clients[EU_BASE] = OpenAI(api_key=key, base_url=EU_BASE, max_retries=3, timeout=120)
            self._clients[US_BASE] = OpenAI(api_key=key, base_url=US_BASE, max_retries=3, timeout=180)
        if self.offline_base_url:
            self._clients[self.offline_base_url] = OpenAI(api_key="offline", base_url=self.offline_base_url, timeout=600)
        self.ledger = ledger or Ledger()

    def _client_for(self, spec: ModelSpec) -> tuple[OpenAI, str]:
        if self.offline_base_url:
            # Offline mode: everything goes to the local llama.cpp server; deep tier is disabled by callers.
            return self._clients[self.offline_base_url], os.environ.get("OFFLINE_MODEL", "nemotron-3-nano")
        return self._clients[spec.base_url], spec.id

    def chat(
        self,
        tier: Tier,
        messages: list[dict[str, Any]],
        *,
        purpose: str,
        trace_id: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: Any = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        context_tokens: int = 0,
    ) -> Any:
        spec = route(tier, context_tokens)
        client, model_id = self._client_for(spec)
        thinking_on = tier is not Tier.FAST
        extra_body: dict[str, Any] = {"chat_template_kwargs": {"enable_thinking": thinking_on}}
        budget = THINKING_BUDGET[tier]
        if thinking_on and spec.id == MODELS["ultra"].id:
            extra_body["chat_template_kwargs"]["reasoning_budget"] = budget
        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens + (budget if thinking_on else 0),
            "temperature": temperature,
            "extra_body": extra_body,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice or "required"
        t0 = time.perf_counter()
        resp = client.chat.completions.create(**kwargs)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        usage = getattr(resp, "usage", None)
        tin = getattr(usage, "prompt_tokens", 0) or 0
        tout = getattr(usage, "completion_tokens", 0) or 0
        usd = (tin * spec.usd_in_per_m + tout * spec.usd_out_per_m) / 1_000_000
        self.ledger.record(
            CallRecord(
                trace_id=trace_id or str(uuid.uuid4()),
                tier=tier.value,
                model=spec.label if not self.offline_base_url else f"offline:{model_id}",
                model_id=model_id,
                purpose=purpose,
                tokens_in=tin,
                tokens_out=tout,
                usd=0.0 if self.offline_base_url else usd,
                latency_ms=latency_ms,
            )
        )
        return resp

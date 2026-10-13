"""Smoke test: one real call per tier against Nebius Token Factory. Prints the ledger.

Run: make smoke   (needs NEBIUS_API_KEY in .env or the environment)
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages/llm"))

from pydantic import BaseModel
from rich import print
from sieve_llm import Ledger, Tier, TokenFactoryClient, call_structured


def load_env() -> None:
    env = Path(__file__).resolve().parents[1] / ".env"
    if not env.exists():
        env = Path(__file__).resolve().parents[2] / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


class DeviceGuess(BaseModel):
    """Identify the device class from a short description."""

    device_class: str
    manufacturer: str | None = None
    confidence: float


def main() -> None:
    load_env()
    ledger = Ledger("data/ledger.db")
    client = TokenFactoryClient(ledger=ledger)
    trace = str(uuid.uuid4())

    # FAST: structured extraction with thinking off
    guess = call_structured(
        client,
        Tier.FAST,
        DeviceGuess,
        [
            {"role": "system", "content": "You extract structured facts. Use the tool."},
            {"role": "user", "content": "Nameplate reads: Philips Respironics EverFlo, REF 1020000, 230V 50Hz."},
        ],
        purpose="smoke.identify",
        trace_id=trace,
    )
    print("[bold]FAST[/bold]", guess)

    # MID: short reasoning
    r = client.chat(
        Tier.MID,
        [{"role": "user", "content": "In one sentence: why does a yellow light on an oxygen concentrator usually appear after 15 minutes?"}],
        purpose="smoke.reason",
        trace_id=trace,
        max_tokens=200,
    )
    print("[bold]MID[/bold]", (r.choices[0].message.content or "").strip()[:300])

    # DEEP: tiny audit call to confirm the Ultra endpoint works
    r = client.chat(
        Tier.DEEP,
        [{"role": "user", "content": "Reply with the single word APPROVE."}],
        purpose="smoke.audit",
        trace_id=trace,
        max_tokens=20,
    )
    print("[bold]DEEP[/bold]", (r.choices[0].message.content or "").strip()[:50])

    print("\n[bold]Trace[/bold]")
    for row in ledger.trace(trace):
        print(f"  {row['tier']:5} {row['model']:22} {row['purpose']:16} in={row['tokens_in']:>6} out={row['tokens_out']:>5} ${row['usd']:.5f} {row['latency_ms']} ms")
    print("\n[bold]Totals[/bold]", ledger.totals())


if __name__ == "__main__":
    main()

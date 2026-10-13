"""Token Factory client, model router, cost ledger and trace for Sieve.

Facts this module encodes (verified 2026-10-13):
- Nemotron 3 Nano and 3.5 Lightning are served from the EU base URL; Super and Ultra from the US base URL.
- Nemotron reasons by default; extraction calls disable it via chat_template_kwargs.enable_thinking=false.
- Nemotron models have no JSON-mode tag on Token Factory; structured output uses tool calling.
"""

from .client import MODELS, ModelSpec, Tier, TokenFactoryClient
from .ledger import CallRecord, Ledger
from .structured import call_structured

__all__ = [
    "MODELS",
    "CallRecord",
    "Ledger",
    "ModelSpec",
    "Tier",
    "TokenFactoryClient",
    "call_structured",
]

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ValidationError

from .client import Tier, TokenFactoryClient


def _tool_for(schema: type[BaseModel]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": schema.__name__,
            "description": (schema.__doc__ or "Return the structured result.").strip(),
            "parameters": schema.model_json_schema(),
        },
    }


def call_structured[T: BaseModel](
    client: TokenFactoryClient,
    tier: Tier,
    schema: type[T],
    messages: list[dict[str, Any]],
    *,
    purpose: str,
    trace_id: str | None = None,
    max_tokens: int = 2048,
    context_tokens: int = 0,
    retries: int = 1,
) -> T:
    """Structured output via a single forced tool call, validated with pydantic.

    Nemotron on Token Factory does not advertise JSON mode, so tool calling is the reliable path.
    On validation failure the error is appended and the call is retried once.
    """
    tool = _tool_for(schema)
    msgs = list(messages)
    last_err: Exception | None = None
    for _ in range(retries + 1):
        resp = client.chat(
            tier,
            msgs,
            purpose=purpose,
            trace_id=trace_id,
            tools=[tool],
            tool_choice={"type": "function", "function": {"name": schema.__name__}},
            max_tokens=max_tokens,
            context_tokens=context_tokens,
        )
        msg = resp.choices[0].message
        raw: str | None = None
        if msg.tool_calls:
            raw = msg.tool_calls[0].function.arguments
        elif msg.content:
            raw = msg.content
        try:
            data = json.loads(raw or "{}")
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = e
            msgs = msgs + [
                {"role": "assistant", "content": raw or ""},
                {"role": "user", "content": f"The previous output failed validation: {e}. Return a corrected tool call."},
            ]
    raise RuntimeError(f"Structured output failed after retries: {last_err}")

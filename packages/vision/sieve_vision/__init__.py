"""Vision: structured description of a device photo. Fallback chain, never a dead end.

1. Self-hosted NVIDIA Nemotron Nano VL on a Nebius Serverless Endpoint (VISION_ENDPOINT_URL).
2. A Token Factory image2text model resolved at runtime from /v1/models.
3. Manual entry (the caller receives mode="manual" and the UI shows fields).
Vision is asked only to describe; it never decides.
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
from pydantic import BaseModel


class NameplateFields(BaseModel):
    """Structured fields visible in a photo of a medical device."""

    manufacturer: str | None = None
    model: str | None = None
    ref: str | None = None
    serial: str | None = None
    device_type_guess: str | None = None
    visible_text: list[str] = []
    indicators: list[dict[str, str]] = []  # {colour, state, label}
    confidence: float = 0.0


@dataclass
class VisionResult:
    mode: str  # "nemotron-vl" | "tf-image2text" | "manual"
    fields: NameplateFields
    raw: str = ""
    notes: list[str] = field(default_factory=list)


PROMPT = (
    "You are reading a photo of a medical device for a technician. Return ONLY a JSON object with keys: "
    "manufacturer, model, ref, serial, device_type_guess, visible_text (at most 15 short strings exactly as printed, words only; skip scale numbers and repeated symbols), "
    "indicators (list of {colour, state, label} for any lights or displays you can see), confidence (0 to 1). "
    "Do not guess values that are not visible; use null."
)


def _data_url(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64,{base64.b64encode(image_bytes).decode()}"


def _salvage(raw: str) -> dict[str, Any]:
    """Recover string fields and the text list from a reply that was cut off mid-JSON."""
    import re

    out: dict[str, Any] = {}
    for k in ("manufacturer", "model", "ref", "serial", "device_type_guess"):
        m = re.search(rf'"{k}"\s*:\s*"([^"]*)"', raw)
        if m:
            out[k] = m.group(1)
    m = re.search(r'"visible_text"\s*:\s*\[(.*?)(\]|$)', raw, re.DOTALL)
    if m:
        out["visible_text"] = re.findall(r'"([^"]{2,80})"', m.group(1))[:20]
    return out


def _parse(raw: str) -> NameplateFields:
    start, end = raw.find("{"), raw.rfind("}")
    if start >= 0 and end > start:
        try:
            return NameplateFields.model_validate(json.loads(raw[start : end + 1]))
        except Exception:  # noqa: BLE001, S110 - fall through to salvage below
            pass
    salvaged = _salvage(raw)
    if salvaged:
        try:
            return NameplateFields.model_validate({**salvaged, "confidence": 0.5})
        except Exception:  # noqa: BLE001
            return NameplateFields(confidence=0.0, visible_text=["parse_error"])
    return NameplateFields(confidence=0.0, visible_text=["parse_error"] if raw else [])


def _openai_vision_call(base_url: str, api_key: str, model: str, image_bytes: bytes, timeout: float = 90) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": 1500,
        "temperature": 0.0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": _data_url(image_bytes)}},
                ],
            }
        ],
    }
    if "nemotron" in model.lower():
        payload["chat_template_kwargs"] = {"enable_thinking": False}  # read, do not deliberate
    last: Exception | None = None
    for attempt in range(3):  # rate limits and transient 5xx are retried with backoff
        try:
            r = httpx.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                import time

                time.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"] or ""
        except httpx.TransportError as e:
            last = e
    raise last or RuntimeError("vision call failed")


# NVIDIA Nemotron 3.5 Super VL first: on real Indian pesticide labels it read Gramoxone as paraquat where MiniCPM-V
# invented organophosphates from the small print (2026-10-27). Others are fallbacks if it is missing or fails.
IMAGE_MODELS = ["nvidia/Nemotron-3.5-Super-VL", "openbmb/MiniCPM-V-4_5", "Qwen/Qwen3.8-27B"]


def _tf_image_models(api_key: str, base_url: str) -> list[str]:
    """Image-capable models from Token Factory's live catalog, in preference order. Cached for the process."""
    cache = os.environ.get("_TF_IMG_MODELS")
    if cache:
        return cache.split(",")
    try:
        r = httpx.get(f"{base_url.rstrip('/')}/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=20)
        r.raise_for_status()
        ids = [m["id"] for m in r.json().get("data", [])]
        picks = [m for m in IMAGE_MODELS if m in ids] or [i for i in ids if any(k in i.lower() for k in ("-vl", "vision", "minicpm-v"))][:2]
        if picks:
            os.environ["_TF_IMG_MODELS"] = ",".join(picks)
        return picks
    except Exception:  # noqa: BLE001
        return []


def describe(image_bytes: bytes) -> VisionResult:
    notes: list[str] = []
    ep, tok = os.environ.get("VISION_ENDPOINT_URL"), os.environ.get("VISION_ENDPOINT_TOKEN", "none")
    if ep:
        try:
            raw = _openai_vision_call(ep, tok, os.environ.get("VISION_MODEL", "nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL"), image_bytes)
            return VisionResult("nemotron-vl", _parse(raw), raw, notes)
        except Exception as e:  # noqa: BLE001
            notes.append(f"nemotron-vl endpoint failed: {type(e).__name__}")
    key = os.environ.get("NEBIUS_API_KEY")
    base = "https://api.tokenfactory.nebius.com/v1/"
    if key:
        models = _tf_image_models(key, base)
        for model in models:
            try:
                raw = _openai_vision_call(base, key, model, image_bytes)
                notes.append(f"image model: {model}")
                mode = "nemotron-vl" if "nemotron" in model.lower() else "tf-image2text"
                return VisionResult(mode, _parse(raw), raw, notes)
            except Exception as e:  # noqa: BLE001
                notes.append(f"{model} failed: {type(e).__name__}")
        if not models:
            notes.append("no image model found in Token Factory catalog")
    else:
        notes.append("NEBIUS_API_KEY not set")
    notes.append("manual entry required")
    return VisionResult("manual", NameplateFields(), "", notes)

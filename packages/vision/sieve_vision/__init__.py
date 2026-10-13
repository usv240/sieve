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
    "manufacturer, model, ref, serial, device_type_guess, visible_text (list of strings exactly as printed), "
    "indicators (list of {colour, state, label} for any lights or displays you can see), confidence (0 to 1). "
    "Do not guess values that are not visible; use null."
)


def _data_url(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64,{base64.b64encode(image_bytes).decode()}"


def _parse(raw: str) -> NameplateFields:
    start, end = raw.find("{"), raw.rfind("}")
    if start >= 0 and end > start:
        try:
            return NameplateFields.model_validate(json.loads(raw[start : end + 1]))
        except Exception as e:  # noqa: BLE001
            return NameplateFields(confidence=0.0, visible_text=[f"parse_error: {type(e).__name__}"])
    return NameplateFields(confidence=0.0)


def _openai_vision_call(base_url: str, api_key: str, model: str, image_bytes: bytes, timeout: float = 90) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": 600,
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
    r = httpx.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"] or ""


def _tf_image_model(api_key: str, base_url: str) -> str | None:
    """Pick an image-capable model from Token Factory's live catalog. Cached for the process."""
    cache = os.environ.get("_TF_IMG_MODEL")
    if cache:
        return cache
    try:
        r = httpx.get(f"{base_url.rstrip('/')}/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=20)
        r.raise_for_status()
        ids = [m["id"] for m in r.json().get("data", [])]
        preferred = [i for i in ids if any(k in i.lower() for k in ("vl", "vision", "minicpm-v", "kimi", "glm-5.3-flash", "qwen3.8"))]
        pick = preferred[0] if preferred else None
        if pick:
            os.environ["_TF_IMG_MODEL"] = pick
        return pick
    except Exception:  # noqa: BLE001
        return None


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
        model = _tf_image_model(key, base)
        if model:
            try:
                raw = _openai_vision_call(base, key, model, image_bytes)
                notes.append(f"fallback image2text model: {model}")
                return VisionResult("tf-image2text", _parse(raw), raw, notes)
            except Exception as e:  # noqa: BLE001
                notes.append(f"tf image2text failed: {type(e).__name__}")
        else:
            notes.append("no image2text model found in Token Factory catalog")
    else:
        notes.append("NEBIUS_API_KEY not set")
    notes.append("manual entry required")
    return VisionResult("manual", NameplateFields(), "", notes)

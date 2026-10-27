"""Telegram front door: photograph the machine, say what is wrong in the caption, get the cited steps back.

The handler is a pure function over a Telegram update so it can be tested without the network. The webhook route in
main.py verifies Telegram's secret header, then calls handle_update with real I/O.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

MAX_STEPS = 6


def format_plan(res: Any) -> str:
    lines: list[str] = [f"Device: {res.device_label}"]
    stops = [h for h in res.rule_hits if h.severity == "stop"]
    for h in stops:
        lines += ["", f"STOP: {h.message}"]
    if res.blocked:
        lines += ["", "Sieve stopped before asking any model. Nothing else is shown for this request."]
        return "\n".join(lines)
    tree = res.tree
    if not tree:
        lines += ["", "No manual pages matched. Upload the service manual at the web app, or describe the problem in more detail."]
        return "\n".join(lines)
    lines += ["", tree.summary]
    for i, s in enumerate(tree.steps[:MAX_STEPS], 1):
        label = {"manual": " [manual states this]", "general": " [general practice]"}.get(getattr(s, "support", ""), "")
        lines += ["", f"{i}. {s.action}{label}", f"   Expect: {s.expected}"]
        if s.cite and s.cite.page:
            lines.append(f"   Manual page {s.cite.page}")
    lines += ["", "Answer each check before the next one in the web app to follow the branches, and record the work order."]
    return "\n".join(lines)


def handle_update(
    update: dict[str, Any],
    *,
    identify: Callable[[str], str | None],
    analyze: Callable[[str | None, str], Any],
    send: Callable[[int, str], None],
) -> str:
    """identify(file_id) returns a registry device_id or None; analyze(device_id, free_text) returns an AnalyzeResult."""
    msg = update.get("message") or update.get("edited_message") or {}
    chat = (msg.get("chat") or {}).get("id")
    if chat is None:
        return "ignored: no chat"
    text = (msg.get("text") or msg.get("caption") or "").strip()
    if text.startswith(("/start", "/help")):
        send(chat, "Photograph the nameplate or the front panel of the machine and write what is wrong in the caption, "
                   "for example: yellow light on, alarm after 20 minutes. You will get the manufacturer's own steps with the manual page for each. "
                   "Smoke, burning or oil near oxygen stops the plan before any model replies.")
        return "help"
    if msg.get("photo"):
        send(chat, "Reading the machine...")
        device = identify(msg["photo"][-1]["file_id"])
        if not device:
            send(chat, "I could not match this machine to a manual I have. Try a photo of the nameplate on the back, or upload the manual in the web app.")
            return "photo unmatched"
        send(chat, format_plan(analyze(device, text)))
        return "photo plan"
    if text:
        send(chat, "Send a photo of the machine with this description as the caption, so I can open the right manual.")
        return "asked for photo"
    return "ignored: no content"

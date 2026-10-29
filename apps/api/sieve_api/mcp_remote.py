"""Sieve as a hosted MCP server at /mcp (streamable HTTP, stateless), so any agent adds it by URL with no install.

The tools call the same pipeline, registry and page store as the HTTP API; the safety rules, citation verifier and
Nemotron 3 Ultra audit run exactly as they do for the web app. Stateless mode fits a serverless function: every
request gets its own session manager, so nothing depends on the app's lifespan.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from mcp.server.mcpserver import MCPServer
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from sieve_api import main as api

mcp = MCPServer(
    "sieve",
    instructions=(
        "Repair copilot for hospital oxygen concentrators. Call list_devices or identify_device first, then diagnose "
        "with the device and what the front panel shows. Every step cites a service-manual page; read_manual_page "
        "returns that page. If the result is blocked, show the stop to the technician and do not suggest a workaround."
    ),
)


@mcp.tool()
def list_devices() -> dict[str, Any]:
    """Devices Sieve covers, with their indicator ids (front-panel lights and alarms) and whether a manual is indexed."""
    return {"devices": api.devices()}


@mcp.tool()
def identify_device(manufacturer: str = "", model: str = "", ref: str = "", visible_text: list[str] | None = None) -> dict[str, Any]:
    """Match nameplate fields to a covered device. The registry decides; nothing is guessed."""
    body = api.IdentifyBody(manufacturer=manufacturer or None, model=model or None, ref=ref or None, visible_text=visible_text or [])
    return api.identify(body)


@mcp.tool()
def diagnose(device_id: str, indicator_ids: list[str] | None = None, free_text: str = "", audit: bool = True) -> dict[str, Any]:
    """Manual-grounded repair plan with safety stops. Nemotron 3 Super writes it, a verifier checks every cited sentence
    on its page, fixed rules stop hazards (oil near oxygen, live mains, smoke) and Nemotron 3 Ultra audits the plan
    against the whole manual. Takes up to a minute with the audit on."""
    try:
        out = api.analyze(api.AnalyzeBody(device_id=device_id, indicator_ids=indicator_ids or [], free_text=free_text, audit=audit))
    except HTTPException as e:
        return {"error": e.detail}
    keep = ("trace_id", "device_id", "device_label", "blocked", "tree", "audit", "rule_hits", "citations", "recalls", "notes", "latency_ms")
    return {k: out.get(k) for k in keep} | {"models": [{"model": t.get("model"), "tier": t.get("tier"), "usd": t.get("usd")} for t in out.get("trace") or []]}


@mcp.tool()
def read_manual_page(doc_id: str, page: int) -> dict[str, Any]:
    """Full text of one indexed service-manual page, with its title and source, to check a citation."""
    try:
        return api.page(doc_id, page)
    except HTTPException as e:
        return {"error": f"{e.detail}: {doc_id} page {page}. Use a doc_id and page from a diagnose citation."}


class MCPEndpoint:
    """ASGI endpoint the API routes /mcp to. A class instance, so Starlette passes it the raw ASGI call."""

    async def __call__(self, scope, receive, send) -> None:
        manager = StreamableHTTPSessionManager(app=mcp._lowlevel_server, json_response=True, stateless=True)
        async with manager.run():
            await manager.handle_request(scope, receive, send)

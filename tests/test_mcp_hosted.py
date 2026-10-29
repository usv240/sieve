"""The hosted MCP endpoint at /mcp: an agent on another host can list the tools and call one. No model key needed."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
from fastapi.testclient import TestClient
from sieve_api.main import app

client = TestClient(app)
HEADERS = {"Accept": "application/json, text/event-stream", "Host": "sieve-api.vercel.app"}


def rpc(method: str, params: dict | None = None) -> dict:
    r = client.post("/mcp", headers=HEADERS, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}})
    assert r.status_code == 200
    return r.json()["result"]


def test_tools_are_listed_and_callable_from_another_host():
    assert sorted(t["name"] for t in rpc("tools/list")["tools"]) == ["diagnose", "identify_device", "list_devices", "read_manual_page"]
    out = rpc("tools/call", {"name": "list_devices", "arguments": {}})
    assert not out["isError"] and json.loads(out["content"][0]["text"])["devices"]

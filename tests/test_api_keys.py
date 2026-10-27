"""Signed API keys: issued, verified, and rejected when forged. No network, no model key needed."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
from fastapi.testclient import TestClient
from sieve_api.main import app

client = TestClient(app)


def test_issued_key_verifies_and_forged_key_is_rejected():
    key = client.post("/v1/keys", json={"label": "judge"}).json()["key"]
    assert key.startswith("sieve_judge_")
    ok = client.get("/v1/keys/verify", headers={"X-API-Key": key}).json()
    assert ok["valid"] is True and ok["label"] == "judge"
    forged = key[:-4] + "abcd"
    r = client.get("/v1/keys/verify", headers={"X-API-Key": forged})
    assert r.status_code == 401


def test_rate_limit_headers_are_sent():
    r = client.get("/v1/keys/verify")
    assert "X-RateLimit-Remaining" in r.headers


def test_rejections_carry_cors_headers_so_browsers_can_read_them():
    r = client.get("/v1/keys/verify", headers={"X-API-Key": "forged_x.y", "Origin": "https://example.com"})
    assert r.status_code == 401 and r.headers.get("access-control-allow-origin") == "*"

"""When the model service fails, every sample preset still answers from its recording, marked as a replay."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
from fastapi.testclient import TestClient
from sieve_api import main

REPLAY = Path(__file__).resolve().parents[1] / "data/samples/replay"


def _boom(*_a, **_k):
    raise RuntimeError("simulated model outage")


def test_every_preset_survives_a_model_outage(monkeypatch):
    monkeypatch.setattr(main.PIPE, "analyze", _boom)
    client = TestClient(main.app)
    recs = sorted(REPLAY.glob("*.json"))
    assert len(recs) >= 6
    for f in recs:
        req = json.loads(f.read_text(encoding="utf-8"))["request"]
        r = client.post("/v1/analyze", json=req)
        assert r.status_code == 200, f.name
        assert r.json()["mode"] == "replay"


def test_unknown_request_gets_an_honest_503(monkeypatch):
    monkeypatch.setattr(main.PIPE, "analyze", _boom)
    body = {"device_id": "nobody", "indicator_ids": [], "answers": {}}
    r = TestClient(main.app).post("/v1/analyze", json=body)
    assert r.status_code == 503 and "sample presets" in r.json()["detail"]

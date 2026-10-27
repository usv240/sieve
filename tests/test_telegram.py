"""Telegram handler: no network, no model key."""

import sys
from pathlib import Path

import pytest
from sieve_core import Registry
from sieve_core.pipeline import SievePipeline
from sieve_retrieval import PageStore

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
from sieve_api.telegram import handle_update

INDEX = Path(__file__).resolve().parents[1] / "data/index/sieve.db"


def test_smoke_in_caption_stops_before_any_step():
    if not (INDEX.exists() and INDEX.stat().st_size > 1_000_000):
        pytest.skip("index not built")
    pipe = SievePipeline(None, PageStore(INDEX), Registry())
    sent: list[str] = []
    did = handle_update({"message": {"chat": {"id": 7}, "photo": [{"file_id": "x"}], "caption": "smoke coming from the back"}},
                        identify=lambda _f: "devilbiss-525",
                        analyze=lambda d, t: pipe.analyze(device_id=d, indicator_ids=[], answers={}, free_text=t, audit=False),
                        send=lambda _c, t: sent.append(t))
    assert did == "photo plan"
    assert "STOP" in sent[-1] and "remove the unit from service" in sent[-1].lower()


def test_unmatched_photo_asks_for_nameplate():
    sent: list[str] = []
    did = handle_update({"message": {"chat": {"id": 7}, "photo": [{"file_id": "x"}]}},
                        identify=lambda _f: None, analyze=lambda d, t: None, send=lambda _c, t: sent.append(t))
    assert did == "photo unmatched" and "nameplate" in sent[-1]

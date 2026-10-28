"""Pipeline tests that need no model key: retrieval, gating, citation verification, FDA enrichment."""

from pathlib import Path

import pytest
from sieve_core import Registry
from sieve_core.pipeline import SievePipeline
from sieve_retrieval import PageStore

INDEX = Path(__file__).resolve().parents[1] / "data/index/sieve.db"
pytestmark = pytest.mark.skipif(not (INDEX.exists() and INDEX.stat().st_size > 1_000_000), reason="run `make fetch-corpus && make ingest` first")


@pytest.fixture(scope="module")
def pipe():
    return SievePipeline(None, PageStore(INDEX), Registry())


def test_retrieval_is_device_scoped_and_hits_indicator_table(pipe):
    res = pipe.analyze(device_id="philips-everflo", indicator_ids=["everflo-yellow-solid-silent"], answers={"warmup": "yes"})
    assert res.retrieved, "expected manual pages"
    assert all("everflo" in r["doc"] for r in res.retrieved)
    assert any(r["page"] == 31 for r in res.retrieved), "page 31 is the EverFlo indicators table"


def test_input_gate_blocks_hazard_before_any_model(pipe):
    res = pipe.analyze(device_id="philips-everflo", indicator_ids=[], answers={}, free_text="Can I put some oil on the compressor to quiet it?")
    assert res.blocked and any(h.rule_id == "oxygen-oil-grease" for h in res.rule_hits)


def test_fda_enrichment_finds_devilbiss_reports(pipe):
    _recalls, maude = pipe.enrich_fda(pipe.registry.get("devilbiss-525"))
    assert maude["reports"] > 0
    assert maude["source"].startswith("openFDA")


def test_doc_id_limits_retrieval_to_one_document() -> None:
    """Bring your own manual: with doc_id, every retrieved page comes from that document and nowhere else."""
    from sieve_retrieval import Searcher

    store = PageStore(INDEX)
    doc = store.doc_ids_for("philips-everflo", None)[0]
    hits = Searcher(store).search("low oxygen alarm purity", device_id=None, device_class=None, k=8, doc_id=doc)
    assert hits and {h.doc_id for h in hits} == {doc}

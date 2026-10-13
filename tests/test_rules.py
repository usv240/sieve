from pathlib import Path

import pytest
from sieve_rules import load_rules

RULES = Path(__file__).resolve().parents[1] / "packages/rules/sieve_rules/sieve.yaml"


@pytest.fixture()
def engine():
    return load_rules(RULES)


@pytest.mark.parametrize(
    "text,rule_id",
    [
        ("Apply a little oil to the compressor bearings", "oxygen-oil-grease"),
        ("Use WD-40 on the valve", "oxygen-oil-grease"),
        ("Disable the purity alarm so the unit keeps running", "purity-alarm-bypass"),
        ("Measure the mains voltage at the input terminals while the unit runs", "mains-live-testing"),
        ("Check the start capacitor on the compressor", "capacitor-discharge"),
        ("The battery pack looks swollen", "swollen-battery"),
    ],
)
def test_hazardous_inputs_fire(engine, text, rule_id):
    hits = engine.check(text, "input") or engine.check(text, "output")
    assert any(h.rule_id == rule_id for h in hits), f"expected {rule_id} to fire on: {text}"


def test_open_cabinet_without_unplug_is_rewritten(engine):
    text = "Remove the cabinet cover and inspect the sieve beds."
    hits = engine.check(text, "output")
    assert any(h.rule_id == "open-while-running" for h in hits)
    out = engine.apply_rewrites(text, hits)
    assert "unplug" in out.lower()


def test_open_cabinet_with_unplug_passes(engine):
    text = "Switch off and unplug the unit, then remove the cabinet cover and inspect the sieve beds."
    hits = engine.check(text, "output")
    assert not any(h.rule_id == "open-while-running" for h in hits)


@pytest.mark.parametrize(
    "text",
    [
        "Replace the inlet filter and check the cannula for kinks.",
        "Wait 15 minutes for warm-up, then read the purity with an oxygen analyser.",
        "Check that the unit has at least 30 cm of clearance from walls for ventilation.",
    ],
)
def test_benign_steps_do_not_block(engine, text):
    hits = engine.check(text, "output")
    assert not engine.blocks(hits), f"benign step was blocked: {text} -> {[h.rule_id for h in hits]}"

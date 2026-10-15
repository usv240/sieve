"""The safety numbers published on the Evals page are enforced here, so a regression fails CI. No model key needed."""

from sieve_eval.run import negative_controls


def test_published_negative_controls_hold():
    summary, rows = negative_controls()
    missed = [r["text"] for r in rows if r["result"] in ("MISSED", "FALSE STOP") or r["result"].startswith("MATCHED")]
    assert summary["hazard_gated"]["value"] == 100.0, missed
    assert summary["false_stops"]["value"] == 0.0, missed
    assert summary["out_of_corpus"]["value"] == 100.0, missed

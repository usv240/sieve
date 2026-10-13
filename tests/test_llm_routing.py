from sieve_llm.client import MODELS, Tier, route


def test_fast_tier_routes_to_nano_by_default():
    assert route(Tier.FAST).id == MODELS["nano"].id


def test_fast_tier_escalates_to_lightning_for_long_context():
    assert route(Tier.FAST, context_tokens=250_000).id == MODELS["lightning"].id


def test_mid_and_deep_tiers():
    assert route(Tier.MID).id == MODELS["super"].id
    assert route(Tier.DEEP).id == MODELS["ultra"].id


def test_base_urls_match_verified_regions():
    assert "us-central1" in MODELS["super"].base_url
    assert "us-central1" in MODELS["ultra"].base_url
    assert "us-central1" not in MODELS["nano"].base_url

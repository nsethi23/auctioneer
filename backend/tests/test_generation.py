import random

from auctioneer.simulation.generation import generate_bidders


def test_generate_bidders_returns_requested_count():
    bidders = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))

    assert len(bidders) == 3


def test_generate_bidders_uses_expected_ids():
    bidders = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))

    assert bidders[0]["id"] == "B0"
    assert bidders[1]["id"] == "B1"
    assert bidders[2]["id"] == "B2"


def test_generate_bidders_values_are_within_range():
    bidders = generate_bidders(20, 1.0, 10.0, rng=random.Random(123))

    for bidder in bidders:
        assert 1.0 <= bidder["value"] <= 10.0


def test_generate_bidders_bids_truthfully_by_default():
    bidders = generate_bidders(20, 1.0, 10.0, rng=random.Random(123))

    for bidder in bidders:
        assert bidder["bid"] == bidder["value"]


def test_generate_bidders_is_deterministic_with_seeded_rng():
    first = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))
    second = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))

    assert first == second

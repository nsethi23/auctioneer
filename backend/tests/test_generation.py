import random

import pytest

from auctioneer.agents.strategies import shaded_bid
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


def test_generate_bidders_accepts_shaded_strategy():
    bidders = generate_bidders(
        3,
        10.0,
        10.0,
        rng=random.Random(123),
        strategy=shaded_bid,
        strategy_kwargs={"shade_factor": 0.8},
    )

    for bidder in bidders:
        assert bidder["value"] == pytest.approx(10.0)
        assert bidder["bid"] == pytest.approx(8.0)


def test_generate_bidders_accepts_strategy_kwargs():
    bidders = generate_bidders(
        1,
        10.0,
        10.0,
        rng=random.Random(123),
        strategy=shaded_bid,
        strategy_kwargs={"shade_factor": 0.25},
    )

    assert bidders[0]["value"] == pytest.approx(10.0)
    assert bidders[0]["bid"] == pytest.approx(2.5)


def test_generate_bidders_is_deterministic_with_seeded_rng():
    first = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))
    second = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))

    assert first == second

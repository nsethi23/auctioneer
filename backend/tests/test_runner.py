import random

import pytest

from auctioneer.agents.strategies import shaded_bid
from auctioneer.simulation.runner import run_repeated_comparisons


def test_run_repeated_comparisons_returns_requested_count():
    result = run_repeated_comparisons(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        rng=random.Random(123),
    )

    assert result["num_auctions"] == 5


def test_run_repeated_comparisons_includes_average_metrics():
    result = run_repeated_comparisons(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        rng=random.Random(123),
    )

    assert "gsp" in result["averages"]
    assert "vcg" in result["averages"]
    assert "difference" in result["averages"]

    assert "revenue" in result["averages"]["gsp"]
    assert "welfare" in result["averages"]["gsp"]
    assert "bidder_surplus" in result["averages"]["gsp"]

    assert "revenue" in result["averages"]["vcg"]
    assert "welfare" in result["averages"]["vcg"]
    assert "bidder_surplus" in result["averages"]["vcg"]

    assert "revenue" in result["averages"]["difference"]
    assert "welfare" in result["averages"]["difference"]
    assert "bidder_surplus" in result["averages"]["difference"]


def test_run_repeated_comparisons_is_deterministic_with_seeded_rng():
    first = run_repeated_comparisons(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        rng=random.Random(123),
    )

    second = run_repeated_comparisons(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        rng=random.Random(123),
    )

    assert first == second


def test_run_repeated_comparisons_with_zero_slots_has_zero_metrics():
    result = run_repeated_comparisons(
        num_auctions=5,
        num_bidders=3,
        ctrs=[],
        min_value=1.0,
        max_value=10.0,
        rng=random.Random(123),
    )

    for mechanism in ["gsp", "vcg", "difference"]:
        assert result["averages"][mechanism]["revenue"] == pytest.approx(0.0)
        assert result["averages"][mechanism]["welfare"] == pytest.approx(0.0)
        assert result["averages"][mechanism]["bidder_surplus"] == pytest.approx(0.0)


def test_run_repeated_comparisons_accepts_shaded_strategy():
    truthful_result = run_repeated_comparisons(
        num_auctions=1,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=10.0,
        max_value=10.0,
        rng=random.Random(123),
    )

    shaded_result = run_repeated_comparisons(
        num_auctions=1,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=10.0,
        max_value=10.0,
        rng=random.Random(123),
        strategy=shaded_bid,
        strategy_kwargs={"shade_factor": 0.5},
    )

    assert (
        shaded_result["averages"]["gsp"]["revenue"]
        < truthful_result["averages"]["gsp"]["revenue"]
    )


def test_run_repeated_comparisons_passes_strategy_kwargs():
    result = run_repeated_comparisons(
        num_auctions=1,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=10.0,
        max_value=10.0,
        rng=random.Random(123),
        strategy=shaded_bid,
        strategy_kwargs={"shade_factor": 0.25},
    )

    assert result["averages"]["gsp"]["revenue"] == pytest.approx(2.25)

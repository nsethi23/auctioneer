import random

import pytest

from auctioneer.agents.strategies import shaded_bid, truthful_bid
from auctioneer.simulation.mixed_profiles import run_mixed_profile_comparison


def test_run_mixed_profile_comparison_returns_generated_bidders():
    profiles = [
        {
            "id": "truthful",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        },
        {
            "id": "shaded",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_kwargs": {"shade_factor": 0.8},
        },
    ]

    result = run_mixed_profile_comparison(
        profiles,
        ctrs=[0.6, 0.3],
        rng=random.Random(123),
    )

    assert len(result["bidders"]) == 2
    assert result["bidders"][0]["id"] == "truthful"
    assert result["bidders"][1]["id"] == "shaded"


def test_run_mixed_profile_comparison_applies_mixed_strategies():
    profiles = [
        {
            "id": "truthful",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        },
        {
            "id": "shaded",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_kwargs": {"shade_factor": 0.8},
        },
    ]

    result = run_mixed_profile_comparison(
        profiles,
        ctrs=[0.6, 0.3],
        rng=random.Random(123),
    )

    assert result["bidders"][0]["value"] == pytest.approx(10.0)
    assert result["bidders"][0]["bid"] == pytest.approx(10.0)
    assert result["bidders"][1]["value"] == pytest.approx(10.0)
    assert result["bidders"][1]["bid"] == pytest.approx(8.0)


def test_run_mixed_profile_comparison_returns_gsp_and_vcg_results():
    profiles = [
        {
            "id": "A",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        },
        {
            "id": "B",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_kwargs": {"shade_factor": 0.8},
        },
        {
            "id": "C",
            "min_value": 5.0,
            "max_value": 5.0,
            "strategy": truthful_bid,
        },
    ]

    result = run_mixed_profile_comparison(
        profiles,
        ctrs=[0.6, 0.3],
        rng=random.Random(123),
    )

    assert "gsp" in result["comparison"]
    assert "vcg" in result["comparison"]
    assert "difference" in result["comparison"]


def test_run_mixed_profile_comparison_computes_expected_gsp_revenue():
    profiles = [
        {
            "id": "A",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        },
        {
            "id": "B",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_kwargs": {"shade_factor": 0.8},
        },
        {
            "id": "C",
            "min_value": 5.0,
            "max_value": 5.0,
            "strategy": truthful_bid,
        },
    ]

    result = run_mixed_profile_comparison(
        profiles,
        ctrs=[0.6, 0.3],
        rng=random.Random(123),
    )

    assert result["comparison"]["gsp"]["revenue"] == pytest.approx(6.3)


def test_run_mixed_profile_comparison_returns_gsp_bidder_outcomes():
    profiles = [
        {
            "id": "A",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
            "strategy_name": "truthful",
        },
        {
            "id": "B",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_name": "shaded",
            "strategy_kwargs": {"shade_factor": 0.8},
        },
        {
            "id": "C",
            "min_value": 5.0,
            "max_value": 5.0,
            "strategy": truthful_bid,
            "strategy_name": "truthful",
        },
    ]

    result = run_mixed_profile_comparison(
        profiles,
        ctrs=[0.6, 0.3],
        rng=random.Random(123),
    )

    assert result["bidder_outcomes"]["A"]["utility"] == pytest.approx(1.2)
    assert result["bidder_outcomes"]["B"]["utility"] == pytest.approx(1.5)
    assert "C" not in result["bidder_outcomes"]


def test_run_mixed_profile_comparison_returns_gsp_strategy_outcomes():
    profiles = [
        {
            "id": "A",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
            "strategy_name": "truthful",
        },
        {
            "id": "B",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_name": "shaded",
            "strategy_kwargs": {"shade_factor": 0.8},
        },
        {
            "id": "C",
            "min_value": 5.0,
            "max_value": 5.0,
            "strategy": truthful_bid,
            "strategy_name": "truthful",
        },
    ]

    result = run_mixed_profile_comparison(
        profiles,
        ctrs=[0.6, 0.3],
        rng=random.Random(123),
    )

    assert result["strategy_outcomes"]["truthful"]["count"] == 2
    assert result["strategy_outcomes"]["truthful"]["total_utility"] == pytest.approx(
        1.2
    )
    assert result["strategy_outcomes"]["truthful"]["average_utility"] == pytest.approx(
        0.6
    )

    assert result["strategy_outcomes"]["shaded"]["count"] == 1
    assert result["strategy_outcomes"]["shaded"]["total_utility"] == pytest.approx(1.5)
    assert result["strategy_outcomes"]["shaded"]["average_utility"] == pytest.approx(
        1.5
    )

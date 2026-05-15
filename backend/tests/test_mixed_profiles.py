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

import random

import pytest

from auctioneer.simulation.statistical_runner import (
    run_repeated_comparisons_with_confidence,
)


def test_run_repeated_comparisons_with_confidence_returns_metadata():
    result = run_repeated_comparisons_with_confidence(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        num_resamples=20,
        confidence=0.8,
        rng=random.Random(123),
    )

    assert result["num_auctions"] == 5
    assert result["confidence"] == pytest.approx(0.8)
    assert result["num_resamples"] == 20


def test_run_repeated_comparisons_with_confidence_includes_all_metrics():
    result = run_repeated_comparisons_with_confidence(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        num_resamples=20,
        confidence=0.8,
        rng=random.Random(123),
    )

    for mechanism in ["gsp", "vcg", "difference"]:
        assert mechanism in result["metrics"]

        for metric in ["revenue", "welfare", "bidder_surplus"]:
            interval = result["metrics"][mechanism][metric]

            assert "mean" in interval
            assert "lower" in interval
            assert "upper" in interval
            assert interval["confidence"] == pytest.approx(0.8)
            assert interval["num_resamples"] == 20


def test_run_repeated_comparisons_with_confidence_is_deterministic_with_seeded_rng():
    first = run_repeated_comparisons_with_confidence(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        num_resamples=20,
        confidence=0.8,
        rng=random.Random(123),
    )
    second = run_repeated_comparisons_with_confidence(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        num_resamples=20,
        confidence=0.8,
        rng=random.Random(123),
    )

    assert first == second


def test_run_repeated_comparisons_with_confidence_rejects_zero_auctions():
    with pytest.raises(ValueError, match="num_auctions"):
        run_repeated_comparisons_with_confidence(
            num_auctions=0,
            num_bidders=3,
            ctrs=[0.6, 0.3],
            min_value=1.0,
            max_value=10.0,
        )


def test_run_repeated_comparisons_with_confidence_rejects_negative_num_bidders():
    with pytest.raises(ValueError, match="num_bidders"):
        run_repeated_comparisons_with_confidence(
            num_auctions=5,
            num_bidders=-1,
            ctrs=[0.6, 0.3],
            min_value=1.0,
            max_value=10.0,
        )


def test_run_repeated_comparisons_with_confidence_rejects_inverted_value_range():
    with pytest.raises(ValueError, match="min_value"):
        run_repeated_comparisons_with_confidence(
            num_auctions=5,
            num_bidders=3,
            ctrs=[0.6, 0.3],
            min_value=10.0,
            max_value=1.0,
        )

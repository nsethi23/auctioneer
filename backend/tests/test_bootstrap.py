import random

import pytest

from auctioneer.statistics.bootstrap import bootstrap_mean_confidence_interval


def test_bootstrap_mean_confidence_interval_returns_mean_and_bounds():
    result = bootstrap_mean_confidence_interval(
        values=[1.0, 2.0, 3.0, 4.0],
        num_resamples=100,
        confidence=0.8,
        rng=random.Random(123),
    )

    assert result["mean"] == pytest.approx(2.5)
    assert result["lower"] <= result["mean"] <= result["upper"]
    assert result["confidence"] == pytest.approx(0.8)
    assert result["num_resamples"] == 100


def test_bootstrap_mean_confidence_interval_is_deterministic_with_seeded_rng():
    first = bootstrap_mean_confidence_interval(
        values=[1.0, 2.0, 3.0, 4.0],
        num_resamples=100,
        confidence=0.8,
        rng=random.Random(123),
    )
    second = bootstrap_mean_confidence_interval(
        values=[1.0, 2.0, 3.0, 4.0],
        num_resamples=100,
        confidence=0.8,
        rng=random.Random(123),
    )

    assert first == second


def test_bootstrap_mean_confidence_interval_with_constant_values_has_constant_bounds():
    result = bootstrap_mean_confidence_interval(
        values=[5.0, 5.0, 5.0],
        num_resamples=50,
        rng=random.Random(123),
    )

    assert result["mean"] == pytest.approx(5.0)
    assert result["lower"] == pytest.approx(5.0)
    assert result["upper"] == pytest.approx(5.0)


def test_bootstrap_mean_confidence_interval_rejects_empty_values():
    with pytest.raises(ValueError, match="values"):
        bootstrap_mean_confidence_interval([])


def test_bootstrap_mean_confidence_interval_rejects_non_positive_resamples():
    with pytest.raises(ValueError, match="num_resamples"):
        bootstrap_mean_confidence_interval([1.0, 2.0], num_resamples=0)


def test_bootstrap_mean_confidence_interval_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="confidence"):
        bootstrap_mean_confidence_interval([1.0, 2.0], confidence=1.0)

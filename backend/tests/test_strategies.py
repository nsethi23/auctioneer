import pytest

from auctioneer.agents.strategies import shaded_bid, truthful_bid


def test_truthful_bid_returns_value_unchanged():
    assert truthful_bid(10.0) == pytest.approx(10.0)
    assert truthful_bid(7.5) == pytest.approx(7.5)
    assert truthful_bid(0.0) == pytest.approx(0.0)


def test_shaded_bid_multiplies_value_by_shade_factor():
    assert shaded_bid(10.0, 0.8) == pytest.approx(8.0)
    assert shaded_bid(7.5, 0.6) == pytest.approx(4.5)
    assert shaded_bid(12.0, 0.25) == pytest.approx(3.0)


def test_shaded_bid_with_factor_one_matches_truthful_bid():
    value = 10.0

    assert shaded_bid(value, 1.0) == pytest.approx(truthful_bid(value))


def test_shaded_bid_with_factor_zero_returns_zero():
    assert shaded_bid(10.0, 0.0) == pytest.approx(0.0)
    assert shaded_bid(7.5, 0.0) == pytest.approx(0.0)

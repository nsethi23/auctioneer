import pytest

from auctioneer.metrics.efficiency import (
    compute_optimal_welfare,
    compute_price_of_anarchy,
)


def test_compute_optimal_welfare_sorts_by_true_value_not_bid():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 1.0},
        {"id": "B", "value": 8.0, "bid": 100.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = compute_optimal_welfare(bidders, ctrs=[0.6, 0.3])

    assert result == pytest.approx(8.4)


def test_compute_optimal_welfare_ignores_bidders_without_slots():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = compute_optimal_welfare(bidders, ctrs=[0.6])

    assert result == pytest.approx(6.0)


def test_compute_price_of_anarchy_is_one_for_truthful_efficient_allocation():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = compute_price_of_anarchy(bidders, ctrs=[0.6, 0.3])

    assert result["optimal_welfare"] == pytest.approx(8.4)
    assert result["strategic_welfare"] == pytest.approx(8.4)
    assert result["price_of_anarchy"] == pytest.approx(1.0)
    assert result["welfare_loss"] == pytest.approx(0.0)


def test_compute_price_of_anarchy_detects_welfare_loss_from_distorted_bids():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 1.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = compute_price_of_anarchy(bidders, ctrs=[0.6, 0.3])

    assert result["optimal_welfare"] == pytest.approx(8.4)
    assert result["strategic_welfare"] == pytest.approx(6.3)
    assert result["price_of_anarchy"] == pytest.approx(8.4 / 6.3)
    assert result["welfare_loss"] == pytest.approx(2.1)


def test_compute_price_of_anarchy_returns_infinity_when_strategic_welfare_is_zero():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = compute_price_of_anarchy(bidders, ctrs=[])

    assert result["optimal_welfare"] == pytest.approx(0.0)
    assert result["strategic_welfare"] == pytest.approx(0.0)
    assert result["price_of_anarchy"] == float("inf")
    assert result["welfare_loss"] == pytest.approx(0.0)

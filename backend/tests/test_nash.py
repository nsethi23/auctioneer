import pytest

from auctioneer.agents.nash import check_gsp_nash_equilibrium


def test_check_gsp_nash_equilibrium_detects_profitable_deviation():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = check_gsp_nash_equilibrium(
        bidders=bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
    )

    assert result["is_equilibrium"] is False
    assert result["max_utility_gain"] == pytest.approx(0.3)
    assert result["deviations"] == [
        {
            "bidder_id": "A",
            "current_bid": 10.0,
            "best_bid": 6.0,
            "current_utility": pytest.approx(1.2),
            "best_utility": pytest.approx(1.5),
            "utility_gain": pytest.approx(0.3),
        }
    ]


def test_check_gsp_nash_equilibrium_returns_true_when_no_bidder_can_improve():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 6.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = check_gsp_nash_equilibrium(
        bidders=bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
    )

    assert result["is_equilibrium"] is True
    assert result["max_utility_gain"] == pytest.approx(0.0)
    assert result["deviations"] == []


def test_check_gsp_nash_equilibrium_uses_tolerance_for_tiny_gains():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = check_gsp_nash_equilibrium(
        bidders=bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
        tolerance=1.0,
    )

    assert result["is_equilibrium"] is True
    assert result["max_utility_gain"] == pytest.approx(0.3)
    assert result["deviations"] == []


def test_check_gsp_nash_equilibrium_rejects_empty_candidate_bids():
    with pytest.raises(ValueError, match="candidate_bids"):
        check_gsp_nash_equilibrium(
            bidders=[{"id": "A", "value": 10.0, "bid": 10.0}],
            ctrs=[0.6],
            candidate_bids=[],
        )

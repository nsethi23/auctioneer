import pytest

from auctioneer.agents.best_response import find_best_response_bid


def test_find_best_response_bid_returns_candidate_with_highest_utility():
    other_bidders = [
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = find_best_response_bid(
        bidder_id="A",
        value=10.0,
        other_bidders=other_bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
    )

    assert result["bid"] == pytest.approx(6.0)
    assert result["utility"] == pytest.approx(1.5)


def test_find_best_response_bid_returns_result_for_each_candidate():
    candidate_bids = [0.0, 5.0, 6.0, 8.0, 10.0]

    result = find_best_response_bid(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=candidate_bids,
    )

    assert len(result["results"]) == len(candidate_bids)
    assert [entry["bid"] for entry in result["results"]] == candidate_bids


def test_find_best_response_bid_assigns_zero_utility_when_bidder_loses():
    result = find_best_response_bid(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0],
    )

    assert result["bid"] == pytest.approx(0.0)
    assert result["utility"] == pytest.approx(0.0)
    assert result["results"] == [{"bid": 0.0, "utility": 0.0}]


def test_find_best_response_bid_keeps_first_bid_when_utilities_tie():
    result = find_best_response_bid(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0, 7.0],
    )

    assert result["bid"] == pytest.approx(6.0)
    assert result["utility"] == pytest.approx(1.5)


def test_find_best_response_bid_can_return_bid_below_private_value():
    result = find_best_response_bid(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0, 10.0],
    )

    assert result["bid"] < 10.0
    assert result["utility"] == pytest.approx(1.5)

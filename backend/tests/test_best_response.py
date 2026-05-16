import pytest

from auctioneer.agents.best_response import (
    find_best_response_bid,
    generate_best_response_curve,
)


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


def test_find_best_response_bid_rejects_empty_candidate_bids():
    with pytest.raises(ValueError, match="candidate_bids"):
        find_best_response_bid(
            bidder_id="A",
            value=10.0,
            other_bidders=[
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            ctrs=[0.6, 0.3],
            candidate_bids=[],
        )


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


def test_generate_best_response_curve_returns_entry_for_each_value():
    values = [6.0, 10.0]

    result = generate_best_response_curve(
        bidder_id="A",
        values=values,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
    )

    assert len(result) == len(values)
    assert [entry["value"] for entry in result] == values


def test_generate_best_response_curve_uses_clear_best_response_keys():
    result = generate_best_response_curve(
        bidder_id="A",
        values=[10.0],
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
    )

    assert result[0]["value"] == pytest.approx(10.0)
    assert result[0]["best_bid"] == pytest.approx(6.0)
    assert result[0]["best_utility"] == pytest.approx(1.5)
    assert "results" in result[0]


def test_generate_best_response_curve_can_show_best_bid_changes_by_value():
    result = generate_best_response_curve(
        bidder_id="A",
        values=[4.0, 10.0],
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
    )

    assert result[0]["best_bid"] == pytest.approx(0.0)
    assert result[0]["best_utility"] == pytest.approx(0.0)
    assert result[1]["best_bid"] == pytest.approx(6.0)
    assert result[1]["best_utility"] == pytest.approx(1.5)

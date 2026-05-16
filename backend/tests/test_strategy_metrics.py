import pytest

from auctioneer.metrics.strategies import summarize_strategy_outcomes


def test_summarize_strategy_outcomes_groups_utilities_by_strategy():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0, "strategy": "truthful"},
        {"id": "B", "value": 8.0, "bid": 6.4, "strategy": "shaded"},
        {"id": "C", "value": 5.0, "bid": 5.0, "strategy": "truthful"},
    ]
    auction_result = {
        "allocations": [
            {
                "bidder_id": "A",
                "slot": 0,
                "ctr": 0.6,
                "value": 10.0,
                "bid": 10.0,
                "payment": 3.84,
                "utility": 2.16,
            },
            {
                "bidder_id": "B",
                "slot": 1,
                "ctr": 0.3,
                "value": 8.0,
                "bid": 6.4,
                "payment": 1.5,
                "utility": 0.9,
            },
        ]
    }

    result = summarize_strategy_outcomes(bidders, auction_result)

    assert result["truthful"]["count"] == 2
    assert result["truthful"]["total_utility"] == pytest.approx(2.16)
    assert result["truthful"]["average_utility"] == pytest.approx(1.08)

    assert result["shaded"]["count"] == 1
    assert result["shaded"]["total_utility"] == pytest.approx(0.9)
    assert result["shaded"]["average_utility"] == pytest.approx(0.9)


def test_summarize_strategy_outcomes_counts_losing_bidders_with_zero_utility():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0, "strategy": "truthful"},
        {"id": "B", "value": 8.0, "bid": 8.0, "strategy": "truthful"},
    ]
    auction_result = {
        "allocations": [
            {
                "bidder_id": "A",
                "slot": 0,
                "ctr": 0.6,
                "value": 10.0,
                "bid": 10.0,
                "payment": 4.8,
                "utility": 1.2,
            }
        ]
    }

    result = summarize_strategy_outcomes(bidders, auction_result)

    assert result["truthful"]["count"] == 2
    assert result["truthful"]["total_utility"] == pytest.approx(1.2)
    assert result["truthful"]["average_utility"] == pytest.approx(0.6)


def test_summarize_strategy_outcomes_uses_unknown_for_missing_strategy_label():
    bidders = [{"id": "A", "value": 10.0, "bid": 10.0}]
    auction_result = {
        "allocations": [
            {
                "bidder_id": "A",
                "slot": 0,
                "ctr": 0.6,
                "value": 10.0,
                "bid": 10.0,
                "payment": 4.8,
                "utility": 1.2,
            }
        ]
    }

    result = summarize_strategy_outcomes(bidders, auction_result)

    assert result["unknown"]["count"] == 1
    assert result["unknown"]["total_utility"] == pytest.approx(1.2)
    assert result["unknown"]["average_utility"] == pytest.approx(1.2)


def test_summarize_strategy_outcomes_with_no_bidders_returns_empty_dict():
    result = summarize_strategy_outcomes([], {"allocations": []})

    assert result == {}

import pytest

from auctioneer.metrics.bidders import summarize_bidder_outcomes


def test_summarize_bidder_outcomes_keys_results_by_bidder_id():
    auction_result = {
        "allocations": [
            {
                "bidder_id": "A",
                "slot": 0,
                "ctr": 0.6,
                "value": 10.0,
                "bid": 8.0,
                "payment": 4.5,
                "utility": 1.5,
            },
            {
                "bidder_id": "B",
                "slot": 1,
                "ctr": 0.3,
                "value": 9.0,
                "bid": 9.0,
                "payment": 2.0,
                "utility": 0.7,
            },
        ],
        "revenue": 6.5,
        "welfare": 8.7,
        "bidder_surplus": 2.2,
    }

    result = summarize_bidder_outcomes(auction_result)

    assert set(result) == {"A", "B"}


def test_summarize_bidder_outcomes_preserves_bidder_metrics():
    auction_result = {
        "allocations": [
            {
                "bidder_id": "A",
                "slot": 0,
                "ctr": 0.6,
                "value": 10.0,
                "bid": 8.0,
                "payment": 4.5,
                "utility": 1.5,
            }
        ]
    }

    result = summarize_bidder_outcomes(auction_result)

    assert result["A"]["slot"] == 0
    assert result["A"]["ctr"] == pytest.approx(0.6)
    assert result["A"]["value"] == pytest.approx(10.0)
    assert result["A"]["bid"] == pytest.approx(8.0)
    assert result["A"]["payment"] == pytest.approx(4.5)
    assert result["A"]["utility"] == pytest.approx(1.5)


def test_summarize_bidder_outcomes_with_no_allocations_returns_empty_dict():
    result = summarize_bidder_outcomes({"allocations": []})

    assert result == {}


def test_summarize_bidder_outcomes_ignores_auction_level_metrics():
    auction_result = {
        "allocations": [
            {
                "bidder_id": "A",
                "slot": 0,
                "ctr": 0.6,
                "value": 10.0,
                "bid": 8.0,
                "payment": 4.5,
                "utility": 1.5,
            }
        ],
        "revenue": 4.5,
        "welfare": 6.0,
        "bidder_surplus": 1.5,
    }

    result = summarize_bidder_outcomes(auction_result)

    assert "revenue" not in result["A"]
    assert "welfare" not in result["A"]
    assert "bidder_surplus" not in result["A"]

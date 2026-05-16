import pytest

from auctioneer.metrics.allocations import get_bidder_utility


def test_get_bidder_utility_returns_winning_bidder_utility():
    auction_result = {
        "allocations": [
            {"bidder_id": "A", "utility": 1.2},
            {"bidder_id": "B", "utility": 0.9},
        ]
    }

    assert get_bidder_utility(auction_result, "A") == pytest.approx(1.2)
    assert get_bidder_utility(auction_result, "B") == pytest.approx(0.9)


def test_get_bidder_utility_returns_zero_for_losing_bidder():
    auction_result = {
        "allocations": [
            {"bidder_id": "A", "utility": 1.2},
        ]
    }

    assert get_bidder_utility(auction_result, "C") == pytest.approx(0.0)

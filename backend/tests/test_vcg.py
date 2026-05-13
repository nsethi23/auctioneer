import pytest

from auctioneer.auctions.vcg import run_vcg_auction


def test_run_vcg_auction_three_bidders_two_slots():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    ctrs = [0.6, 0.3]

    result = run_vcg_auction(bidders, ctrs)

    assert len(result["allocations"]) == 2

    first_allocation = result["allocations"][0]
    second_allocation = result["allocations"][1]

    assert first_allocation["bidder_id"] == "A"
    assert first_allocation["slot"] == 0
    assert first_allocation["ctr"] == pytest.approx(0.6)
    assert first_allocation["value"] == pytest.approx(10.0)
    assert first_allocation["bid"] == pytest.approx(10.0)
    assert first_allocation["payment"] == pytest.approx(3.9)
    assert first_allocation["utility"] == pytest.approx(2.1)

    assert second_allocation["bidder_id"] == "B"
    assert second_allocation["slot"] == 1
    assert second_allocation["ctr"] == pytest.approx(0.3)
    assert second_allocation["value"] == pytest.approx(8.0)
    assert second_allocation["bid"] == pytest.approx(8.0)
    assert second_allocation["payment"] == pytest.approx(1.5)
    assert second_allocation["utility"] == pytest.approx(0.9)

    assert result["revenue"] == pytest.approx(5.4)
    assert result["welfare"] == pytest.approx(8.4)
    assert result["bidder_surplus"] == pytest.approx(3.0)

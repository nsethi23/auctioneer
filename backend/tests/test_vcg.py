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


def test_run_vcg_auction_with_zero_slots():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = run_vcg_auction(bidders, [])

    assert result["allocations"] == []
    assert result["revenue"] == pytest.approx(0.0)
    assert result["welfare"] == pytest.approx(0.0)
    assert result["bidder_surplus"] == pytest.approx(0.0)


def test_run_vcg_auction_with_one_bidder():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 7.0},
    ]

    result = run_vcg_auction(bidders, [0.5])

    assert len(result["allocations"]) == 1

    allocation = result["allocations"][0]

    assert allocation["bidder_id"] == "A"
    assert allocation["slot"] == 0
    assert allocation["payment"] == pytest.approx(0.0)
    assert allocation["utility"] == pytest.approx(5.0)

    assert result["revenue"] == pytest.approx(0.0)
    assert result["welfare"] == pytest.approx(5.0)
    assert result["bidder_surplus"] == pytest.approx(5.0)


def test_run_vcg_auction_sorts_bidders_by_bid():
    bidders = [
        {"id": "C", "value": 5.0, "bid": 5.0},
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = run_vcg_auction(bidders, [0.6, 0.3])

    assert result["allocations"][0]["bidder_id"] == "A"
    assert result["allocations"][1]["bidder_id"] == "B"


def test_run_vcg_auction_with_more_slots_than_bidders():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = run_vcg_auction(bidders, [0.6, 0.3, 0.1])

    assert len(result["allocations"]) == 2
    assert result["allocations"][0]["payment"] == pytest.approx(2.4)
    assert result["allocations"][1]["payment"] == pytest.approx(0.0)

    assert result["revenue"] == pytest.approx(2.4)
    assert result["welfare"] == pytest.approx(8.4)
    assert result["bidder_surplus"] == pytest.approx(6.0)

import pytest

from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.models import Bidder


def test_run_gsp_auction_three_bidders_two_slots():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    ctrs = [0.6, 0.3]

    result = run_gsp_auction(bidders, ctrs)

    assert len(result["allocations"]) == 2

    first_allocation = result["allocations"][0]
    second_allocation = result["allocations"][1]

    assert first_allocation["bidder_id"] == "A"
    assert first_allocation["slot"] == 0
    assert first_allocation["ctr"] == pytest.approx(0.6)
    assert first_allocation["value"] == pytest.approx(10.0)
    assert first_allocation["bid"] == pytest.approx(10.0)
    assert first_allocation["payment"] == pytest.approx(4.8)
    assert first_allocation["utility"] == pytest.approx(1.2)

    assert second_allocation["bidder_id"] == "B"
    assert second_allocation["slot"] == 1
    assert second_allocation["ctr"] == pytest.approx(0.3)
    assert second_allocation["value"] == pytest.approx(8.0)
    assert second_allocation["bid"] == pytest.approx(8.0)
    assert second_allocation["payment"] == pytest.approx(1.5)
    assert second_allocation["utility"] == pytest.approx(0.9)

    assert result["revenue"] == pytest.approx(6.3)
    assert result["welfare"] == pytest.approx(8.4)
    assert result["bidder_surplus"] == pytest.approx(2.1)


def test_run_gsp_auction_with_zero_slots():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = run_gsp_auction(bidders, [])

    assert result["allocations"] == []
    assert result["revenue"] == pytest.approx(0.0)
    assert result["welfare"] == pytest.approx(0.0)
    assert result["bidder_surplus"] == pytest.approx(0.0)


def test_run_gsp_auction_with_one_bidder():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 7.0},
    ]

    result = run_gsp_auction(bidders, [0.5])

    assert len(result["allocations"]) == 1

    allocation = result["allocations"][0]

    assert allocation["bidder_id"] == "A"
    assert allocation["slot"] == 0
    assert allocation["payment"] == pytest.approx(0.0)
    assert allocation["utility"] == pytest.approx(5.0)

    assert result["revenue"] == pytest.approx(0.0)
    assert result["welfare"] == pytest.approx(5.0)
    assert result["bidder_surplus"] == pytest.approx(5.0)


def test_run_gsp_auction_sorts_bidders_by_bid():
    bidders = [
        {"id": "C", "value": 5.0, "bid": 5.0},
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3])

    assert result["allocations"][0]["bidder_id"] == "A"
    assert result["allocations"][1]["bidder_id"] == "B"


def test_run_gsp_auction_with_more_slots_than_bidders():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3, 0.1])

    assert len(result["allocations"]) == 2
    assert result["allocations"][0]["payment"] == pytest.approx(4.8)
    assert result["allocations"][1]["payment"] == pytest.approx(0.0)

    assert result["revenue"] == pytest.approx(4.8)
    assert result["welfare"] == pytest.approx(8.4)
    assert result["bidder_surplus"] == pytest.approx(3.6)


def test_run_gsp_auction_accepts_bidder_models():
    bidders = [
        Bidder(id="A", value=10.0, bid=10.0),
        Bidder(id="B", value=8.0, bid=8.0),
        Bidder(id="C", value=5.0, bid=5.0),
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3])

    assert result["allocations"][0]["bidder_id"] == "A"
    assert result["allocations"][1]["bidder_id"] == "B"
    assert result["revenue"] == pytest.approx(6.3)
    assert result["welfare"] == pytest.approx(8.4)


def test_run_gsp_auction_reserve_filters_out_low_bidders():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 5.0},
        {"id": "C", "value": 7.0, "bid": 4.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3], reserve_price=6.0)

    assert len(result["allocations"]) == 1
    assert result["allocations"][0]["bidder_id"] == "A"


def test_run_gsp_auction_single_eligible_winner_pays_reserve():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 5.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3], reserve_price=6.0)

    assert result["allocations"][0]["payment"] == pytest.approx(3.6)
    assert result["allocations"][0]["utility"] == pytest.approx(2.4)
    assert result["revenue"] == pytest.approx(3.6)
    assert result["welfare"] == pytest.approx(6.0)
    assert result["bidder_surplus"] == pytest.approx(2.4)


def test_run_gsp_auction_reserve_sets_minimum_price_with_multiple_winners():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3], reserve_price=6.0)

    assert result["allocations"][0]["payment"] == pytest.approx(4.8)
    assert result["allocations"][1]["payment"] == pytest.approx(1.8)
    assert result["revenue"] == pytest.approx(6.6)


def test_run_gsp_auction_reserve_can_leave_all_slots_unfilled():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 5.0},
        {"id": "B", "value": 8.0, "bid": 4.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3], reserve_price=6.0)

    assert result["allocations"] == []
    assert result["revenue"] == pytest.approx(0.0)
    assert result["welfare"] == pytest.approx(0.0)
    assert result["bidder_surplus"] == pytest.approx(0.0)


def test_run_gsp_auction_default_reserve_keeps_original_behavior():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3])

    assert result["revenue"] == pytest.approx(6.3)
    assert result["welfare"] == pytest.approx(8.4)
    assert result["bidder_surplus"] == pytest.approx(2.1)


def test_run_gsp_auction_ignores_quality_scores_by_default():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0, "quality_score": 1.0},
        {"id": "B", "value": 8.0, "bid": 7.0, "quality_score": 2.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3])

    assert result["allocations"][0]["bidder_id"] == "A"
    assert result["allocations"][1]["bidder_id"] == "B"


def test_run_gsp_auction_quality_scores_can_change_ranking():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0, "quality_score": 1.0},
        {"id": "B", "value": 8.0, "bid": 7.0, "quality_score": 2.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3], use_quality_scores=True)

    assert result["allocations"][0]["bidder_id"] == "B"
    assert result["allocations"][0]["rank_score"] == pytest.approx(14.0)
    assert result["allocations"][0]["payment"] == pytest.approx(3.0)
    assert result["allocations"][1]["bidder_id"] == "A"


def test_run_gsp_auction_missing_quality_score_defaults_to_one():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 8.0, "quality_score": 2.0},
        {"id": "B", "value": 8.0, "bid": 9.0},
    ]

    result = run_gsp_auction(bidders, [0.6, 0.3], use_quality_scores=True)

    assert result["allocations"][0]["bidder_id"] == "A"
    assert result["allocations"][0]["quality_score"] == pytest.approx(2.0)
    assert result["allocations"][0]["rank_score"] == pytest.approx(16.0)
    assert result["allocations"][0]["payment"] == pytest.approx(2.7)
    assert result["allocations"][1]["quality_score"] == pytest.approx(1.0)


def test_run_gsp_auction_quality_score_pricing_respects_reserve():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 8.0, "quality_score": 2.0},
        {"id": "B", "value": 8.0, "bid": 7.0, "quality_score": 1.0},
    ]

    result = run_gsp_auction(
        bidders,
        [0.6, 0.3],
        reserve_price=6.0,
        use_quality_scores=True,
    )

    assert result["allocations"][0]["bidder_id"] == "A"
    assert result["allocations"][0]["payment"] == pytest.approx(3.6)
    assert result["allocations"][1]["bidder_id"] == "B"
    assert result["allocations"][1]["payment"] == pytest.approx(1.8)


def test_run_gsp_auction_reserve_still_filters_by_bid_with_quality_scores():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 6.0, "quality_score": 1.0},
        {"id": "B", "value": 8.0, "bid": 5.0, "quality_score": 10.0},
    ]

    result = run_gsp_auction(
        bidders,
        [0.6, 0.3],
        reserve_price=6.0,
        use_quality_scores=True,
    )

    assert len(result["allocations"]) == 1
    assert result["allocations"][0]["bidder_id"] == "A"


def test_run_gsp_auction_rejects_non_positive_quality_score_when_enabled():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0, "quality_score": 0.0},
    ]

    with pytest.raises(ValueError, match="quality_score"):
        run_gsp_auction(bidders, [0.6], use_quality_scores=True)

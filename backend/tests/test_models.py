import pytest

from auctioneer.models import (
    Allocation,
    Bidder,
    allocation_to_dict,
    bidder_to_dict,
    normalize_bidder,
)


def test_bidder_stores_core_fields():
    bidder = Bidder(id="A", value=10.0, bid=8.0)

    assert bidder.id == "A"
    assert bidder.value == pytest.approx(10.0)
    assert bidder.bid == pytest.approx(8.0)
    assert bidder.strategy is None


def test_bidder_can_store_strategy_label():
    bidder = Bidder(id="A", value=10.0, bid=8.0, strategy="shaded")

    assert bidder.strategy == "shaded"


def test_allocation_stores_auction_outcome_fields():
    allocation = Allocation(
        bidder_id="A",
        slot=0,
        ctr=0.6,
        value=10.0,
        bid=8.0,
        payment=4.5,
        utility=1.5,
    )

    assert allocation.bidder_id == "A"
    assert allocation.slot == 0
    assert allocation.ctr == pytest.approx(0.6)
    assert allocation.value == pytest.approx(10.0)
    assert allocation.bid == pytest.approx(8.0)
    assert allocation.payment == pytest.approx(4.5)
    assert allocation.utility == pytest.approx(1.5)


def test_bidder_to_dict_omits_missing_strategy():
    bidder = Bidder(id="A", value=10.0, bid=8.0)

    assert bidder_to_dict(bidder) == {
        "id": "A",
        "value": 10.0,
        "bid": 8.0,
    }


def test_bidder_to_dict_includes_strategy_when_present():
    bidder = Bidder(id="A", value=10.0, bid=8.0, strategy="shaded")

    assert bidder_to_dict(bidder) == {
        "id": "A",
        "value": 10.0,
        "bid": 8.0,
        "strategy": "shaded",
    }


def test_normalize_bidder_converts_bidder_model_to_dict():
    bidder = Bidder(id="A", value=10.0, bid=8.0, strategy="shaded")

    assert normalize_bidder(bidder) == {
        "id": "A",
        "value": 10.0,
        "bid": 8.0,
        "strategy": "shaded",
    }


def test_normalize_bidder_leaves_existing_dict_unchanged():
    bidder = {"id": "A", "value": 10.0, "bid": 8.0}

    assert normalize_bidder(bidder) is bidder


def test_allocation_to_dict_preserves_all_fields():
    allocation = Allocation(
        bidder_id="A",
        slot=0,
        ctr=0.6,
        value=10.0,
        bid=8.0,
        payment=4.5,
        utility=1.5,
    )

    assert allocation_to_dict(allocation) == {
        "bidder_id": "A",
        "slot": 0,
        "ctr": 0.6,
        "value": 10.0,
        "bid": 8.0,
        "payment": 4.5,
        "utility": 1.5,
    }

from dataclasses import dataclass


@dataclass
class Bidder:
    id: str
    value: float
    bid: float
    strategy: str | None = None


@dataclass
class Allocation:
    bidder_id: str
    slot: int
    ctr: float
    value: float
    bid: float
    payment: float
    utility: float


def bidder_to_dict(bidder):
    result = {
        "id": bidder.id,
        "value": bidder.value,
        "bid": bidder.bid,
    }

    if bidder.strategy is not None:
        result["strategy"] = bidder.strategy

    return result


def normalize_bidder(bidder):
    if isinstance(bidder, Bidder):
        return bidder_to_dict(bidder)

    return bidder


def allocation_to_dict(allocation):
    return {
        "bidder_id": allocation.bidder_id,
        "slot": allocation.slot,
        "ctr": allocation.ctr,
        "value": allocation.value,
        "bid": allocation.bid,
        "payment": allocation.payment,
        "utility": allocation.utility,
    }

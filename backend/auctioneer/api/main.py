from fastapi import FastAPI
from pydantic import BaseModel

from auctioneer.agents.nash import check_gsp_nash_equilibrium
from auctioneer.simulation.comparison import compare_gsp_and_vcg

app = FastAPI(title="Auctioneer API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


class BidderInput(BaseModel):
    id: str
    value: float
    bid: float
    quality_score: float | None = None
    strategy: str | None = None


class AuctionCompareRequest(BaseModel):
    bidders: list[BidderInput]
    ctrs: list[float]


class NashCheckRequest(BaseModel):
    bidders: list[BidderInput]
    ctrs: list[float]
    candidate_bids: list[float]
    tolerance: float = 1e-9


def bidder_input_to_dict(bidder):
    bidder_dict = {
        "id": bidder.id,
        "value": bidder.value,
        "bid": bidder.bid,
    }

    if bidder.quality_score is not None:
        bidder_dict["quality_score"] = bidder.quality_score

    if bidder.strategy is not None:
        bidder_dict["strategy"] = bidder.strategy

    return bidder_dict


@app.post("/auction/compare")
def compare_auction(request: AuctionCompareRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]
    return compare_gsp_and_vcg(bidders, request.ctrs)


@app.post("/nash/check")
def check_nash(request: NashCheckRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]

    return check_gsp_nash_equilibrium(
        bidders=bidders,
        ctrs=request.ctrs,
        candidate_bids=request.candidate_bids,
        tolerance=request.tolerance,
    )

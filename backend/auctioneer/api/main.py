from fastapi import FastAPI
from pydantic import BaseModel

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


@app.post("/auction/compare")
def compare_auction(request: AuctionCompareRequest):
    bidders = []

    for bidder in request.bidders:
        bidder_dict = {
            "id": bidder.id,
            "value": bidder.value,
            "bid": bidder.bid,
        }

        if bidder.quality_score is not None:
            bidder_dict["quality_score"] = bidder.quality_score

        if bidder.strategy is not None:
            bidder_dict["strategy"] = bidder.strategy

        bidders.append(bidder_dict)

    return compare_gsp_and_vcg(bidders, request.ctrs)

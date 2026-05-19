from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auctioneer.agents.nash import check_gsp_nash_equilibrium
from auctioneer.agents.q_learning_evaluation import track_q_learning_convergence
from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.auctions.vcg import run_vcg_auction
from auctioneer.metrics.efficiency import compute_price_of_anarchy
from auctioneer.simulation.comparison import compare_gsp_and_vcg
from auctioneer.simulation.statistical_runner import (
    run_repeated_comparisons_with_confidence,
)

app = FastAPI(title="Auctioneer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class GSPAuctionRequest(BaseModel):
    bidders: list[BidderInput]
    ctrs: list[float]
    reserve_price: float = 0.0
    use_quality_scores: bool = False


class VCGAuctionRequest(BaseModel):
    bidders: list[BidderInput]
    ctrs: list[float]
    reserve_price: float = 0.0


class PriceOfAnarchyRequest(BaseModel):
    bidders: list[BidderInput]
    ctrs: list[float]


class NashCheckRequest(BaseModel):
    bidders: list[BidderInput]
    ctrs: list[float]
    candidate_bids: list[float]
    tolerance: float = 1e-9


class RLConvergenceRequest(BaseModel):
    bidder_id: str
    value: float
    other_bidders: list[BidderInput]
    ctrs: list[float]
    candidate_bids: list[float]
    num_episodes: int
    checkpoint_interval: int
    learning_rate: float = 0.1
    discount_factor: float = 0.0
    epsilon: float = 0.1


class StatisticalSimulationRequest(BaseModel):
    num_auctions: int
    num_bidders: int
    ctrs: list[float]
    min_value: float
    max_value: float
    num_resamples: int = 1000
    confidence: float = 0.95


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


@app.post("/auction/gsp")
def run_gsp(request: GSPAuctionRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]

    return run_gsp_auction(
        bidders=bidders,
        ctrs=request.ctrs,
        reserve_price=request.reserve_price,
        use_quality_scores=request.use_quality_scores,
    )


@app.post("/auction/vcg")
def run_vcg(request: VCGAuctionRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]

    return run_vcg_auction(
        bidders=bidders,
        ctrs=request.ctrs,
        reserve_price=request.reserve_price,
    )


@app.post("/metrics/price-of-anarchy")
def compute_price_of_anarchy_metric(request: PriceOfAnarchyRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]
    return compute_price_of_anarchy(bidders, request.ctrs)


@app.post("/nash/check")
def check_nash(request: NashCheckRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]

    return check_gsp_nash_equilibrium(
        bidders=bidders,
        ctrs=request.ctrs,
        candidate_bids=request.candidate_bids,
        tolerance=request.tolerance,
    )


@app.post("/rl/convergence")
def track_rl_convergence(request: RLConvergenceRequest):
    other_bidders = [bidder_input_to_dict(bidder) for bidder in request.other_bidders]

    return track_q_learning_convergence(
        bidder_id=request.bidder_id,
        value=request.value,
        other_bidders=other_bidders,
        ctrs=request.ctrs,
        candidate_bids=request.candidate_bids,
        num_episodes=request.num_episodes,
        checkpoint_interval=request.checkpoint_interval,
        learning_rate=request.learning_rate,
        discount_factor=request.discount_factor,
        epsilon=request.epsilon,
    )


@app.post("/simulation/statistical")
def run_statistical_simulation(request: StatisticalSimulationRequest):
    return run_repeated_comparisons_with_confidence(
        num_auctions=request.num_auctions,
        num_bidders=request.num_bidders,
        ctrs=request.ctrs,
        min_value=request.min_value,
        max_value=request.max_value,
        num_resamples=request.num_resamples,
        confidence=request.confidence,
    )

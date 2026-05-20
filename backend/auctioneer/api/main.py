from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auctioneer.agents.best_response import (
    find_best_response_bid,
    generate_best_response_curve,
)
from auctioneer.agents.nash import check_gsp_nash_equilibrium
from auctioneer.agents.exp3_evaluation import track_exp3_convergence
from auctioneer.agents.strategies import shaded_bid, truthful_bid
from auctioneer.agents.multi_agent_q_learning import train_multi_agent_q_learning
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
        "https://auctioneer-five.vercel.app",
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


class BestResponseRequest(BaseModel):
    bidder_id: str
    bidders: list[BidderInput]
    ctrs: list[float]
    candidate_bids: list[float]


class BestResponseCurveRequest(BaseModel):
    bidder_id: str
    bidders: list[BidderInput]
    ctrs: list[float]
    values: list[float]
    candidate_bids: list[float]


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


class EXP3ConvergenceRequest(BaseModel):
    bidder_id: str
    value: float
    other_bidders: list[BidderInput]
    ctrs: list[float]
    candidate_bids: list[float]
    num_episodes: int
    checkpoint_interval: int
    gamma: float = 0.1


class MultiAgentRLRequest(BaseModel):
    bidder_specs: list[BidderInput]
    ctrs: list[float]
    candidate_bids: list[float]
    num_episodes: int
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
    distribution: str = "uniform"


class StrategyComparisonRequest(BaseModel):
    num_auctions: int
    num_bidders: int
    ctrs: list[float]
    min_value: float
    max_value: float
    shade_factor: float = 0.7
    num_resamples: int = 1000
    confidence: float = 0.95
    distribution: str = "uniform"


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


@app.post("/best-response")
def compute_best_response(request: BestResponseRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]
    target_bidder = next(
        (bidder for bidder in bidders if bidder["id"] == request.bidder_id),
        None,
    )

    if target_bidder is None:
        raise HTTPException(
            status_code=400,
            detail="bidder_id must match one of the bidders",
        )

    other_bidders = [bidder for bidder in bidders if bidder["id"] != request.bidder_id]

    return find_best_response_bid(
        bidder_id=target_bidder["id"],
        value=target_bidder["value"],
        other_bidders=other_bidders,
        ctrs=request.ctrs,
        candidate_bids=request.candidate_bids,
    )


@app.post("/best-response/curve")
def compute_best_response_curve(request: BestResponseCurveRequest):
    bidders = [bidder_input_to_dict(bidder) for bidder in request.bidders]
    target_bidder = next(
        (bidder for bidder in bidders if bidder["id"] == request.bidder_id),
        None,
    )

    if target_bidder is None:
        raise HTTPException(
            status_code=400,
            detail="bidder_id must match one of the bidders",
        )

    other_bidders = [bidder for bidder in bidders if bidder["id"] != request.bidder_id]

    return {
        "bidder_id": request.bidder_id,
        "values": request.values,
        "candidate_bids": request.candidate_bids,
        "curve": generate_best_response_curve(
            bidder_id=target_bidder["id"],
            values=request.values,
            other_bidders=other_bidders,
            ctrs=request.ctrs,
            candidate_bids=request.candidate_bids,
        ),
    }


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
    try:
        return run_repeated_comparisons_with_confidence(
            num_auctions=request.num_auctions,
            num_bidders=request.num_bidders,
            ctrs=request.ctrs,
            min_value=request.min_value,
            max_value=request.max_value,
            num_resamples=request.num_resamples,
            confidence=request.confidence,
            distribution=request.distribution,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/rl/exp3")
def track_exp3_convergence_endpoint(request: EXP3ConvergenceRequest):
    other_bidders = [bidder_input_to_dict(bidder) for bidder in request.other_bidders]
    try:
        return track_exp3_convergence(
            bidder_id=request.bidder_id,
            value=request.value,
            other_bidders=other_bidders,
            ctrs=request.ctrs,
            candidate_bids=request.candidate_bids,
            num_episodes=request.num_episodes,
            checkpoint_interval=request.checkpoint_interval,
            gamma=request.gamma,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/rl/multi-agent")
def train_multi_agent_rl(request: MultiAgentRLRequest):
    bidder_specs = [{"id": b.id, "value": b.value} for b in request.bidder_specs]
    try:
        result = train_multi_agent_q_learning(
            bidder_specs=bidder_specs,
            ctrs=request.ctrs,
            candidate_bids=request.candidate_bids,
            num_episodes=request.num_episodes,
            learning_rate=request.learning_rate,
            discount_factor=request.discount_factor,
            epsilon=request.epsilon,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"history": result["history"]}


@app.post("/simulation/strategy-comparison")
def compare_strategy_simulation(request: StrategyComparisonRequest):
    # Use a shared seed so both profiles face the same randomly-drawn markets.
    # This isolates the effect of strategy from market variance.
    import random as _random

    seed = _random.randint(0, 2**32 - 1)

    try:
        truthful = run_repeated_comparisons_with_confidence(
            num_auctions=request.num_auctions,
            num_bidders=request.num_bidders,
            ctrs=request.ctrs,
            min_value=request.min_value,
            max_value=request.max_value,
            num_resamples=request.num_resamples,
            confidence=request.confidence,
            distribution=request.distribution,
            strategy=truthful_bid,
            rng=_random.Random(seed),
        )
        shaded = run_repeated_comparisons_with_confidence(
            num_auctions=request.num_auctions,
            num_bidders=request.num_bidders,
            ctrs=request.ctrs,
            min_value=request.min_value,
            max_value=request.max_value,
            num_resamples=request.num_resamples,
            confidence=request.confidence,
            distribution=request.distribution,
            strategy=shaded_bid,
            strategy_kwargs={"shade_factor": request.shade_factor},
            rng=_random.Random(seed),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "truthful": truthful["metrics"],
        "shaded": shaded["metrics"],
        "shade_factor": request.shade_factor,
        "num_auctions": request.num_auctions,
        "confidence": request.confidence,
        "num_resamples": request.num_resamples,
    }

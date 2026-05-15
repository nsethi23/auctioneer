import random

from auctioneer.agents.strategies import shaded_bid, truthful_bid
from auctioneer.simulation.runner import run_repeated_comparisons


def compare_truthful_and_shaded(
    num_auctions,
    num_bidders,
    ctrs,
    min_value,
    max_value,
    shade_factor,
    seed=None,
):
    # Use matched random streams so both profiles face the same private values.
    truthful_rng = random.Random(seed)
    shaded_rng = random.Random(seed)

    # Baseline: bidders report private values directly.
    truthful_result = run_repeated_comparisons(
        num_auctions=num_auctions,
        num_bidders=num_bidders,
        ctrs=ctrs,
        min_value=min_value,
        max_value=max_value,
        rng=truthful_rng,
        strategy=truthful_bid,
    )

    # Counterfactual: same markets, but bidders shade bids below value.
    shaded_result = run_repeated_comparisons(
        num_auctions=num_auctions,
        num_bidders=num_bidders,
        ctrs=ctrs,
        min_value=min_value,
        max_value=max_value,
        rng=shaded_rng,
        strategy=shaded_bid,
        strategy_kwargs={"shade_factor": shade_factor},
    )

    # Differences use shaded minus truthful, isolating the effect of bid shading.
    return {
        "truthful": truthful_result,
        "shaded": shaded_result,
        "difference": {
            "gsp": {
                "revenue": (
                    shaded_result["averages"]["gsp"]["revenue"]
                    - truthful_result["averages"]["gsp"]["revenue"]
                ),
                "welfare": (
                    shaded_result["averages"]["gsp"]["welfare"]
                    - truthful_result["averages"]["gsp"]["welfare"]
                ),
                "bidder_surplus": (
                    shaded_result["averages"]["gsp"]["bidder_surplus"]
                    - truthful_result["averages"]["gsp"]["bidder_surplus"]
                ),
            },
            "vcg": {
                "revenue": (
                    shaded_result["averages"]["vcg"]["revenue"]
                    - truthful_result["averages"]["vcg"]["revenue"]
                ),
                "welfare": (
                    shaded_result["averages"]["vcg"]["welfare"]
                    - truthful_result["averages"]["vcg"]["welfare"]
                ),
                "bidder_surplus": (
                    shaded_result["averages"]["vcg"]["bidder_surplus"]
                    - truthful_result["averages"]["vcg"]["bidder_surplus"]
                ),
            },
        },
    }

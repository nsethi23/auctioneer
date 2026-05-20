import random

from auctioneer.simulation.comparison import compare_gsp_and_vcg
from auctioneer.simulation.generation import generate_bidders
from auctioneer.statistics.bootstrap import bootstrap_mean_confidence_interval


def run_repeated_comparisons_with_confidence(
    num_auctions,
    num_bidders,
    ctrs,
    min_value,
    max_value,
    num_resamples=1000,
    confidence=0.95,
    rng=None,
    distribution="uniform",
):
    if num_auctions <= 0:
        raise ValueError("num_auctions must be positive")

    if num_bidders < 0:
        raise ValueError("num_bidders must be non-negative")

    if min_value > max_value:
        raise ValueError("min_value must be less than or equal to max_value")

    if rng is None:
        rng = random.Random()

    # First collect raw per-auction samples; bootstrap needs the full sample set.
    metric_samples = {
        "gsp": {
            "revenue": [],
            "welfare": [],
            "bidder_surplus": [],
        },
        "vcg": {
            "revenue": [],
            "welfare": [],
            "bidder_surplus": [],
        },
        "difference": {
            "revenue": [],
            "welfare": [],
            "bidder_surplus": [],
        },
    }

    for _ in range(num_auctions):
        bidders = generate_bidders(
            num_bidders=num_bidders,
            min_value=min_value,
            max_value=max_value,
            rng=rng,
            distribution=distribution,
        )

        comparison = compare_gsp_and_vcg(bidders, ctrs)

        # Store every metric separately so each confidence interval is estimated independently.
        for mechanism in ["gsp", "vcg", "difference"]:
            for metric in ["revenue", "welfare", "bidder_surplus"]:
                metric_samples[mechanism][metric].append(comparison[mechanism][metric])

    intervals = {}

    # After sampling auctions, estimate uncertainty around each average metric.
    for mechanism in ["gsp", "vcg", "difference"]:
        intervals[mechanism] = {}

        for metric in ["revenue", "welfare", "bidder_surplus"]:
            intervals[mechanism][metric] = bootstrap_mean_confidence_interval(
                metric_samples[mechanism][metric],
                num_resamples=num_resamples,
                confidence=confidence,
                rng=rng,
            )

    return {
        "num_auctions": num_auctions,
        "confidence": confidence,
        "num_resamples": num_resamples,
        "metrics": intervals,
    }

import random

from auctioneer.metrics.bidders import summarize_bidder_outcomes
from auctioneer.metrics.strategies import summarize_strategy_outcomes
from auctioneer.simulation.generation import generate_bidders_from_profiles
from auctioneer.simulation.comparison import compare_gsp_and_vcg


def run_mixed_profile_comparison(profiles, ctrs, rng=None):
    if rng is None:
        rng = random.Random()

    bidders = generate_bidders_from_profiles(profiles, rng)
    comparison = compare_gsp_and_vcg(bidders, ctrs)
    gsp_result = comparison["gsp"]

    return {
        "bidders": bidders,
        "comparison": comparison,
        # Mixed markets care most about who captures surplus under GSP.
        "bidder_outcomes": summarize_bidder_outcomes(gsp_result),
        "strategy_outcomes": summarize_strategy_outcomes(bidders, gsp_result),
    }

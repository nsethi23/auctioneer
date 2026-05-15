import random

from auctioneer.simulation.generation import generate_bidders_from_profiles
from auctioneer.simulation.comparison import compare_gsp_and_vcg


def run_mixed_profile_comparison(profiles, ctrs, rng=None):
    if rng is None:
        rng = random.Random()

    bidders = generate_bidders_from_profiles(profiles, rng)
    comparison = compare_gsp_and_vcg(bidders, ctrs)

    return {
        "bidders": bidders,
        "comparison": comparison,
    }

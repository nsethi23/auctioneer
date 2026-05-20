import random

from auctioneer.agents.strategies import truthful_bid
from auctioneer.simulation.comparison import compare_gsp_and_vcg
from auctioneer.simulation.generation import generate_bidders


def run_repeated_comparisons(
    num_auctions,
    num_bidders,
    ctrs,
    min_value,
    max_value,
    rng=None,
    strategy=truthful_bid,
    strategy_kwargs=None,
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

    gsp_revenue_total = 0.0
    gsp_welfare_total = 0.0
    gsp_bidder_surplus_total = 0.0

    vcg_revenue_total = 0.0
    vcg_welfare_total = 0.0
    vcg_bidder_surplus_total = 0.0

    difference_revenue_total = 0.0
    difference_welfare_total = 0.0
    difference_bidder_surplus_total = 0.0

    for _ in range(num_auctions):
        # Each round samples a fresh market, applies a bidding strategy, then compares mechanisms.
        bidders = generate_bidders(
            num_bidders,
            min_value,
            max_value,
            rng,
            strategy,
            strategy_kwargs,
            distribution=distribution,
        )
        comparison_result = compare_gsp_and_vcg(bidders, ctrs)

        gsp_revenue_total += comparison_result["gsp"]["revenue"]
        gsp_welfare_total += comparison_result["gsp"]["welfare"]
        gsp_bidder_surplus_total += comparison_result["gsp"]["bidder_surplus"]

        vcg_revenue_total += comparison_result["vcg"]["revenue"]
        vcg_welfare_total += comparison_result["vcg"]["welfare"]
        vcg_bidder_surplus_total += comparison_result["vcg"]["bidder_surplus"]

        difference_revenue_total += comparison_result["difference"]["revenue"]
        difference_welfare_total += comparison_result["difference"]["welfare"]
        difference_bidder_surplus_total += comparison_result["difference"][
            "bidder_surplus"
        ]

    # Return aggregate averages instead of every auction to keep simulations compact.
    return {
        "num_auctions": num_auctions,
        "averages": {
            "gsp": {
                "revenue": gsp_revenue_total / num_auctions,
                "welfare": gsp_welfare_total / num_auctions,
                "bidder_surplus": gsp_bidder_surplus_total / num_auctions,
            },
            "vcg": {
                "revenue": vcg_revenue_total / num_auctions,
                "welfare": vcg_welfare_total / num_auctions,
                "bidder_surplus": vcg_bidder_surplus_total / num_auctions,
            },
            "difference": {
                "revenue": difference_revenue_total / num_auctions,
                "welfare": difference_welfare_total / num_auctions,
                "bidder_surplus": difference_bidder_surplus_total / num_auctions,
            },
        },
    }

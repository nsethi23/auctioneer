from auctioneer.agents.best_response import find_best_response_bid
from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.metrics.allocations import get_bidder_utility


def check_gsp_nash_equilibrium(bidders, ctrs, candidate_bids, tolerance=1e-9):
    if not candidate_bids:
        raise ValueError("candidate_bids must not be empty")

    current_result = run_gsp_auction(bidders, ctrs)

    deviations = []
    max_utility_gain = 0.0

    for bidder in bidders:
        other_bidders = [
            other_bidder
            for other_bidder in bidders
            if other_bidder["id"] != bidder["id"]
        ]

        current_utility = get_bidder_utility(current_result, bidder["id"])

        best_response = find_best_response_bid(
            bidder_id=bidder["id"],
            value=bidder["value"],
            other_bidders=other_bidders,
            ctrs=ctrs,
            candidate_bids=candidate_bids,
        )

        best_utility = best_response["utility"]
        utility_gain = best_utility - current_utility
        max_utility_gain = max(max_utility_gain, utility_gain)

        if utility_gain > tolerance:
            deviations.append(
                {
                    "bidder_id": bidder["id"],
                    "current_bid": bidder["bid"],
                    "best_bid": best_response["bid"],
                    "current_utility": current_utility,
                    "best_utility": best_utility,
                    "utility_gain": utility_gain,
                }
            )

    return {
        "is_equilibrium": len(deviations) == 0,
        "max_utility_gain": max_utility_gain,
        "deviations": deviations,
    }

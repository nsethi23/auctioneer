from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.metrics.allocations import get_bidder_utility


def find_best_response_bid(
    bidder_id,
    value,
    other_bidders,
    ctrs,
    candidate_bids,
):
    results = []
    best_bid = None
    best_utility = None

    # Try each candidate bid while holding all other bidders fixed.
    for bid in candidate_bids:
        bidder = {"id": bidder_id, "value": value, "bid": bid}
        auction_result = run_gsp_auction(other_bidders + [bidder], ctrs)
        utility = get_bidder_utility(auction_result, bidder_id)

        results.append({"bid": bid, "utility": utility})

        # Use strict greater-than so the first best bid wins ties.
        if best_utility is None or utility > best_utility:
            best_bid = bid
            best_utility = utility

    return {
        "bid": best_bid,
        "utility": best_utility,
        "results": results,
    }


def generate_best_response_curve(
    bidder_id,
    values,
    other_bidders,
    ctrs,
    candidate_bids,
):
    results = []

    # Sweep private values to produce chart-ready best-response data.
    for value in values:
        best_response = find_best_response_bid(
            bidder_id,
            value,
            other_bidders,
            ctrs,
            candidate_bids,
        )
        results.append(
            {
                "value": value,
                "best_bid": best_response["bid"],
                "best_utility": best_response["utility"],
                "results": best_response["results"],
            }
        )

    return results

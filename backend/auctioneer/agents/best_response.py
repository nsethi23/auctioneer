from auctioneer.auctions.gsp import run_gsp_auction


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

        # Losing bidders do not appear in allocations, so their utility is zero.
        utility = 0.0

        for allocation in auction_result["allocations"]:
            if allocation["bidder_id"] == bidder_id:
                utility = allocation["utility"]
                break

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

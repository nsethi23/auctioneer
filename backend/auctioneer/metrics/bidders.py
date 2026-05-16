def summarize_bidder_outcomes(auction_result):
    outcomes = {}

    for allocation in auction_result["allocations"]:
        bidder_id = allocation["bidder_id"]

        # Keying by bidder id makes individual utility comparisons easy later.
        outcomes[bidder_id] = {
            "slot": allocation["slot"],
            "ctr": allocation["ctr"],
            "value": allocation["value"],
            "bid": allocation["bid"],
            "payment": allocation["payment"],
            "utility": allocation["utility"],
        }

    return outcomes

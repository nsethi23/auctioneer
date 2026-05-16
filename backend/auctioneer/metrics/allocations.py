def get_bidder_utility(auction_result, bidder_id):
    for allocation in auction_result["allocations"]:
        if allocation["bidder_id"] == bidder_id:
            return allocation["utility"]

    return 0.0

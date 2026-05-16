from auctioneer.metrics.bidders import summarize_bidder_outcomes


def summarize_strategy_outcomes(bidders, auction_result):
    bidder_outcomes = summarize_bidder_outcomes(auction_result)
    strategy_outcomes = {}

    for bidder in bidders:
        strategy = bidder.get("strategy", "unknown")
        utility = bidder_outcomes.get(bidder["id"], {}).get("utility", 0.0)

        # Grouping by strategy lets mixed markets compare behavior-level surplus.
        if strategy not in strategy_outcomes:
            strategy_outcomes[strategy] = {
                "count": 0,
                "total_utility": 0.0,
                "average_utility": 0.0,
            }

        strategy_outcomes[strategy]["count"] += 1
        strategy_outcomes[strategy]["total_utility"] += utility

    for outcome in strategy_outcomes.values():
        outcome["average_utility"] = outcome["total_utility"] / outcome["count"]

    return strategy_outcomes

from auctioneer.models import normalize_bidder


def run_gsp_auction(bidders, ctrs):
    bidders = [normalize_bidder(bidder) for bidder in bidders]

    allocations = []

    revenue = 0.0
    welfare = 0.0
    bidder_surplus = 0.0

    # GSP ranks advertisers by bid: highest bidder gets the highest-CTR slot.
    sorted_bidders = sorted(bidders, key=lambda b: b["bid"], reverse=True)

    # Assign winners in ranked order until we run out of slots.
    for i, bidder in enumerate(sorted_bidders):
        if i >= len(ctrs):
            break

        ctr = ctrs[i]
        if i + 1 < len(sorted_bidders):
            next_bid = sorted_bidders[i + 1]["bid"]
        else:
            next_bid = 0.0

        # Expected value is the bidder's private value scaled by slot click rate.
        realized_value = ctr * bidder["value"]

        # In GSP, each winner pays the next-highest bid scaled by their slot CTR.
        payment = ctr * next_bid

        # Bidder surplus/profit from winning this slot.
        utility = realized_value - payment

        allocations.append(
            {
                "bidder_id": bidder["id"],
                "slot": i,
                "ctr": ctr,
                "value": bidder["value"],
                "bid": bidder["bid"],
                "payment": payment,
                "utility": utility,
            }
        )

        revenue += payment
        welfare += realized_value
        bidder_surplus += utility

    return {
        "allocations": allocations,
        "revenue": revenue,
        "welfare": welfare,
        "bidder_surplus": bidder_surplus,
    }

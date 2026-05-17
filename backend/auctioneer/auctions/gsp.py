from auctioneer.models import normalize_bidder


def run_gsp_auction(bidders, ctrs, reserve_price=0.0):
    bidders = [normalize_bidder(bidder) for bidder in bidders]

    allocations = []

    revenue = 0.0
    welfare = 0.0
    bidder_surplus = 0.0

    # Reserve prices make low bids ineligible before ranking happens.
    eligible_bidders = [bidder for bidder in bidders if bidder["bid"] >= reserve_price]

    # GSP ranks advertisers by bid: highest bidder gets the highest-CTR slot.
    sorted_bidders = sorted(eligible_bidders, key=lambda b: b["bid"], reverse=True)

    # Assign winners in ranked order until we run out of slots.
    for i, bidder in enumerate(sorted_bidders):
        if i >= len(ctrs):
            break

        ctr = ctrs[i]
        if i + 1 < len(sorted_bidders):
            next_bid = sorted_bidders[i + 1]["bid"]
        else:
            next_bid = reserve_price

        # Expected value is the bidder's private value scaled by slot click rate.
        realized_value = ctr * bidder["value"]

        # Winners pay at least the reserve price, even without a next bidder.
        payment = ctr * max(next_bid, reserve_price)

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

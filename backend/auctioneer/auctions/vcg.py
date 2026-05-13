def compute_welfare(sorted_bidders, ctrs):
    welfare = 0.0

    for i, bidder in enumerate(sorted_bidders):
        if i >= len(ctrs):
            break

        ctr = ctrs[i]
        welfare += ctr * bidder["value"]

    return welfare


def run_vcg_auction(bidders, ctrs):
    allocations = []

    revenue = 0.0
    welfare = 0.0
    bidder_surplus = 0.0

    sorted_bidders = sorted(bidders, key=lambda b: b["bid"], reverse=True)

    for i, bidder in enumerate(sorted_bidders):
        if i >= len(ctrs):
            break

        ctr = ctrs[i]
        realized_value = ctr * bidder["value"]

        welfare_without_bidder = compute_welfare(
            sorted_bidders[:i] + sorted_bidders[i + 1 :],
            ctrs,
        )

        total_welfare_with_bidder = compute_welfare(sorted_bidders, ctrs)
        others_welfare_with_bidder = total_welfare_with_bidder - realized_value

        payment = welfare_without_bidder - others_welfare_with_bidder
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

from auctioneer.models import normalize_bidder


def compute_welfare(sorted_bidders, ctrs):
    welfare = 0.0

    # Welfare is the total expected value created by assigning bidders to slots.
    for i, bidder in enumerate(sorted_bidders):
        if i >= len(ctrs):
            break

        ctr = ctrs[i]
        welfare += ctr * bidder["value"]

    return welfare


def run_vcg_auction(bidders, ctrs, reserve_price=0.0):
    bidders = [normalize_bidder(bidder) for bidder in bidders]

    allocations = []

    revenue = 0.0
    welfare = 0.0
    bidder_surplus = 0.0

    # Reserve prices remove low bidders before allocation and externality pricing.
    eligible_bidders = [bidder for bidder in bidders if bidder["bid"] >= reserve_price]

    sorted_bidders = sorted(eligible_bidders, key=lambda b: (-b["bid"], b["id"]))

    for i, bidder in enumerate(sorted_bidders):
        if i >= len(ctrs):
            break

        ctr = ctrs[i]
        realized_value = ctr * bidder["value"]

        # VCG prices each winner by the welfare other bidders would gain
        # if this winner were removed and the slots were reallocated.
        welfare_without_bidder = compute_welfare(
            sorted_bidders[:i] + sorted_bidders[i + 1 :],
            ctrs,
        )

        total_welfare_with_bidder = compute_welfare(sorted_bidders, ctrs)
        others_welfare_with_bidder = total_welfare_with_bidder - realized_value

        # The payment is the externality imposed on everyone else,
        # bounded below by the reserve-scaled slot price.
        externality_payment = welfare_without_bidder - others_welfare_with_bidder
        reserve_payment = reserve_price * ctr
        payment = max(externality_payment, reserve_payment)
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

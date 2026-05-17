from auctioneer.models import normalize_bidder


def get_quality_score(bidder):
    return bidder.get("quality_score", 1.0)


def get_rank_score(bidder, use_quality_scores):
    if not use_quality_scores:
        return bidder["bid"]

    return bidder["bid"] * get_quality_score(bidder)


def get_gsp_price_per_click(
    bidder,
    sorted_bidders,
    bidder_index,
    reserve_price,
    use_quality_scores,
):
    if bidder_index + 1 < len(sorted_bidders):
        next_bidder = sorted_bidders[bidder_index + 1]

        if use_quality_scores:
            next_rank_score = get_rank_score(next_bidder, use_quality_scores=True)
            return max(next_rank_score / get_quality_score(bidder), reserve_price)

        return max(next_bidder["bid"], reserve_price)

    return reserve_price


def run_gsp_auction(
    bidders,
    ctrs,
    reserve_price=0.0,
    use_quality_scores=False,
):
    bidders = [normalize_bidder(bidder) for bidder in bidders]

    if use_quality_scores:
        for bidder in bidders:
            if get_quality_score(bidder) <= 0:
                raise ValueError("quality_score must be positive")

    allocations = []

    revenue = 0.0
    welfare = 0.0
    bidder_surplus = 0.0

    # Reserve prices make low bids ineligible before ranking happens.
    eligible_bidders = [bidder for bidder in bidders if bidder["bid"] >= reserve_price]

    # With quality scores enabled, ad rank is bid times quality.
    sorted_bidders = sorted(
        eligible_bidders,
        key=lambda b: (-get_rank_score(b, use_quality_scores), b["id"]),
    )

    # Assign winners in ranked order until we run out of slots.
    for i, bidder in enumerate(sorted_bidders):
        if i >= len(ctrs):
            break

        ctr = ctrs[i]
        price_per_click = get_gsp_price_per_click(
            bidder=bidder,
            sorted_bidders=sorted_bidders,
            bidder_index=i,
            reserve_price=reserve_price,
            use_quality_scores=use_quality_scores,
        )

        # Expected value is the bidder's private value scaled by slot click rate.
        realized_value = ctr * bidder["value"]

        # Payment is expected clicks times the generalized second price per click.
        payment = ctr * price_per_click

        # Bidder surplus/profit from winning this slot.
        utility = realized_value - payment

        allocations.append(
            {
                "bidder_id": bidder["id"],
                "slot": i,
                "ctr": ctr,
                "value": bidder["value"],
                "bid": bidder["bid"],
                "quality_score": get_quality_score(bidder),
                "rank_score": get_rank_score(bidder, use_quality_scores),
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

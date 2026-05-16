from auctioneer.auctions.gsp import run_gsp_auction


def compute_optimal_welfare(bidders, ctrs):
    # The efficient benchmark assigns the best slots to the highest true values.
    sorted_bidders = sorted(bidders, key=lambda b: b["value"], reverse=True)

    return sum(bidder["value"] * ctr for bidder, ctr in zip(sorted_bidders, ctrs))


def compute_price_of_anarchy(bidders, ctrs):
    optimal_welfare = compute_optimal_welfare(bidders, ctrs)
    strategic_result = run_gsp_auction(bidders, ctrs)
    strategic_welfare = strategic_result["welfare"]

    # Price of anarchy compares ideal welfare against the strategic GSP outcome.
    if strategic_welfare == 0:
        price_of_anarchy = float("inf")
    else:
        price_of_anarchy = optimal_welfare / strategic_welfare

    return {
        "optimal_welfare": optimal_welfare,
        "strategic_welfare": strategic_welfare,
        "price_of_anarchy": price_of_anarchy,
        "welfare_loss": optimal_welfare - strategic_welfare,
    }

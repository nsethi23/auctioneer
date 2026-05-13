from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.auctions.vcg import run_vcg_auction


def compare_gsp_and_vcg(bidders, ctrs):
    gsp_result = run_gsp_auction(bidders, ctrs)
    vcg_result = run_vcg_auction(bidders, ctrs)

    # Keep both raw mechanism outputs and deltas so simulations and UI panels
    # can compare revenue, efficiency, and bidder surplus from one response.
    return {
        "gsp": gsp_result,
        "vcg": vcg_result,
        "difference": {
            "revenue": gsp_result["revenue"] - vcg_result["revenue"],
            "welfare": gsp_result["welfare"] - vcg_result["welfare"],
            "bidder_surplus": (
                gsp_result["bidder_surplus"] - vcg_result["bidder_surplus"]
            ),
        },
    }

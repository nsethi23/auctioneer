from auctioneer.agents.best_response import find_best_response_bid
from auctioneer.agents.nash import check_gsp_nash_equilibrium


def _copy_bidders(bidders):
    return [dict(bidder) for bidder in bidders]


def _record_round(round_number, bidders, ctrs, candidate_bids, tolerance):
    nash_result = check_gsp_nash_equilibrium(
        bidders=bidders,
        ctrs=ctrs,
        candidate_bids=candidate_bids,
        tolerance=tolerance,
    )

    return {
        "round": round_number,
        "is_equilibrium": nash_result["is_equilibrium"],
        "max_utility_gain": nash_result["max_utility_gain"],
        "bidders": _copy_bidders(bidders),
        "deviations": nash_result["deviations"],
    }


def run_best_response_dynamics(
    bidders,
    ctrs,
    candidate_bids,
    max_rounds,
    tolerance=1e-9,
):
    if not candidate_bids:
        raise ValueError("candidate_bids must not be empty")

    if max_rounds < 0:
        raise ValueError("max_rounds must be non-negative")

    initial_bidders = _copy_bidders(bidders)
    current_bidders = _copy_bidders(bidders)

    history = [
        _record_round(
            round_number=0,
            bidders=current_bidders,
            ctrs=ctrs,
            candidate_bids=candidate_bids,
            tolerance=tolerance,
        )
    ]

    if history[-1]["is_equilibrium"]:
        return {
            "initial_bidders": initial_bidders,
            "final_bidders": _copy_bidders(current_bidders),
            "converged": True,
            "rounds_run": 0,
            "history": history,
        }

    rounds_run = 0

    for round_number in range(1, max_rounds + 1):
        # Sequentially let each bidder best-respond to the latest market state.
        for bidder in current_bidders:
            other_bidders = [
                other_bidder
                for other_bidder in current_bidders
                if other_bidder["id"] != bidder["id"]
            ]
            best_response = find_best_response_bid(
                bidder_id=bidder["id"],
                value=bidder["value"],
                other_bidders=other_bidders,
                ctrs=ctrs,
                candidate_bids=candidate_bids,
            )
            bidder["bid"] = best_response["bid"]

        rounds_run = round_number
        history.append(
            _record_round(
                round_number=round_number,
                bidders=current_bidders,
                ctrs=ctrs,
                candidate_bids=candidate_bids,
                tolerance=tolerance,
            )
        )

        if history[-1]["is_equilibrium"]:
            break

    return {
        "initial_bidders": initial_bidders,
        "final_bidders": _copy_bidders(current_bidders),
        "converged": history[-1]["is_equilibrium"],
        "rounds_run": rounds_run,
        "history": history,
    }

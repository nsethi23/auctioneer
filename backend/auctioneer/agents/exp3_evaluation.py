import random

from auctioneer.agents.best_response import find_best_response_bid
from auctioneer.agents.exp3 import EXP3Bidder
from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.metrics.allocations import get_bidder_utility


def track_exp3_convergence(
    bidder_id,
    value,
    other_bidders,
    ctrs,
    candidate_bids,
    num_episodes,
    checkpoint_interval,
    gamma=0.1,
    rng=None,
):
    if num_episodes < 0:
        raise ValueError("num_episodes must be non-negative")

    if checkpoint_interval <= 0:
        raise ValueError("checkpoint_interval must be positive")

    if not candidate_bids:
        raise ValueError("candidate_bids must not be empty")

    if rng is None:
        rng = random.Random()

    agent = EXP3Bidder(gamma=gamma, rng=rng)

    # Compute the analytic benchmark once so every checkpoint can measure the gap.
    best_response = find_best_response_bid(
        bidder_id=bidder_id,
        value=value,
        other_bidders=other_bidders,
        ctrs=ctrs,
        candidate_bids=candidate_bids,
    )

    history = []
    checkpoints = []

    for episode in range(1, num_episodes + 1):
        bid = agent.select_bid(candidate_bids)

        bidder = {"id": bidder_id, "value": value, "bid": bid}
        auction_result = run_gsp_auction(other_bidders + [bidder], ctrs)
        reward = get_bidder_utility(auction_result, bidder_id)

        agent.update(bid, reward, candidate_bids)

        history.append({"episode": episode, "bid": bid, "reward": reward})

        if episode % checkpoint_interval == 0:
            # At checkpoints evaluate the greedy policy (highest-weight bid) without
            # sampling noise, so the bid gap measures convergence cleanly.
            learned_bid = agent.best_bid(candidate_bids)
            learned_weight = agent.best_weight(candidate_bids)

            recent_window = min(10, len(history))
            average_recent_reward = (
                sum(entry["reward"] for entry in history[-recent_window:])
                / recent_window
            )

            checkpoints.append(
                {
                    "episode": episode,
                    "learned_bid": learned_bid,
                    "learned_weight": learned_weight,
                    "best_response_bid": best_response["bid"],
                    "best_response_utility": best_response["utility"],
                    "bid_gap": abs(learned_bid - best_response["bid"]),
                    "average_recent_reward": average_recent_reward,
                }
            )

    return {
        "best_response": {
            "bid": best_response["bid"],
            "utility": best_response["utility"],
        },
        "checkpoints": checkpoints,
        "history": history,
    }

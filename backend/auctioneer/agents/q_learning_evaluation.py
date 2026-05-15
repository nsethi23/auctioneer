import random

from auctioneer.agents.best_response import find_best_response_bid
from auctioneer.agents.q_learning_training import train_q_learning_bidder


def compute_convergence_metrics(history, learned_bid, learned_q_value, best_response):
    if not history:
        average_reward = 0.0
        average_recent_reward = 0.0
    else:
        average_reward = sum(entry["reward"] for entry in history) / len(history)

        recent_window = min(10, len(history))
        recent_history = history[-recent_window:]
        average_recent_reward = sum(entry["reward"] for entry in recent_history) / len(
            recent_history
        )

    return {
        "bid_gap": abs(learned_bid - best_response["bid"]),
        "utility_gap": best_response["utility"] - learned_q_value,
        "average_reward": average_reward,
        "average_recent_reward": average_recent_reward,
    }


def compare_q_learning_to_best_response(
    bidder_id,
    value,
    other_bidders,
    ctrs,
    candidate_bids,
    num_episodes,
    learning_rate=0.1,
    discount_factor=0.0,
    epsilon=0.1,
    rng=None,
):
    if rng is None:
        rng = random.Random()

    # Train from auction rewards before comparing against the analytic search.
    training_result = train_q_learning_bidder(
        bidder_id=bidder_id,
        value=value,
        other_bidders=other_bidders,
        ctrs=ctrs,
        candidate_bids=candidate_bids,
        num_episodes=num_episodes,
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        epsilon=epsilon,
        rng=rng,
    )

    agent = training_result["agent"]

    # Disable exploration so the learned policy uses its best-known bid.
    agent.epsilon = 0.0
    learned_bid = agent.select_bid("default", candidate_bids)
    learned_q_value = agent.get_q_value("default", learned_bid)

    # Best response is the brute-force GSP benchmark for the same market.
    best_response_result = find_best_response_bid(
        bidder_id=bidder_id,
        value=value,
        other_bidders=other_bidders,
        ctrs=ctrs,
        candidate_bids=candidate_bids,
    )

    # Convergence metrics quantify how close learning came to best response.
    metrics = compute_convergence_metrics(
        training_result["history"],
        learned_bid,
        learned_q_value,
        best_response_result,
    )

    return {
        "learned": {
            "bid": learned_bid,
            "q_value": learned_q_value,
        },
        "best_response": {
            "bid": best_response_result["bid"],
            "utility": best_response_result["utility"],
        },
        "metrics": metrics,
        "training": training_result,
    }

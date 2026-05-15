import random

from auctioneer.agents.best_response import find_best_response_bid
from auctioneer.agents.q_learning import QLearningBidder
from auctioneer.agents.q_learning_training import train_q_learning_bidder
from auctioneer.auctions.gsp import run_gsp_auction


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


def track_q_learning_convergence(
    bidder_id,
    value,
    other_bidders,
    ctrs,
    candidate_bids,
    num_episodes,
    checkpoint_interval,
    learning_rate=0.1,
    discount_factor=0.0,
    epsilon=0.1,
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

    agent = QLearningBidder(
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        epsilon=epsilon,
        rng=rng,
    )

    best_response = find_best_response_bid(
        bidder_id=bidder_id,
        value=value,
        other_bidders=other_bidders,
        ctrs=ctrs,
        candidate_bids=candidate_bids,
    )

    state = "default"
    next_state = "default"

    history = []
    checkpoints = []

    # Train episode by episode so checkpoints can measure learning progress.
    for episode in range(1, num_episodes + 1):
        bid = agent.select_bid(state, candidate_bids)

        bidder = {
            "id": bidder_id,
            "value": value,
            "bid": bid,
        }

        auction_result = run_gsp_auction(other_bidders + [bidder], ctrs)

        reward = 0.0

        for allocation in auction_result["allocations"]:
            if allocation["bidder_id"] == bidder_id:
                reward = allocation["utility"]
                break

        q_value = agent.update(
            state=state,
            bid=bid,
            reward=reward,
            next_state=next_state,
            candidate_bids=candidate_bids,
        )

        history.append(
            {
                "episode": episode,
                "bid": bid,
                "reward": reward,
                "q_value": q_value,
            }
        )

        # Checkpoints evaluate the learned policy without exploration noise.
        if episode % checkpoint_interval == 0:
            old_epsilon = agent.epsilon
            agent.epsilon = 0.0

            learned_bid = agent.select_bid(state, candidate_bids)
            learned_q_value = agent.get_q_value(state, learned_bid)

            agent.epsilon = old_epsilon

            recent_window = min(10, len(history))
            recent_history = history[-recent_window:]
            average_recent_reward = sum(
                entry["reward"] for entry in recent_history
            ) / len(recent_history)

            checkpoints.append(
                {
                    "episode": episode,
                    "learned_bid": learned_bid,
                    "learned_q_value": learned_q_value,
                    "best_response_bid": best_response["bid"],
                    "best_response_utility": best_response["utility"],
                    "bid_gap": abs(learned_bid - best_response["bid"]),
                    "utility_gap": best_response["utility"] - learned_q_value,
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

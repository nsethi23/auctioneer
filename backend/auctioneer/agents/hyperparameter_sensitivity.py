import random

from auctioneer.agents.q_learning_evaluation import compare_q_learning_to_best_response


def run_q_learning_hyperparameter_sensitivity(
    bidder_id,
    value,
    other_bidders,
    ctrs,
    candidate_bids,
    num_episodes,
    learning_rates,
    epsilons,
    discount_factor=0.0,
    rng=None,
):
    if not learning_rates:
        raise ValueError("learning_rates must not be empty")

    if not epsilons:
        raise ValueError("epsilons must not be empty")

    if rng is None:
        rng = random.Random()

    experiments = []

    for learning_rate in learning_rates:
        for epsilon in epsilons:
            # Run the same market under one learning-rate/exploration setting.
            evaluation = compare_q_learning_to_best_response(
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

            experiments.append(
                {
                    "learning_rate": learning_rate,
                    "epsilon": epsilon,
                    "learned_bid": evaluation["learned"]["bid"],
                    "learned_q_value": evaluation["learned"]["q_value"],
                    "best_response_bid": evaluation["best_response"]["bid"],
                    "best_response_utility": evaluation["best_response"]["utility"],
                    "metrics": evaluation["metrics"],
                }
            )

    return {
        "num_episodes": num_episodes,
        "discount_factor": discount_factor,
        "experiments": experiments,
    }

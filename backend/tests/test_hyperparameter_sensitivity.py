import random

import pytest

from auctioneer.agents.hyperparameter_sensitivity import (
    run_q_learning_hyperparameter_sensitivity,
)


def test_run_q_learning_hyperparameter_sensitivity_returns_all_grid_combinations():
    result = run_q_learning_hyperparameter_sensitivity(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 6.0, 10.0],
        num_episodes=5,
        learning_rates=[0.1, 0.5],
        epsilons=[0.0, 0.2],
        rng=random.Random(123),
    )

    assert result["num_episodes"] == 5
    assert len(result["experiments"]) == 4
    assert [
        (experiment["learning_rate"], experiment["epsilon"])
        for experiment in result["experiments"]
    ] == [(0.1, 0.0), (0.1, 0.2), (0.5, 0.0), (0.5, 0.2)]


def test_run_q_learning_hyperparameter_sensitivity_includes_evaluation_metrics():
    result = run_q_learning_hyperparameter_sensitivity(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        learning_rates=[0.1],
        epsilons=[0.0],
        rng=random.Random(123),
    )

    experiment = result["experiments"][0]

    assert experiment["learned_bid"] == pytest.approx(6.0)
    assert experiment["best_response_bid"] == pytest.approx(6.0)
    assert experiment["best_response_utility"] == pytest.approx(1.5)
    assert "bid_gap" in experiment["metrics"]
    assert "utility_gap" in experiment["metrics"]
    assert "average_reward" in experiment["metrics"]
    assert "average_recent_reward" in experiment["metrics"]


def test_run_q_learning_hyperparameter_sensitivity_is_deterministic_with_seeded_rng():
    first = run_q_learning_hyperparameter_sensitivity(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 6.0, 10.0],
        num_episodes=5,
        learning_rates=[0.1, 0.5],
        epsilons=[0.0, 0.2],
        rng=random.Random(123),
    )
    second = run_q_learning_hyperparameter_sensitivity(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 6.0, 10.0],
        num_episodes=5,
        learning_rates=[0.1, 0.5],
        epsilons=[0.0, 0.2],
        rng=random.Random(123),
    )

    assert first == second


def test_run_q_learning_hyperparameter_sensitivity_rejects_empty_learning_rates():
    with pytest.raises(ValueError, match="learning_rates"):
        run_q_learning_hyperparameter_sensitivity(
            bidder_id="A",
            value=10.0,
            other_bidders=[],
            ctrs=[0.6],
            candidate_bids=[0.0, 10.0],
            num_episodes=1,
            learning_rates=[],
            epsilons=[0.1],
        )


def test_run_q_learning_hyperparameter_sensitivity_rejects_empty_epsilons():
    with pytest.raises(ValueError, match="epsilons"):
        run_q_learning_hyperparameter_sensitivity(
            bidder_id="A",
            value=10.0,
            other_bidders=[],
            ctrs=[0.6],
            candidate_bids=[0.0, 10.0],
            num_episodes=1,
            learning_rates=[0.1],
            epsilons=[],
        )

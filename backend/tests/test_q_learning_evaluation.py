import random

import pytest

from auctioneer.agents.q_learning_evaluation import (
    compare_q_learning_to_best_response,
    compute_convergence_metrics,
)


def test_compare_q_learning_to_best_response_returns_expected_sections():
    result = compare_q_learning_to_best_response(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=1,
        rng=random.Random(123),
    )

    assert "learned" in result
    assert "best_response" in result
    assert "metrics" in result
    assert "training" in result


def test_compare_q_learning_to_best_response_learned_bid_comes_from_candidates():
    candidate_bids = [0.0, 6.0, 10.0]

    result = compare_q_learning_to_best_response(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=candidate_bids,
        num_episodes=10,
        epsilon=0.2,
        rng=random.Random(123),
    )

    assert result["learned"]["bid"] in candidate_bids


def test_compare_q_learning_to_best_response_reports_known_best_response():
    result = compare_q_learning_to_best_response(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 6.0, 10.0],
        num_episodes=1,
        rng=random.Random(123),
    )

    assert result["best_response"]["bid"] == pytest.approx(6.0)
    assert result["best_response"]["utility"] == pytest.approx(1.5)


def test_compare_q_learning_to_best_response_includes_training_history():
    result = compare_q_learning_to_best_response(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        rng=random.Random(123),
    )

    assert len(result["training"]["history"]) == 3


def test_compare_q_learning_to_best_response_can_match_single_candidate_policy():
    result = compare_q_learning_to_best_response(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert result["learned"]["bid"] == pytest.approx(6.0)
    assert result["best_response"]["bid"] == pytest.approx(6.0)


def test_compare_q_learning_to_best_response_reports_zero_bid_gap_when_bids_match():
    result = compare_q_learning_to_best_response(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert result["metrics"]["bid_gap"] == pytest.approx(0.0)


def test_compare_q_learning_to_best_response_reports_average_rewards():
    result = compare_q_learning_to_best_response(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert result["metrics"]["average_reward"] == pytest.approx(1.5)
    assert result["metrics"]["average_recent_reward"] == pytest.approx(1.5)


def test_compute_convergence_metrics_handles_empty_history():
    metrics = compute_convergence_metrics(
        history=[],
        learned_bid=6.0,
        learned_q_value=1.0,
        best_response={"bid": 6.0, "utility": 1.5},
    )

    assert metrics["bid_gap"] == pytest.approx(0.0)
    assert metrics["utility_gap"] == pytest.approx(0.5)
    assert metrics["average_reward"] == pytest.approx(0.0)
    assert metrics["average_recent_reward"] == pytest.approx(0.0)


def test_compute_convergence_metrics_uses_recent_reward_window():
    history = [
        {"reward": 0.0},
        {"reward": 0.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
        {"reward": 1.0},
    ]

    metrics = compute_convergence_metrics(
        history=history,
        learned_bid=6.0,
        learned_q_value=1.0,
        best_response={"bid": 6.0, "utility": 1.5},
    )

    assert metrics["average_reward"] == pytest.approx(10.0 / 12.0)
    assert metrics["average_recent_reward"] == pytest.approx(1.0)

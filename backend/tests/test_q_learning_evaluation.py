import random

import pytest

from auctioneer.agents.q_learning_evaluation import (
    compare_q_learning_to_best_response,
    compute_convergence_metrics,
    track_q_learning_convergence,
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


def test_track_q_learning_convergence_returns_best_response_checkpoints_and_history():
    result = track_q_learning_convergence(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        checkpoint_interval=1,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert "best_response" in result
    assert "checkpoints" in result
    assert "history" in result
    assert len(result["history"]) == 3


def test_track_q_learning_convergence_records_checkpoints_at_interval():
    result = track_q_learning_convergence(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=5,
        checkpoint_interval=2,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert [checkpoint["episode"] for checkpoint in result["checkpoints"]] == [2, 4]


def test_track_q_learning_convergence_single_candidate_has_zero_bid_gap():
    result = track_q_learning_convergence(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        checkpoint_interval=1,
        epsilon=0.0,
        rng=random.Random(123),
    )

    for checkpoint in result["checkpoints"]:
        assert checkpoint["learned_bid"] == pytest.approx(6.0)
        assert checkpoint["best_response_bid"] == pytest.approx(6.0)
        assert checkpoint["bid_gap"] == pytest.approx(0.0)


def test_track_q_learning_convergence_computes_average_recent_reward():
    result = track_q_learning_convergence(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=3,
        checkpoint_interval=1,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert result["checkpoints"][-1]["average_recent_reward"] == pytest.approx(1.5)


def test_track_q_learning_convergence_rejects_negative_num_episodes():
    with pytest.raises(ValueError, match="num_episodes"):
        track_q_learning_convergence(
            bidder_id="A",
            value=10.0,
            other_bidders=[],
            ctrs=[0.6],
            candidate_bids=[1.0],
            num_episodes=-1,
            checkpoint_interval=1,
        )


def test_track_q_learning_convergence_rejects_non_positive_checkpoint_interval():
    with pytest.raises(ValueError, match="checkpoint_interval"):
        track_q_learning_convergence(
            bidder_id="A",
            value=10.0,
            other_bidders=[],
            ctrs=[0.6],
            candidate_bids=[1.0],
            num_episodes=1,
            checkpoint_interval=0,
        )


def test_track_q_learning_convergence_rejects_empty_candidate_bids():
    with pytest.raises(ValueError, match="candidate_bids"):
        track_q_learning_convergence(
            bidder_id="A",
            value=10.0,
            other_bidders=[],
            ctrs=[0.6],
            candidate_bids=[],
            num_episodes=1,
            checkpoint_interval=1,
        )

import random

import pytest

from auctioneer.agents.q_learning import QLearningBidder
from auctioneer.agents.q_learning_training import train_q_learning_bidder


def test_train_q_learning_bidder_returns_trained_agent():
    result = train_q_learning_bidder(
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

    assert isinstance(result["agent"], QLearningBidder)


def test_train_q_learning_bidder_records_one_history_entry_per_episode():
    result = train_q_learning_bidder(
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

    assert len(result["history"]) == 3
    assert [entry["episode"] for entry in result["history"]] == [0, 1, 2]


def test_train_q_learning_bidder_uses_candidate_bids():
    candidate_bids = [0.0, 6.0]

    result = train_q_learning_bidder(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=candidate_bids,
        num_episodes=5,
        epsilon=1.0,
        rng=random.Random(123),
    )

    for entry in result["history"]:
        assert entry["bid"] in candidate_bids


def test_train_q_learning_bidder_updates_q_value_after_positive_reward():
    result = train_q_learning_bidder(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[6.0],
        num_episodes=1,
        learning_rate=0.5,
        discount_factor=0.0,
        epsilon=0.0,
        rng=random.Random(123),
    )

    history_entry = result["history"][0]

    assert history_entry["reward"] == pytest.approx(1.5)
    assert history_entry["q_value"] == pytest.approx(0.75)
    assert result["agent"].get_q_value("default", 6.0) == pytest.approx(0.75)


def test_train_q_learning_bidder_records_zero_reward_when_bidder_loses():
    result = train_q_learning_bidder(
        bidder_id="A",
        value=10.0,
        other_bidders=[
            {"id": "B", "value": 8.0, "bid": 8.0},
            {"id": "C", "value": 5.0, "bid": 5.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0],
        num_episodes=1,
        learning_rate=0.5,
        discount_factor=0.0,
        epsilon=0.0,
        rng=random.Random(123),
    )

    history_entry = result["history"][0]

    assert history_entry["reward"] == pytest.approx(0.0)
    assert history_entry["q_value"] == pytest.approx(0.0)

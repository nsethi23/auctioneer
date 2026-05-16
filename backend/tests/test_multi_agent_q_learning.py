import random

import pytest

from auctioneer.agents.multi_agent_q_learning import train_multi_agent_q_learning
from auctioneer.agents.q_learning import QLearningBidder


def test_train_multi_agent_q_learning_returns_agent_for_each_bidder():
    result = train_multi_agent_q_learning(
        bidder_specs=[
            {"id": "A", "value": 10.0},
            {"id": "B", "value": 8.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 10.0],
        num_episodes=3,
        rng=random.Random(123),
    )

    assert set(result["agents"]) == {"A", "B"}
    assert isinstance(result["agents"]["A"], QLearningBidder)
    assert isinstance(result["agents"]["B"], QLearningBidder)


def test_train_multi_agent_q_learning_records_episode_history():
    result = train_multi_agent_q_learning(
        bidder_specs=[
            {"id": "A", "value": 10.0},
            {"id": "B", "value": 8.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[10.0],
        num_episodes=2,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert len(result["history"]) == 2
    assert result["history"][0]["episode"] == 0
    assert result["history"][0]["bids"] == {"A": 10.0, "B": 10.0}
    assert result["history"][0]["rewards"]["A"] == pytest.approx(0.0)
    assert result["history"][0]["rewards"]["B"] == pytest.approx(2.4)
    assert result["history"][0]["revenue"] == pytest.approx(6.0)
    assert result["history"][0]["welfare"] == pytest.approx(8.4)
    assert result["history"][0]["bidder_surplus"] == pytest.approx(2.4)


def test_train_multi_agent_q_learning_updates_each_agent_q_table():
    result = train_multi_agent_q_learning(
        bidder_specs=[
            {"id": "A", "value": 10.0},
            {"id": "B", "value": 8.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[10.0],
        num_episodes=1,
        learning_rate=1.0,
        discount_factor=0.0,
        epsilon=0.0,
        rng=random.Random(123),
    )

    assert result["agents"]["A"].get_q_value("default", 10.0) == pytest.approx(0.0)
    assert result["agents"]["B"].get_q_value("default", 10.0) == pytest.approx(2.4)


def test_train_multi_agent_q_learning_is_deterministic_with_seeded_rng():
    first = train_multi_agent_q_learning(
        bidder_specs=[
            {"id": "A", "value": 10.0},
            {"id": "B", "value": 8.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 10.0],
        num_episodes=3,
        epsilon=1.0,
        rng=random.Random(123),
    )
    second = train_multi_agent_q_learning(
        bidder_specs=[
            {"id": "A", "value": 10.0},
            {"id": "B", "value": 8.0},
        ],
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 10.0],
        num_episodes=3,
        epsilon=1.0,
        rng=random.Random(123),
    )

    assert first["history"] == second["history"]


def test_train_multi_agent_q_learning_does_not_mutate_bidder_specs():
    bidder_specs = [
        {"id": "A", "value": 10.0},
        {"id": "B", "value": 8.0},
    ]
    original_bidder_specs = [dict(bidder_spec) for bidder_spec in bidder_specs]

    train_multi_agent_q_learning(
        bidder_specs=bidder_specs,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 10.0],
        num_episodes=3,
        rng=random.Random(123),
    )

    assert bidder_specs == original_bidder_specs


def test_train_multi_agent_q_learning_with_zero_episodes_returns_empty_history():
    result = train_multi_agent_q_learning(
        bidder_specs=[{"id": "A", "value": 10.0}],
        ctrs=[0.6],
        candidate_bids=[0.0, 10.0],
        num_episodes=0,
        rng=random.Random(123),
    )

    assert set(result["agents"]) == {"A"}
    assert result["history"] == []


def test_train_multi_agent_q_learning_rejects_empty_candidate_bids():
    with pytest.raises(ValueError, match="candidate_bids"):
        train_multi_agent_q_learning(
            bidder_specs=[{"id": "A", "value": 10.0}],
            ctrs=[0.6],
            candidate_bids=[],
            num_episodes=1,
        )


def test_train_multi_agent_q_learning_rejects_negative_num_episodes():
    with pytest.raises(ValueError, match="num_episodes"):
        train_multi_agent_q_learning(
            bidder_specs=[{"id": "A", "value": 10.0}],
            ctrs=[0.6],
            candidate_bids=[0.0, 10.0],
            num_episodes=-1,
        )

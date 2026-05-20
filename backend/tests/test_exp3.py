import random

import pytest

from auctioneer.agents.exp3 import EXP3Bidder


def test_select_bid_returns_a_candidate():
    agent = EXP3Bidder(gamma=0.1, rng=random.Random(0))
    bid = agent.select_bid([5.0, 8.0, 10.0])

    assert bid in [5.0, 8.0, 10.0]


def test_select_bid_is_deterministic_with_seeded_rng():
    first = EXP3Bidder(gamma=0.1, rng=random.Random(42)).select_bid([5.0, 8.0, 10.0])
    second = EXP3Bidder(gamma=0.1, rng=random.Random(42)).select_bid([5.0, 8.0, 10.0])

    assert first == second


def test_probabilities_sum_to_one():
    agent = EXP3Bidder(gamma=0.1)
    probs = agent.probabilities([5.0, 8.0, 10.0])

    assert sum(probs) == pytest.approx(1.0)


def test_probabilities_are_uniform_before_any_updates():
    # All weights start at 1.0, so before any updates the distribution is uniform.
    agent = EXP3Bidder(gamma=0.0)
    probs = agent.probabilities([5.0, 8.0, 10.0])

    assert probs[0] == pytest.approx(1 / 3)
    assert probs[1] == pytest.approx(1 / 3)
    assert probs[2] == pytest.approx(1 / 3)


def test_probabilities_with_full_exploration_are_uniform():
    # gamma=1 forces pure uniform exploration regardless of weights.
    agent = EXP3Bidder(gamma=1.0)
    agent.weights[5.0] = 100.0
    probs = agent.probabilities([5.0, 8.0, 10.0])

    assert probs[0] == pytest.approx(1 / 3)
    assert probs[1] == pytest.approx(1 / 3)
    assert probs[2] == pytest.approx(1 / 3)


def test_update_increases_weight_after_positive_reward():
    agent = EXP3Bidder(gamma=0.1, rng=random.Random(0))
    initial_weight = agent._get_weight(8.0)

    agent.update(bid=8.0, reward=5.0, candidate_bids=[5.0, 8.0, 10.0])

    assert agent._get_weight(8.0) > initial_weight


def test_update_does_not_change_other_weights():
    agent = EXP3Bidder(gamma=0.1, rng=random.Random(0))

    agent.update(bid=8.0, reward=5.0, candidate_bids=[5.0, 8.0, 10.0])

    # Only the chosen bid's weight is updated; others stay at the default 1.0.
    assert agent._get_weight(5.0) == pytest.approx(1.0)
    assert agent._get_weight(10.0) == pytest.approx(1.0)


def test_best_bid_returns_highest_weight_bid():
    agent = EXP3Bidder(gamma=0.1)
    agent.weights[5.0] = 1.0
    agent.weights[8.0] = 5.0
    agent.weights[10.0] = 2.0

    assert agent.best_bid([5.0, 8.0, 10.0]) == pytest.approx(8.0)


def test_best_bid_defaults_to_first_when_all_weights_equal():
    agent = EXP3Bidder(gamma=0.1)

    # All weights default to 1.0; max() returns the first maximum found.
    assert agent.best_bid([5.0, 8.0, 10.0]) == pytest.approx(5.0)


def test_repeated_positive_rewards_shift_probability_toward_that_bid():
    agent = EXP3Bidder(gamma=0.1, rng=random.Random(0))

    # Repeatedly reward bid 8.0 and check that its probability rises.
    for _ in range(20):
        agent.update(bid=8.0, reward=3.0, candidate_bids=[5.0, 8.0, 10.0])

    probs = agent.probabilities([5.0, 8.0, 10.0])
    assert probs[1] > probs[0]
    assert probs[1] > probs[2]

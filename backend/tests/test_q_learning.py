import random

import pytest

from auctioneer.agents.q_learning import QLearningBidder


class ChoiceRng:
    def random(self):
        return 0.0

    def choice(self, candidates):
        return candidates[-1]


def test_get_q_value_defaults_to_zero():
    bidder = QLearningBidder()

    assert bidder.get_q_value("default", 1.0) == pytest.approx(0.0)


def test_get_q_value_returns_stored_value():
    bidder = QLearningBidder()
    bidder.q_table[("default", 2.0)] = 1.25

    assert bidder.get_q_value("default", 2.0) == pytest.approx(1.25)


def test_select_bid_with_zero_epsilon_chooses_highest_q_value():
    bidder = QLearningBidder(epsilon=0.0, rng=random.Random(123))
    bidder.q_table[("default", 1.0)] = 0.5
    bidder.q_table[("default", 2.0)] = 1.5
    bidder.q_table[("default", 3.0)] = 1.0

    assert bidder.select_bid("default", [1.0, 2.0, 3.0]) == pytest.approx(2.0)


def test_select_bid_keeps_first_bid_when_q_values_tie():
    bidder = QLearningBidder(epsilon=0.0, rng=random.Random(123))
    bidder.q_table[("default", 1.0)] = 1.0
    bidder.q_table[("default", 2.0)] = 1.0

    assert bidder.select_bid("default", [1.0, 2.0]) == pytest.approx(1.0)


def test_select_bid_with_full_exploration_uses_random_choice():
    bidder = QLearningBidder(epsilon=1.0, rng=ChoiceRng())

    assert bidder.select_bid("default", [1.0, 2.0, 3.0]) == pytest.approx(3.0)


def test_update_increases_q_value_after_positive_reward():
    bidder = QLearningBidder(
        learning_rate=0.5,
        discount_factor=0.0,
        epsilon=0.0,
        rng=random.Random(123),
    )

    new_q = bidder.update(
        state="default",
        bid=2.0,
        reward=4.0,
        next_state="default",
        candidate_bids=[1.0, 2.0, 3.0],
    )

    assert new_q == pytest.approx(2.0)
    assert bidder.get_q_value("default", 2.0) == pytest.approx(2.0)


def test_update_uses_best_future_q_value():
    bidder = QLearningBidder(
        learning_rate=1.0,
        discount_factor=0.5,
        epsilon=0.0,
        rng=random.Random(123),
    )
    bidder.q_table[("next", 1.0)] = 2.0
    bidder.q_table[("next", 2.0)] = 4.0
    bidder.q_table[("next", 3.0)] = 1.0

    new_q = bidder.update(
        state="default",
        bid=2.0,
        reward=3.0,
        next_state="next",
        candidate_bids=[1.0, 2.0, 3.0],
    )

    assert new_q == pytest.approx(5.0)

import random


class QLearningBidder:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1, rng=None):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table = {}
        self.rng = rng if rng is not None else random.Random()

    def get_q_value(self, state, bid):
        # Unknown state-action pairs start with neutral value.
        return self.q_table.get((state, bid), 0.0)

    def select_bid(self, state, candidate_bids):
        # Epsilon-greedy exploration: sometimes try a random bid.
        if self.rng.random() < self.epsilon:
            return self.rng.choice(candidate_bids)

        best_bid = None
        best_q_value = None

        # Otherwise exploit the best known bid, keeping the first bid on ties.
        for bid in candidate_bids:
            q_value = self.get_q_value(state, bid)

            if best_q_value is None or q_value > best_q_value:
                best_bid = bid
                best_q_value = q_value

        return best_bid

    def update(self, state, bid, reward, next_state, candidate_bids):
        old_q = self.get_q_value(state, bid)

        # Q-learning bootstraps from the best known future action.
        next_max_q = max(
            (self.get_q_value(next_state, next_bid) for next_bid in candidate_bids),
            default=0.0,
        )

        target = reward + self.discount_factor * next_max_q
        new_q = old_q + self.learning_rate * (target - old_q)

        self.q_table[(state, bid)] = new_q
        return new_q

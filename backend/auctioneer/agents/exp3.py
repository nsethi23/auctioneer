import math
import random


class EXP3Bidder:
    """Exponential-weights bandit bidder for GSP auctions.

    EXP3 minimizes regret against an adversary by maintaining a weight for each
    candidate bid and sampling proportionally, blended with uniform exploration.
    Unlike Q-learning it makes no stationarity assumption — the weight update is
    purely multiplicative and does not bootstrap from future states.
    """

    def __init__(self, gamma=0.1, rng=None):
        # gamma controls the exploration-exploitation tradeoff.
        # Higher gamma = more uniform; lower gamma = more weight-proportional.
        self.gamma = gamma
        self.weights = {}
        self.rng = rng if rng is not None else random.Random()

    def _get_weight(self, bid):
        # Unseen bids start with weight 1.0 so all actions begin equally likely.
        return self.weights.get(bid, 1.0)

    def probabilities(self, candidate_bids):
        k = len(candidate_bids)
        total_weight = sum(self._get_weight(bid) for bid in candidate_bids)
        # Blend weight-proportional exploitation with uniform exploration.
        return [
            (1 - self.gamma) * self._get_weight(bid) / total_weight + self.gamma / k
            for bid in candidate_bids
        ]

    def select_bid(self, candidate_bids):
        probs = self.probabilities(candidate_bids)
        # Weighted random draw via cumulative probabilities.
        r = self.rng.random()
        cumulative = 0.0
        for bid, prob in zip(candidate_bids, probs):
            cumulative += prob
            if r <= cumulative:
                return bid
        # Floating-point guard: return last bid if cumulative falls just short of 1.
        return candidate_bids[-1]

    def best_bid(self, candidate_bids):
        # At evaluation time, pick the bid with the highest accumulated weight.
        return max(candidate_bids, key=self._get_weight)

    def best_weight(self, candidate_bids):
        return self._get_weight(self.best_bid(candidate_bids))

    def update(self, bid, reward, candidate_bids):
        probs = self.probabilities(candidate_bids)
        k = len(candidate_bids)
        prob_of_bid = probs[candidate_bids.index(bid)]

        # Importance-weighted reward removes the sampling bias introduced by the
        # mixed strategy — bids chosen less often get a proportionally larger update.
        importance_weighted = reward / prob_of_bid

        # Multiplicative weight update: bids that earned high reward grow heavier.
        self.weights[bid] = self._get_weight(bid) * math.exp(
            self.gamma * importance_weighted / k
        )
        return self.weights[bid]

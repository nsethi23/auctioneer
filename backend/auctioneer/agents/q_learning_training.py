import random

from auctioneer.agents.q_learning import QLearningBidder
from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.metrics.allocations import get_bidder_utility


def train_q_learning_bidder(
    bidder_id,
    value,
    other_bidders,
    ctrs,
    candidate_bids,
    num_episodes,
    learning_rate=0.1,
    discount_factor=0.0,
    epsilon=0.1,
    rng=None,
):
    if rng is None:
        rng = random.Random()

    agent = QLearningBidder(
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        epsilon=epsilon,
        rng=rng,
    )

    # Keep the first training environment one-state; richer states come later.
    state = "default"
    next_state = "default"

    history = []

    for episode in range(num_episodes):
        bid = agent.select_bid(state, candidate_bids)
        bidder = {"id": bidder_id, "value": value, "bid": bid}
        auction_result = run_gsp_auction(other_bidders + [bidder], ctrs)

        # Reward is the bidder's realized utility from the auction.
        reward = get_bidder_utility(auction_result, bidder_id)

        q_value = agent.update(state, bid, reward, next_state, candidate_bids)

        history.append(
            {
                "episode": episode,
                "state": state,
                "bid": bid,
                "reward": reward,
                "q_value": q_value,
            }
        )

    return {
        "agent": agent,
        "history": history,
    }

import random

from auctioneer.agents.q_learning import QLearningBidder
from auctioneer.auctions.gsp import run_gsp_auction
from auctioneer.metrics.allocations import get_bidder_utility


def train_multi_agent_q_learning(
    bidder_specs,
    ctrs,
    candidate_bids,
    num_episodes,
    learning_rate=0.1,
    discount_factor=0.0,
    epsilon=0.1,
    rng=None,
):
    if not candidate_bids:
        raise ValueError("candidate_bids must not be empty")

    if num_episodes < 0:
        raise ValueError("num_episodes must be non-negative")

    if rng is None:
        rng = random.Random()

    agents = {}
    for bidder_spec in bidder_specs:
        agents[bidder_spec["id"]] = QLearningBidder(
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            epsilon=epsilon,
            rng=rng,
        )

    # Keep the first multi-agent learner one-state so the only learned choice is bid level.
    state = "default"
    next_state = "default"
    history = []

    for episode in range(num_episodes):
        bids = {}
        bidders = []

        for bidder_spec in bidder_specs:
            bidder_id = bidder_spec["id"]
            bid = agents[bidder_id].select_bid(state, candidate_bids)
            bids[bidder_id] = bid
            bidders.append(
                {
                    "id": bidder_id,
                    "value": bidder_spec["value"],
                    "bid": bid,
                }
            )

        auction_result = run_gsp_auction(bidders, ctrs)

        rewards = {}
        q_values = {}

        for bidder_spec in bidder_specs:
            bidder_id = bidder_spec["id"]
            reward = get_bidder_utility(auction_result, bidder_id)
            rewards[bidder_id] = reward

            # Each agent updates from its own reward while the others also learn.
            q_values[bidder_id] = agents[bidder_id].update(
                state=state,
                bid=bids[bidder_id],
                reward=reward,
                next_state=next_state,
                candidate_bids=candidate_bids,
            )

        history.append(
            {
                "episode": episode,
                "bids": bids,
                "rewards": rewards,
                "q_values": q_values,
                "revenue": auction_result["revenue"],
                "welfare": auction_result["welfare"],
                "bidder_surplus": auction_result["bidder_surplus"],
            }
        )

    return {
        "agents": agents,
        "history": history,
    }

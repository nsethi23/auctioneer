import random

from auctioneer.agents.strategies import truthful_bid


def generate_bidders(
    num_bidders,
    min_value,
    max_value,
    rng=None,
    strategy=truthful_bid,
    strategy_kwargs=None,
):
    if rng is None:
        rng = random.Random()

    if strategy_kwargs is None:
        strategy_kwargs = {}

    bidders = []

    for i in range(num_bidders):
        # Sample each advertiser's private value from the configured market range.
        value = rng.uniform(min_value, max_value)

        # Convert private value into an actual bid using the selected strategy.
        bidders.append(
            {
                "id": f"B{i}",
                "value": value,
                "bid": strategy(value, **strategy_kwargs),
            }
        )

    return bidders


def generate_ctrs(num_slots, top_ctr, decay):
    ctrs = []

    for i in range(num_slots):
        # Model lower ad slots as progressively less likely to receive clicks.
        ctrs.append(top_ctr * (decay**i))

    return ctrs

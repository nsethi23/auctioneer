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
    if num_slots < 0:
        raise ValueError("num_slots must be non-negative")

    if top_ctr < 0 or top_ctr > 1:
        raise ValueError("top_ctr must be between 0 and 1")

    if decay < 0 or decay > 1:
        raise ValueError("decay must be between 0 and 1")

    ctrs = []

    for i in range(num_slots):
        # Model lower ad slots as progressively less likely to receive clicks.
        ctrs.append(top_ctr * (decay**i))

    return ctrs


def generate_bidders_from_profiles(profiles, rng=None):
    if rng is None:
        rng = random.Random()

    bidders = []

    for profile in profiles:
        # Each profile owns its value range and bidding strategy.
        value = rng.uniform(profile["min_value"], profile["max_value"])
        strategy = profile["strategy"]
        strategy_kwargs = profile.get("strategy_kwargs", {})
        strategy_name = profile.get("strategy_name", strategy.__name__)
        bid = strategy(value, **strategy_kwargs)

        # Keep the strategy label so later metrics can group outcomes by behavior.
        bidders.append(
            {
                "id": profile["id"],
                "value": value,
                "bid": bid,
                "strategy": strategy_name,
            }
        )

    return bidders

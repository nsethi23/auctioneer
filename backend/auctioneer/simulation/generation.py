import random


def generate_bidders(num_bidders, min_value, max_value, rng=None):
    if rng is None:
        rng = random.Random()

    bidders = []

    for i in range(num_bidders):
        # Sample each advertiser's private value from the configured market range.
        value = rng.uniform(min_value, max_value)

        # Start with truthful bidders; strategic bid shading comes in later agents.
        bidders.append(
            {
                "id": f"B{i}",
                "value": value,
                "bid": value,
            }
        )

    return bidders

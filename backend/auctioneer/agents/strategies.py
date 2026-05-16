def truthful_bid(value):
    # Truthful bidding reports the advertiser's private value directly.
    return value


def shaded_bid(value, shade_factor):
    if shade_factor < 0 or shade_factor > 1:
        raise ValueError("shade_factor must be between 0 and 1")

    # Bid shading models strategic underbidding to preserve bidder surplus.
    return value * shade_factor

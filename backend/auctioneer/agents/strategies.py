def truthful_bid(value):
    # Truthful bidding reports the advertiser's private value directly.
    return value


def shaded_bid(value, shade_factor):
    # Bid shading models strategic underbidding to preserve bidder surplus.
    return value * shade_factor

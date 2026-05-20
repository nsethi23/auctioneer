import random

import pytest

from auctioneer.agents.strategies import shaded_bid, truthful_bid
from auctioneer.simulation.generation import (
    generate_bidders,
    generate_bidders_from_profiles,
    generate_ctrs,
)


def test_generate_bidders_returns_requested_count():
    bidders = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))

    assert len(bidders) == 3


def test_generate_bidders_uses_expected_ids():
    bidders = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))

    assert bidders[0]["id"] == "B0"
    assert bidders[1]["id"] == "B1"
    assert bidders[2]["id"] == "B2"


def test_generate_bidders_values_are_within_range():
    bidders = generate_bidders(20, 1.0, 10.0, rng=random.Random(123))

    for bidder in bidders:
        assert 1.0 <= bidder["value"] <= 10.0


def test_generate_bidders_bids_truthfully_by_default():
    bidders = generate_bidders(20, 1.0, 10.0, rng=random.Random(123))

    for bidder in bidders:
        assert bidder["bid"] == bidder["value"]


def test_generate_bidders_accepts_shaded_strategy():
    bidders = generate_bidders(
        3,
        10.0,
        10.0,
        rng=random.Random(123),
        strategy=shaded_bid,
        strategy_kwargs={"shade_factor": 0.8},
    )

    for bidder in bidders:
        assert bidder["value"] == pytest.approx(10.0)
        assert bidder["bid"] == pytest.approx(8.0)


def test_generate_bidders_accepts_strategy_kwargs():
    bidders = generate_bidders(
        1,
        10.0,
        10.0,
        rng=random.Random(123),
        strategy=shaded_bid,
        strategy_kwargs={"shade_factor": 0.25},
    )

    assert bidders[0]["value"] == pytest.approx(10.0)
    assert bidders[0]["bid"] == pytest.approx(2.5)


def test_generate_bidders_is_deterministic_with_seeded_rng():
    first = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))
    second = generate_bidders(3, 1.0, 10.0, rng=random.Random(123))

    assert first == second


def test_generate_ctrs_returns_requested_count():
    ctrs = generate_ctrs(num_slots=3, top_ctr=0.6, decay=0.5)

    assert len(ctrs) == 3


def test_generate_ctrs_applies_decay_per_slot():
    ctrs = generate_ctrs(num_slots=3, top_ctr=0.6, decay=0.5)

    assert ctrs[0] == pytest.approx(0.6)
    assert ctrs[1] == pytest.approx(0.3)
    assert ctrs[2] == pytest.approx(0.15)


def test_generate_ctrs_with_zero_slots_returns_empty_list():
    assert generate_ctrs(num_slots=0, top_ctr=0.6, decay=0.5) == []


def test_generate_ctrs_rejects_negative_num_slots():
    with pytest.raises(ValueError, match="num_slots"):
        generate_ctrs(num_slots=-1, top_ctr=0.6, decay=0.5)


def test_generate_ctrs_rejects_top_ctr_below_zero():
    with pytest.raises(ValueError, match="top_ctr"):
        generate_ctrs(num_slots=3, top_ctr=-0.1, decay=0.5)


def test_generate_ctrs_rejects_top_ctr_above_one():
    with pytest.raises(ValueError, match="top_ctr"):
        generate_ctrs(num_slots=3, top_ctr=1.1, decay=0.5)


def test_generate_ctrs_rejects_decay_below_zero():
    with pytest.raises(ValueError, match="decay"):
        generate_ctrs(num_slots=3, top_ctr=0.6, decay=-0.1)


def test_generate_ctrs_rejects_decay_above_one():
    with pytest.raises(ValueError, match="decay"):
        generate_ctrs(num_slots=3, top_ctr=0.6, decay=1.1)


def test_generate_bidders_from_profiles_preserves_profile_ids():
    profiles = [
        {
            "id": "A",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        },
        {
            "id": "B",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_kwargs": {"shade_factor": 0.8},
        },
    ]

    bidders = generate_bidders_from_profiles(profiles, rng=random.Random(123))

    assert bidders[0]["id"] == "A"
    assert bidders[1]["id"] == "B"


def test_generate_bidders_from_profiles_applies_profile_strategies():
    profiles = [
        {
            "id": "truthful",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        },
        {
            "id": "shaded",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_kwargs": {"shade_factor": 0.8},
        },
    ]

    bidders = generate_bidders_from_profiles(profiles, rng=random.Random(123))

    assert bidders[0]["value"] == pytest.approx(10.0)
    assert bidders[0]["bid"] == pytest.approx(10.0)
    assert bidders[1]["value"] == pytest.approx(10.0)
    assert bidders[1]["bid"] == pytest.approx(8.0)


def test_generate_bidders_from_profiles_preserves_explicit_strategy_names():
    profiles = [
        {
            "id": "A",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
            "strategy_name": "truthful",
        },
        {
            "id": "B",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_name": "shaded",
            "strategy_kwargs": {"shade_factor": 0.8},
        },
    ]

    bidders = generate_bidders_from_profiles(profiles, rng=random.Random(123))

    assert bidders[0]["strategy"] == "truthful"
    assert bidders[1]["strategy"] == "shaded"


def test_generate_bidders_from_profiles_defaults_strategy_name_to_function_name():
    profiles = [
        {
            "id": "A",
            "min_value": 10.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        }
    ]

    bidders = generate_bidders_from_profiles(profiles, rng=random.Random(123))

    assert bidders[0]["strategy"] == "truthful_bid"


def test_generate_bidders_lognormal_produces_positive_values():
    # Log-normal is only defined for positive inputs; all values must be > 0.
    bidders = generate_bidders(
        50, 1.0, 10.0, rng=random.Random(42), distribution="lognormal"
    )

    for bidder in bidders:
        assert bidder["value"] > 0


def test_generate_bidders_lognormal_is_deterministic_with_seeded_rng():
    first = generate_bidders(
        10, 1.0, 10.0, rng=random.Random(42), distribution="lognormal"
    )
    second = generate_bidders(
        10, 1.0, 10.0, rng=random.Random(42), distribution="lognormal"
    )

    assert first == second


def test_generate_bidders_lognormal_median_near_geometric_mean():
    # With sigma = (ln(max) - ln(min)) / 4, the median of the log-normal equals
    # exp(mu) = sqrt(min_value * max_value), the geometric mean of the range.
    import math

    bidders = generate_bidders(
        500, 1.0, 100.0, rng=random.Random(0), distribution="lognormal"
    )
    values = sorted(b["value"] for b in bidders)
    median = values[len(values) // 2]
    geometric_mean = math.sqrt(1.0 * 100.0)

    # Median should be within 30% of the geometric mean over 500 samples.
    assert abs(median - geometric_mean) / geometric_mean < 0.3


def test_generate_bidders_rejects_unknown_distribution():
    with pytest.raises(ValueError, match="unknown distribution"):
        generate_bidders(3, 1.0, 10.0, rng=random.Random(0), distribution="power_law")


def test_generate_bidders_from_profiles_is_deterministic_with_seeded_rng():
    profiles = [
        {
            "id": "A",
            "min_value": 1.0,
            "max_value": 10.0,
            "strategy": truthful_bid,
        },
        {
            "id": "B",
            "min_value": 1.0,
            "max_value": 10.0,
            "strategy": shaded_bid,
            "strategy_kwargs": {"shade_factor": 0.8},
        },
    ]

    first = generate_bidders_from_profiles(profiles, rng=random.Random(123))
    second = generate_bidders_from_profiles(profiles, rng=random.Random(123))

    assert first == second

import pytest

from auctioneer.simulation.strategy_profiles import compare_truthful_and_shaded


def test_compare_truthful_and_shaded_returns_both_profiles():
    result = compare_truthful_and_shaded(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        shade_factor=0.8,
        seed=123,
    )

    assert "truthful" in result
    assert "shaded" in result
    assert "difference" in result


def test_compare_truthful_and_shaded_is_deterministic_with_seed():
    first = compare_truthful_and_shaded(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        shade_factor=0.8,
        seed=123,
    )
    second = compare_truthful_and_shaded(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        shade_factor=0.8,
        seed=123,
    )

    assert first == second


def test_compare_truthful_and_shaded_reports_gsp_differences():
    result = compare_truthful_and_shaded(
        num_auctions=1,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=10.0,
        max_value=10.0,
        shade_factor=0.5,
        seed=123,
    )

    assert result["truthful"]["averages"]["gsp"]["revenue"] == pytest.approx(9.0)
    assert result["shaded"]["averages"]["gsp"]["revenue"] == pytest.approx(4.5)
    assert result["difference"]["gsp"]["revenue"] == pytest.approx(-4.5)


def test_compare_truthful_and_shaded_includes_mechanism_difference_metrics():
    result = compare_truthful_and_shaded(
        num_auctions=5,
        num_bidders=3,
        ctrs=[0.6, 0.3],
        min_value=1.0,
        max_value=10.0,
        shade_factor=0.8,
        seed=123,
    )

    for mechanism in ["gsp", "vcg"]:
        assert "revenue" in result["difference"][mechanism]
        assert "welfare" in result["difference"][mechanism]
        assert "bidder_surplus" in result["difference"][mechanism]

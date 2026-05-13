import pytest

from auctioneer.simulation.comparison import compare_gsp_and_vcg


def test_compare_gsp_and_vcg_three_bidders_two_slots():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    ctrs = [0.6, 0.3]

    result = compare_gsp_and_vcg(bidders, ctrs)

    assert result["gsp"]["revenue"] == pytest.approx(6.3)
    assert result["vcg"]["revenue"] == pytest.approx(5.4)
    assert result["difference"]["revenue"] == pytest.approx(0.9)

    assert result["gsp"]["welfare"] == pytest.approx(8.4)
    assert result["vcg"]["welfare"] == pytest.approx(8.4)
    assert result["difference"]["welfare"] == pytest.approx(0.0)

    assert result["gsp"]["bidder_surplus"] == pytest.approx(2.1)
    assert result["vcg"]["bidder_surplus"] == pytest.approx(3.0)
    assert result["difference"]["bidder_surplus"] == pytest.approx(-0.9)

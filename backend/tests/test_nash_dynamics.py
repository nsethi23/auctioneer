import pytest

from auctioneer.agents.nash_dynamics import run_best_response_dynamics


def test_run_best_response_dynamics_converges_from_non_equilibrium_profile():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = run_best_response_dynamics(
        bidders=bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
        max_rounds=5,
    )

    assert result["converged"] is True
    assert result["rounds_run"] == 2
    assert result["history"][0]["is_equilibrium"] is False
    assert result["history"][-1]["is_equilibrium"] is True
    assert result["final_bidders"] == [
        {"id": "A", "value": 10.0, "bid": 5.0},
        {"id": "B", "value": 8.0, "bid": 5.0},
        {"id": "C", "value": 5.0, "bid": 0.0},
    ]


def test_run_best_response_dynamics_stops_immediately_when_already_equilibrium():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 6.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = run_best_response_dynamics(
        bidders=bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
        max_rounds=5,
    )

    assert result["converged"] is True
    assert result["rounds_run"] == 0
    assert len(result["history"]) == 1
    assert result["final_bidders"] == bidders


def test_run_best_response_dynamics_does_not_mutate_input_bidders():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]
    original_bidders = [dict(bidder) for bidder in bidders]

    run_best_response_dynamics(
        bidders=bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
        max_rounds=5,
    )

    assert bidders == original_bidders


def test_run_best_response_dynamics_with_zero_rounds_only_records_initial_state():
    bidders = [
        {"id": "A", "value": 10.0, "bid": 10.0},
        {"id": "B", "value": 8.0, "bid": 8.0},
        {"id": "C", "value": 5.0, "bid": 5.0},
    ]

    result = run_best_response_dynamics(
        bidders=bidders,
        ctrs=[0.6, 0.3],
        candidate_bids=[0.0, 5.0, 6.0, 8.0, 10.0],
        max_rounds=0,
    )

    assert result["converged"] is False
    assert result["rounds_run"] == 0
    assert len(result["history"]) == 1
    assert result["final_bidders"] == bidders


def test_run_best_response_dynamics_rejects_empty_candidate_bids():
    with pytest.raises(ValueError, match="candidate_bids"):
        run_best_response_dynamics(
            bidders=[{"id": "A", "value": 10.0, "bid": 10.0}],
            ctrs=[0.6],
            candidate_bids=[],
            max_rounds=5,
        )


def test_run_best_response_dynamics_rejects_negative_max_rounds():
    with pytest.raises(ValueError, match="max_rounds"):
        run_best_response_dynamics(
            bidders=[{"id": "A", "value": 10.0, "bid": 10.0}],
            ctrs=[0.6],
            candidate_bids=[0.0, 10.0],
            max_rounds=-1,
        )

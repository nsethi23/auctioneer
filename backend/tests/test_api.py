from fastapi.testclient import TestClient
import pytest

from auctioneer.api.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auction_compare_returns_gsp_vcg_and_difference():
    response = client.post(
        "/auction/compare",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert "gsp" in body
    assert "vcg" in body
    assert "difference" in body
    assert body["gsp"]["revenue"] == pytest.approx(6.3)
    assert body["vcg"]["revenue"] == pytest.approx(5.4)


def test_auction_compare_accepts_optional_bidder_fields():
    response = client.post(
        "/auction/compare",
        json={
            "bidders": [
                {
                    "id": "A",
                    "value": 10.0,
                    "bid": 10.0,
                    "quality_score": 1.2,
                    "strategy": "truthful",
                },
                {
                    "id": "B",
                    "value": 8.0,
                    "bid": 8.0,
                    "quality_score": 1.0,
                    "strategy": "shaded",
                },
            ],
            "ctrs": [0.6, 0.3],
        },
    )

    assert response.status_code == 200
    assert response.json()["gsp"]["allocations"][0]["bidder_id"] == "A"


def test_auction_compare_rejects_missing_required_body_fields():
    response = client.post(
        "/auction/compare",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
            ],
        },
    )

    assert response.status_code == 422


def test_auction_compare_rejects_invalid_bidder_shape():
    response = client.post(
        "/auction/compare",
        json={
            "bidders": [
                {"id": "A", "value": 10.0},
            ],
            "ctrs": [0.6],
        },
    )

    assert response.status_code == 422


def test_gsp_endpoint_runs_gsp_auction():
    response = client.post(
        "/auction/gsp",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
        },
    )

    assert response.status_code == 200
    assert response.json()["revenue"] == pytest.approx(6.3)
    assert response.json()["welfare"] == pytest.approx(8.4)


def test_gsp_endpoint_accepts_reserve_and_quality_scores():
    response = client.post(
        "/auction/gsp",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0, "quality_score": 1.0},
                {"id": "B", "value": 8.0, "bid": 7.0, "quality_score": 2.0},
            ],
            "ctrs": [0.6, 0.3],
            "reserve_price": 6.0,
            "use_quality_scores": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["allocations"][0]["bidder_id"] == "B"
    assert response.json()["allocations"][0]["payment"] == pytest.approx(3.6)


def test_vcg_endpoint_runs_vcg_auction():
    response = client.post(
        "/auction/vcg",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
        },
    )

    assert response.status_code == 200
    assert response.json()["revenue"] == pytest.approx(5.4)
    assert response.json()["welfare"] == pytest.approx(8.4)


def test_vcg_endpoint_accepts_reserve_price():
    response = client.post(
        "/auction/vcg",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
            "reserve_price": 6.0,
        },
    )

    assert response.status_code == 200
    assert len(response.json()["allocations"]) == 1
    assert response.json()["revenue"] == pytest.approx(3.6)


def test_price_of_anarchy_endpoint_returns_efficiency_metrics():
    response = client.post(
        "/metrics/price-of-anarchy",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 1.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["optimal_welfare"] == pytest.approx(8.4)
    assert body["strategic_welfare"] == pytest.approx(6.3)
    assert body["price_of_anarchy"] == pytest.approx(8.4 / 6.3)
    assert body["welfare_loss"] == pytest.approx(2.1)


def test_price_of_anarchy_endpoint_rejects_missing_ctrs():
    response = client.post(
        "/metrics/price-of-anarchy",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
            ],
        },
    )

    assert response.status_code == 422


def test_nash_check_returns_equilibrium_status_and_deviations():
    response = client.post(
        "/nash/check",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
            "candidate_bids": [0.0, 5.0, 6.0, 8.0, 10.0],
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["is_equilibrium"] is False
    assert body["max_utility_gain"] == pytest.approx(0.3)
    assert body["deviations"][0]["bidder_id"] == "A"
    assert body["deviations"][0]["best_bid"] == pytest.approx(5.0)


def test_nash_check_accepts_custom_tolerance():
    response = client.post(
        "/nash/check",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
            "candidate_bids": [0.0, 5.0, 6.0, 8.0, 10.0],
            "tolerance": 1.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_equilibrium"] is True


def test_nash_check_rejects_missing_candidate_bids():
    response = client.post(
        "/nash/check",
        json={
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
            ],
            "ctrs": [0.6],
        },
    )

    assert response.status_code == 422


def test_best_response_endpoint_returns_best_bid_and_candidate_results():
    response = client.post(
        "/best-response",
        json={
            "bidder_id": "A",
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
            "candidate_bids": [0.0, 5.0, 6.0, 8.0, 10.0],
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["bid"] == pytest.approx(5.0)
    assert body["utility"] == pytest.approx(1.5)
    assert len(body["results"]) == 5


def test_best_response_endpoint_rejects_unknown_bidder_id():
    response = client.post(
        "/best-response",
        json={
            "bidder_id": "Z",
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
            ],
            "ctrs": [0.6],
            "candidate_bids": [0.0, 10.0],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "bidder_id must match one of the bidders"


def test_best_response_curve_endpoint_returns_value_sweep():
    response = client.post(
        "/best-response/curve",
        json={
            "bidder_id": "A",
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
            "values": [4.0, 10.0],
            "candidate_bids": [0.0, 5.0, 6.0, 8.0, 10.0],
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["bidder_id"] == "A"
    assert body["values"] == [4.0, 10.0]
    assert body["candidate_bids"] == [0.0, 5.0, 6.0, 8.0, 10.0]
    assert len(body["curve"]) == 2
    assert body["curve"][1]["best_bid"] == pytest.approx(5.0)


def test_best_response_curve_endpoint_rejects_unknown_bidder_id():
    response = client.post(
        "/best-response/curve",
        json={
            "bidder_id": "Z",
            "bidders": [
                {"id": "A", "value": 10.0, "bid": 10.0},
            ],
            "ctrs": [0.6],
            "values": [10.0],
            "candidate_bids": [0.0, 10.0],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "bidder_id must match one of the bidders"


def test_rl_convergence_returns_best_response_checkpoints_and_history():
    response = client.post(
        "/rl/convergence",
        json={
            "bidder_id": "A",
            "value": 10.0,
            "other_bidders": [
                {"id": "B", "value": 8.0, "bid": 8.0},
                {"id": "C", "value": 5.0, "bid": 5.0},
            ],
            "ctrs": [0.6, 0.3],
            "candidate_bids": [5.0],
            "num_episodes": 3,
            "checkpoint_interval": 1,
            "learning_rate": 0.1,
            "discount_factor": 0.0,
            "epsilon": 0.0,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["best_response"]["bid"] == pytest.approx(5.0)
    assert body["best_response"]["utility"] == pytest.approx(1.5)
    assert len(body["checkpoints"]) == 3
    assert len(body["history"]) == 3
    assert body["checkpoints"][0]["learned_bid"] == pytest.approx(5.0)


def test_rl_convergence_accepts_default_learning_parameters():
    response = client.post(
        "/rl/convergence",
        json={
            "bidder_id": "A",
            "value": 10.0,
            "other_bidders": [
                {"id": "B", "value": 8.0, "bid": 8.0},
            ],
            "ctrs": [0.6],
            "candidate_bids": [0.0, 8.0, 10.0],
            "num_episodes": 2,
            "checkpoint_interval": 1,
        },
    )

    assert response.status_code == 200
    assert "best_response" in response.json()


def test_rl_convergence_rejects_missing_training_fields():
    response = client.post(
        "/rl/convergence",
        json={
            "bidder_id": "A",
            "value": 10.0,
            "other_bidders": [],
            "ctrs": [0.6],
            "candidate_bids": [0.0, 10.0],
            "num_episodes": 2,
        },
    )

    assert response.status_code == 422


def test_statistical_simulation_returns_confidence_metrics():
    response = client.post(
        "/simulation/statistical",
        json={
            "num_auctions": 5,
            "num_bidders": 3,
            "ctrs": [0.6, 0.3],
            "min_value": 1.0,
            "max_value": 10.0,
            "num_resamples": 20,
            "confidence": 0.8,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["num_auctions"] == 5
    assert body["confidence"] == pytest.approx(0.8)
    assert body["num_resamples"] == 20
    assert "gsp" in body["metrics"]
    assert "vcg" in body["metrics"]
    assert "difference" in body["metrics"]
    assert "mean" in body["metrics"]["gsp"]["revenue"]
    assert "lower" in body["metrics"]["gsp"]["revenue"]
    assert "upper" in body["metrics"]["gsp"]["revenue"]


def test_statistical_simulation_accepts_default_bootstrap_settings():
    response = client.post(
        "/simulation/statistical",
        json={
            "num_auctions": 2,
            "num_bidders": 2,
            "ctrs": [0.6],
            "min_value": 1.0,
            "max_value": 10.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["confidence"] == pytest.approx(0.95)
    assert response.json()["num_resamples"] == 1000


def test_statistical_simulation_rejects_missing_required_fields():
    response = client.post(
        "/simulation/statistical",
        json={
            "num_auctions": 5,
            "num_bidders": 3,
            "ctrs": [0.6, 0.3],
            "min_value": 1.0,
        },
    )

    assert response.status_code == 422

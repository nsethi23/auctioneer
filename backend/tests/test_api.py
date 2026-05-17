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

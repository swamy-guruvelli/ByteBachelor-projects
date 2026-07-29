from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_request_id():
    response = client.get("/health/ready", headers={"X-Request-ID": "lesson-1"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "lesson-1"
    assert response.json()["milestone"] == "contract-shell"


def test_planned_contract_is_explicit():
    response = client.get("/api/v1/planned")
    assert response.status_code == 501
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"].endswith("milestone-planned")


def test_missing_routes_use_problem_contract():
    response = client.get("/not-a-route")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"].endswith("http-404")
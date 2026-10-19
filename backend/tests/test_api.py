from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_and_all_five_scenarios():
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["docs"] == "/docs"
    assert client.get("/api/health").json()["status"] == "ok"
    scenarios = client.get("/api/scenarios").json()
    assert len(scenarios) == 5


def test_simulation_api_returns_decision_and_outcome():
    response = client.post(
        "/api/simulate",
        json={"scenario_id": "pedestrian_crossing", "policy": "safety_aware"},
    )
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["risk"]["risk_score"] <= 100
    assert body["action"] in {"continue", "slow_down", "brake", "stop"}
    assert body["decision_log"]
    assert body["timeline"]


def test_invalid_inputs_and_unknown_scenarios_are_reported():
    invalid_parameter = client.post(
        "/api/simulate",
        json={"scenario_id": "clear_road", "speed_kmh": 0},
    )
    unknown_scenario = client.post("/api/simulate", json={"scenario_id": "missing"})
    assert invalid_parameter.status_code == 422
    assert unknown_scenario.status_code == 404


def test_evaluation_and_csv_export():
    evaluation = client.post(
        "/api/evaluate",
        json={"scenario_ids": ["clear_road"], "episodes_per_scenario": 2, "seed": 7},
    )
    assert evaluation.status_code == 200
    body = evaluation.json()
    assert body["total_episodes_per_policy"] == 2
    assert set(body["metrics_by_policy"]) == {"baseline", "safety_aware"}
    assert len(body["episode_records"]) == 4
    exported = client.get("/api/results/export")
    assert exported.status_code == 200
    assert "text/csv" in exported.headers["content-type"]
    assert "policy" in exported.text


def test_evaluation_rejects_unknown_scenario_ids():
    response = client.post(
        "/api/evaluate",
        json={"scenario_ids": ["unknown"], "episodes_per_scenario": 1},
    )
    assert response.status_code == 404

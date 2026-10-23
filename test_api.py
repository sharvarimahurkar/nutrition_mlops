import os
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
PAYLOAD = dict(name="Test", age=45, gender="male", height_cm=172, weight_kg=88, activity_level=1,
               diet="non_vegetarian", goal="lose_weight", diseases=["diabetes", "hypertension"],
               wake_time="06:00", sleep_hours=6, water_litres=1.5, junk_food_per_week=6)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_plan_ok():
    r = client.post("/api/plan", json=PAYLOAD)
    assert r.status_code == 200
    j = r.json()
    assert j["assessment"]["risk_level"] in ("Low", "Moderate", "High")
    assert len(j["days"]) == 7 and len(j["guidance"]) == 2


def test_validation_error():
    r = client.post("/api/plan", json={**PAYLOAD, "age": 5})
    assert r.status_code == 422


def test_unknown_disease():
    assert client.post("/api/plan", json={**PAYLOAD, "diseases": ["xyz"]}).status_code == 422


def test_metrics_model_info_drift_and_frontend():
    assert "nutrition_requests_total" in client.get("/metrics").text
    assert client.get("/model-info").json()["best_model"]
    assert "status" in client.get("/drift").json()
    assert "NutriPlan" in client.get("/").text

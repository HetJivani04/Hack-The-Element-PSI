# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_get_region():
    response = client.get("/api/region")
    assert response.status_code == 200
    data = response.json()
    assert "region" in data
    assert "bounds" in data["region"]

def test_get_tools():
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_site_validation():
    response = client.get("/api/site/validate?lat=44.1&lon=-63.2")
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data

def test_job_submission():
    payload = {
        "tool_id": "lagrangian_tracking",
        "site": {"lat": 44.1, "lon": -63.2},
        "variables": {"sst": True, "salinity": False},
        "params": {"turbine_rating": 15.0, "rotor_diameter": 236, "hub_height": 150}
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"

def test_job_history():
    response = client.get("/api/jobs/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

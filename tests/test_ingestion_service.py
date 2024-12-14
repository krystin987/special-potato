import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ingest_event_success():
    # Prepare the request payload
    payload = {
        "event_type": "login_attempt",
        "data": {
            "user": "johndoe",
            "success": False,
            "ip_address": "192.168.1.10"
        }
    }

    # Send POST request
    response = client.post("/ingestion/ingest", json=payload)

    # Validate response
    assert response.status_code == 200
    assert response.json()["message"] == "Event ingested successfully"
    assert "event_time" in response.json()

def test_ingest_event_missing_field():
    # Prepare payload with missing 'data'
    payload = {
        "event_type": "login_attempt"
    }

    # Send POST request
    response = client.post("/ingestion/ingest", json=payload)

    # Validate response
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["loc"] == ["body", "data"]

def test_ingest_event_invalid_type():
    # Prepare payload with invalid 'event_type'
    payload = {
        "event_type": 12345,  # Invalid type (should be string)
        "data": {
            "user": "johndoe",
            "success": False,
            "ip_address": "192.168.1.10"
        }
    }

    # Send POST request
    response = client.post("/ingestion/ingest", json=payload)

    # Validate response
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["loc"] == ["body", "event_type"]
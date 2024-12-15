from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.future import engine
from sqlalchemy.orm import Session, sessionmaker

from app.main import app

client = TestClient(app)

def test_ingest_event_success():
    # Prepare the request payload
    payload = {
        "event_type": "login_attempt",
        "event_time": "2024-12-14T21:43:30Z",  # Add this field
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
    assert response.json()["event_time"] == payload["event_time"]  # Match event_time

def test_ingest_event_missing_field():
    # Prepare payload with missing 'data'
    payload = {
        "event_type": "login_attempt",
        "event_time": "2024-12-14T21:43:30Z"
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


def test_ingest_valid_event():
    payload = {
        "event_type": "login_attempt",
        "event_time": "2024-12-14T21:43:30Z",
        "data": {"user": "johndoe", "success": False},
    }
    response = client.post("/ingestion/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Event ingested successfully"

def test_ingest_invalid_event():
    payload = {
        "event_time": "2024-12-14T21:43:30Z",  # Missing event_type
        "data": {"user": "johndoe", "success": False},
    }
    response = client.post("/ingestion/ingest", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "event_type"]
    assert response.json()["detail"][0]["msg"] == "Field required"

def test_ingest_duplicate_event(monkeypatch):
    # Mock the engine's connect method to raise IntegrityError
    def mock_connect(*args, **kwargs):
        class MockConnection:
            def execute(self, *args, **kwargs):
                raise IntegrityError("duplicate key value violates unique constraint", None, None)
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return MockConnection()

    # Patch engine.connect to use the mocked connection
    monkeypatch.setattr("app.ingestion.ingestion_service.engine.connect", mock_connect)

    payload = {
        "event_type": "login_attempt",
        "event_time": "2024-12-14T21:43:30Z",
        "data": {"user": "johndoe", "success": False},
    }
    response = client.post("/ingestion/ingest", json=payload)
    assert response.status_code == 409
    assert "Duplicate event detected" in response.json()["detail"]
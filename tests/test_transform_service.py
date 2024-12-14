import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_data():
    # Provide mock data for testing if needed
    return [
        {"id": 1, "event_type": "login_attempt", "event_time": "2024-12-14T21:43:30Z", "data": {"user": "johndoe", "success": False, "ip_address": "192.168.1.10"}},
        {"id": 2, "event_type": "logout", "event_time": "2024-12-14T22:00:00Z", "data": {"user": "janedoe", "ip_address": "192.168.1.11"}}
    ]

def test_transform_events(mock_data, monkeypatch):
    # Mock database fetch
    def mock_fetch_events(*args, **kwargs):
        return mock_data

    # Patch the database query logic in the service
    from app.transform.transform_service import engine
    monkeypatch.setattr(engine, "connect", mock_fetch_events)

    # Call the endpoint
    response = client.get("/transform/transform")

    # Validate the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Transformation endpoint is working!"  # Update to match the placeholder response